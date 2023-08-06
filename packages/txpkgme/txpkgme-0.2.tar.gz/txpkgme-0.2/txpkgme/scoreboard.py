# Copyright (C) 2012  Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import json
import sys

from httplib2 import Http
from oauth.oauth import (
    OAuthRequest,
    OAuthConsumer,
    OAuthToken,
    OAuthSignatureMethod_PLAINTEXT,
    )
from subunit import TestProtocolClient
from subunit.test_results import AutoTimingTestResultDecorator
from testtools import PlaceHolder
from testtools.content import (
    Content,
    text_content,
    )
from testtools.content_type import ContentType
from twisted.internet import defer
from twisted.internet import reactor as mod_reactor

from .commands import (
    get_service_url,
    UserError,
    )
from .harness import (
    PkgmeServiceError,
    WebServer,
    wrap_pkgme_service_error,
    )
from .utils import parse_json


def json_content(data):
    JSON_TYPE = ContentType('application', 'json', {'charset': 'utf8'})
    return  Content(JSON_TYPE, lambda: [json.dumps(data)])


MYAPPS_SERVERS = {
    'vps': 'https://sca.razorgirl.info/dev/api/app-metadata/',
    'staging': 'https://developer.staging.ubuntu.com/dev/api/app-metadata/',
    'production': 'https://myapps.developer.ubuntu.com/dev/api/app-metadata/',
    }


class SubunitReporter(object):

    def __init__(self, stream):
        client = TestProtocolClient(stream)
        self._client = AutoTimingTestResultDecorator(client)
        client.startTestRun()

    def _to_test(self, application):
        name = application['name'].replace(' ', '-').encode('utf8')
        return PlaceHolder('%s:%s' % (name, application['myapps_id']))

    def _simple_error(self, error):
        return {'traceback': text_content(error)}

    def building_package(self, application):
        self._client.startTest(self._to_test(application))

    def pkgme_failure(self, application, error):
        test = self._to_test(application)
        details = {
            'traceback': text_content(error.traceback),
            'extra_data': json_content(error.body),
            }
        if error.error:
            details['error'] = json_content(error.error)
        self._client.addFailure(test, details=details)
        self._client.stopTest(test)

    def pkgme_success(self, application, data):
        test = self._to_test(application)
        json_data = json_content(data)
        self._client.addSuccess(test, details={'pkgme': json_data})
        self._client.stopTest(test)

    def unexpected_error(self, application, failure):
        test = self._to_test(application)
        self._client.addFailure(
            test, details=self._simple_error(failure.getTraceback()))
        self._client.stopTest(test)


def run_many(functions, num_parallel=1):
    semaphore = defer.DeferredSemaphore(num_parallel)
    deferreds = [semaphore.run(f, *a, **kw) for (f, a, kw) in functions]
    return defer.gatherResults(deferreds)


def submit_application(pkgme_root, application, reporter, hostname, timeout):
    reporter.building_package(application)
    web_server = WebServer(hostname=hostname, timeout=timeout)
    d = web_server.run()
    def web_server_up((root, url, metadata_urls)):
        application.update(metadata_urls)
        return web_server.send_api_request(application, pkgme_root)
    def got_response((method, body)):
        reporter.pkgme_success(application, body)
    def got_failure(failure):
        failure.trap(PkgmeServiceError)
        reporter.pkgme_failure(application, failure.value)
    def unexpected_error(f):
        reporter.unexpected_error(application, f)
    d.addCallback(web_server_up)
    d.addCallbacks(got_response, wrap_pkgme_service_error)
    d.addErrback(got_failure)
    d.addErrback(unexpected_error)
    return d


def get_applications(source_file=None, devportal=None, credentials_file=None,
                     max_apps=None, handle_internal='keep'):
    if source_file:
        content = source_file.read()
    elif devportal:
        if not credentials_file:
            raise UserError(
                "Must provide credentials in order to get application list "
                "from a devportal.")
        credentials = parse_json(credentials_file.read())
        devportal_url = MYAPPS_SERVERS[devportal]
        content = myapps_GET(devportal_url, credentials)
    else:
        raise UserError(
            "Cannot get application list.  Please specify either a source "
            "file or a devportal to get the list from.")
    apps = parse_json(content)
    if max_apps:
        apps = apps[:max_apps]
    if devportal == 'staging':
        apps = map(_clean_up_staging_data, apps)
    if handle_internal == 'convert':
        apps = map(_convert_internal_data, apps)
    elif handle_internal == 'hide':
        apps = [a for a in apps if 'internal_packages' not in a['package_url']]
    return apps


def _clean_up_staging_data(application, cutoff=581):
    application = dict(application)
    myapps_id = application.get('myapps_id', None)
    if myapps_id is None or myapps_id > cutoff:
        return application
    application['package_url'] = application['package_url'].replace(
        'developer.staging.ubuntu.com',
        'myapps.developer.ubuntu.com')
    icons = application.get('icons', {})
    for resolution in icons:
        icons[resolution] = icons[resolution].replace(
            'sc.staging.ubuntu.com',
            'myapps.developer.ubuntu.com')
    return application


def _convert_internal_data(application):
    application = dict(application)
    application['package_url'] = application['package_url'].replace(
        'internal_packages', 'site_media/packages')
    return application


def make_options():
    parser = argparse.ArgumentParser("Resubmit all applications to pkgme-service")
    parser.add_argument("-U", "--url", action='store', type=str, dest="url")
    parser.add_argument("-H", "--host", action='store', type=str, dest="host")
    parser.add_argument("--public-host-name", action='store', type=str,
                        dest='hostname', default='localhost')
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")
    parser.add_argument(
        "--internal-urls", dest="internal_urls",
        choices=("convert", "hide", "keep"), default="keep")
    json_source = parser.add_mutually_exclusive_group(required=True)
    json_source.add_argument(
        "--devportal", choices=MYAPPS_SERVERS, default="production")
    json_source.add_argument("--from-file", type=argparse.FileType('r'))
    parser.add_argument("--credentials", type=argparse.FileType('r'))
    parser.add_argument(
        "--timeout", action='store', type=int, dest='timeout', default=30,
        help=('If packaging an app takes longer than this, abort it.'))
    parser.add_argument(
        "-n", "--max-apps", action='store', type=int, dest='max_apps',
        default=0)
    parser.add_argument("--dump-json", dest='dump_json', action='store_true')
    return parser


def disaster(error):
    sys.stderr.write("UNEXPECTED ERROR\n")
    sys.stderr.write(error.getTraceback())
    sys.stderr.write('\n')


def run(applications, pkgme_url, reporter, hostname, timeout):
    d = run_many(
        [(submit_application,
          (pkgme_url, app, reporter, hostname, timeout), {})
         for app in applications],
        num_parallel=1)
    d.addErrback(disaster)
    d.addBoth(lambda x: mod_reactor.stop())
    return d


def oauth_sign_request(url, creds, http_method='GET', realm='pkgme-service'):
    """Sign a request with OAuth credentials."""
    consumer = OAuthConsumer(creds['consumer_key'], creds['consumer_secret'])
    token = OAuthToken(creds['token'], creds['token_secret'])
    oauth_request = OAuthRequest.from_consumer_and_token(
        consumer, token, http_url=url, http_method=http_method)
    oauth_request.sign_request(OAuthSignatureMethod_PLAINTEXT(),
        consumer, token)
    return oauth_request.to_header(realm)


def myapps_GET(url, creds):
    """Put ``json_body`` to MyApps at ``url``."""
    GOOD_RESPONSES = (200,)

    headers = oauth_sign_request(url, creds, 'GET')
    headers['Content-type'] = 'application/json'
    headers['Accept'] = 'application/json'
    getter = Http(disable_ssl_certificate_validation=True)
    method = 'GET'
    response, content = getter.request(url, method=method, headers=headers)
    if response.status not in GOOD_RESPONSES:
        raise RuntimeError(url, method, response.status, content)
    return content


def main():
    parser = make_options()
    args = parser.parse_args()
    try:
        applications = get_applications(
            args.from_file, args.devportal, args.credentials,
            args.max_apps, args.internal_urls)
        if args.dump_json:
            json.dump(applications, sys.stdout, sort_keys=True, indent=2)
            return
        pkgme_url = get_service_url(None, args.host, args.url)
    except UserError, e:
        sys.stderr.write('ERROR: ')
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
        return 3
    reporter = SubunitReporter(sys.stdout)
    if args.dry_run:
        for app in applications:
            reporter.building_package(app)
            reporter.pkgme_success(app, {})
    else:
        mod_reactor.callWhenRunning(
            run,
            applications, pkgme_url, reporter, args.hostname, args.timeout)
        mod_reactor.run()


if __name__ == '__main__':
    main()
