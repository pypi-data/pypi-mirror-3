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

from datetime import timedelta
from StringIO import StringIO
import sys

from testtools import (
    PlaceHolder,
    TestCase,
    )
from testtools.content import (
    text_content,
    TracebackContent,
    )
from twisted.internet.error import TimeoutError

from txpkgme.reports import (
    calculate_success_ratio,
    calculate_total_time,
    gather_errors,
    map_error,
    format_success_failure,
    format_total_time,
    NO_BACKEND,
    parse_subunit,
    TIMEOUT,
    UNKNOWN,
    )
from txpkgme.scoreboard import json_content


class TestFormatSuccessFailure(TestCase):

    def test_basic(self):
        output = format_success_failure(1, 2)
        self.assertEqual(
            '\n'.join(
                ["Successful: 1",
                 "Failed: 2",
                 "Total: 3",
                 "",
                 "Percentage: 33.33%",
                 "",
                 ]), output)

    def test_zero(self):
        output = format_success_failure(0, 0)
        self.assertEqual("No results found", output)


class TestParseSubunit(TestCase):

    def test_empty(self):
        self.assertEqual([], parse_subunit(StringIO()))

    def test_simple_success(self):
        subunit_data = """
time: 2012-01-01 00:00:00.000000Z
test: foo:32
time: 2012-01-01 00:00:01.000000Z
success: foo:32
time: 2012-01-02 00:00:00.000000Z
"""
        stream = StringIO(subunit_data)
        self.assertEqual(
            [{'test_id': 'foo:32', 'status': 'success',
              'details': {}, 'duration': timedelta(seconds=1)}],
            parse_subunit(stream))


class TestCalculateSuccessRatio(TestCase):

    def test_empty(self):
        self.assertEqual((0, 0), calculate_success_ratio([]))

    def test_single_success(self):
        data = [{'status': 'success'}]
        success, failure = calculate_success_ratio(data)
        self.assertEqual((1, 0), (success, failure))

    def test_single_failure(self):
        data = [{'status': 'failure'}]
        success, failure = calculate_success_ratio(data)
        self.assertEqual((0, 1), (success, failure))


class TestCalculateTotalTime(TestCase):

    def test_empty(self):
        self.assertEqual(timedelta(0), calculate_total_time([]))

    def test_some_results(self):
        data = [{'duration': timedelta(1)}, {'duration': timedelta(2)}]
        self.assertEqual(timedelta(3), calculate_total_time(data))

    def test_missing_duration(self):
        data = [{'duration': timedelta(1)}, {}]
        self.assertEqual(timedelta(1), calculate_total_time(data))


class TestFormatTotalTime(TestCase):

    def test_basic(self):
        duration = timedelta(seconds=5.2)
        self.assertEqual(
            "Total time taken: 0:00:05.200000s\n",
            format_total_time(duration))


class TestMapError(TestCase):

    def test_timeout(self):
        try:
            raise TimeoutError("User timeout caused connection failure.")
        except TimeoutError:
            tb = TracebackContent(sys.exc_info(), PlaceHolder(''))
        timeout_details = {'traceback': tb}
        self.assertEqual(TIMEOUT, map_error(timeout_details))

    def test_no_backend(self):
        content = text_content(
            'No eligible backends for /tmp/tmpH94djh/working. Tried '
            'binary, pdf. The following backends were disallowed by '
            'policy: cmake, dummy, vala, python.')
        details = {'traceback': content}
        self.assertEqual(NO_BACKEND, map_error(details))

    def test_unrecognized_from_server(self):
        content = text_content('IOError: Disk space full')
        details = {'error': content}
        self.assertEqual(content.as_text(), map_error(details))

    def test_non_text_error(self):
        details = {'error': json_content({})}
        self.assertEqual(UNKNOWN, map_error(details))

    def test_no_error(self):
        self.assertEqual(None, map_error({}))
        self.assertEqual(None, map_error({'other-data': {}}))

    def test_backend_script_failure(self):
        big_script_failure = """\
/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/backends/binary/all_info failed with returncode 1. Output:
 | Traceback (most recent call last):
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/backends/binary/all_info", line 13, in <module>
 |     main()
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/backends/binary/all_info", line 9, in main
 |     BinaryBackend().dump_json()
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/metadata.py", line 465, in dump_json
 |     info = self.get_info(self.get_metadata())
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/metadata.py", line 453, in get_info
 |     info[element] = self._calculate_info_element(element, metadata)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/metadata.py", line 232, in _calculate_info_element
 |     return method(metadata, *args, **kwargs)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 348, in get_build_depends
 |     return ', '.join(guess_dependencies(self.path))
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 305, in guess_dependencies
 |     libraries = get_shared_library_dependencies(binaries)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 210, in get_shared_library_dependencies
 |     libraries = needed_libraries_from_objdump(paths)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 201, in needed_libraries_from_objdump
 |     "Can not handle '%s'" % architecture)
 | devportalbinary.binary.UnsupportedArchitecture: Can not handle 'i386:x86-64'
"""
        details = {'traceback': text_content(big_script_failure)}
        mapped = map_error(details)
        self.assertEqual(
            "devportalbinary.binary.UnsupportedArchitecture: Can not handle 'i386:x86-64'",
            mapped)

    def test_unrecognized_local(self):
        try:
            1/0
        except ZeroDivisionError:
            tb = TracebackContent(sys.exc_info(), PlaceHolder(''))
        details = {'traceback': tb}
        self.assertEqual(
            tb.as_text().splitlines()[-1].strip(), map_error(details))


class TestGatherErrors(TestCase):

    def test_just_successes(self):
        self.assertEqual({}, gather_errors([{}, {}, {}]))

    def test_timeout(self):
        try:
            raise TimeoutError("User timeout caused connection failure.")
        except TimeoutError:
            tb = TracebackContent(sys.exc_info(), PlaceHolder(''))
        timeout_details = {'traceback': tb}
        test = {'details': timeout_details}
        self.assertEqual({TIMEOUT: 1}, gather_errors([test]))

    def test_unrecognized(self):
        try:
            1/0
        except ZeroDivisionError:
            tb = TracebackContent(sys.exc_info(), PlaceHolder(''))
        test = {'details': {'traceback': tb}}
        self.assertEqual(
            {tb.as_text().splitlines()[-1].strip(): 1}, gather_errors([test]))
