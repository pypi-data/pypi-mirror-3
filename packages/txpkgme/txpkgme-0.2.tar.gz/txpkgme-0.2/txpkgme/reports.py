#!/usr/bin/env python
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
from datetime import timedelta
from StringIO import StringIO
import sys

from subunit.filters import run_tests_from_stream
from testtools import TestByTestResult


def make_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'subunit', type=argparse.FileType('rb'), nargs='?',
        default='-', help='subunit data to report on')
    return parser


SUCCESSFUL_STATUSES = ('success',)


def calculate_success_ratio(parsed_results):
    total = len(parsed_results)
    successes = len(
        [None for result in parsed_results
         if result['status'] in SUCCESSFUL_STATUSES])
    return successes, total - successes


def calculate_total_time(parsed_results):
    no_time = timedelta(0)
    return sum(
        [result.get('duration', no_time) for result in parsed_results],
        no_time)


def format_success_failure(success, failure):
    total = success + failure
    if not total:
        return "No results found"
    percentage = 100 * float(success) / float(total)
    return '\n'.join(
        ["Successful: %s" % (success,),
         "Failed: %s" % (failure,),
         "Total: %s" % (total,),
         "",
         "Percentage: %0.2f%%" % (percentage,),
         "",
         ])


def format_total_time(duration):
    return "Total time taken: %ss\n" % (duration,)


NO_BACKEND = u'NO-BACKEND'
TIMEOUT = u'TIMEOUT'
UNKNOWN = u'unknown'


def map_error(details):
    if not details:
        return
    traceback = details.get('traceback', None)
    if traceback:
        traceback = traceback.as_text()
        if 'TimeoutError' in traceback:
            return TIMEOUT
        if traceback.startswith('No eligible backends'):
            return NO_BACKEND
        return traceback.splitlines()[-1].strip().lstrip('|').strip()
    error = details.get('error', None)
    if error:
        try:
            return error.as_text()
        except ValueError:
            return UNKNOWN
    return


def gather_errors(parsed_results):
    counts = {}
    for result in parsed_results:
        error = map_error(result.get('details', None))
        if not error:
            continue
        if error in counts:
            counts[error] += 1
        else:
            counts[error] = 1
    return counts


def parse_subunit(subunit_stream):
    output = []
    def on_test(test, status, start_time, stop_time, tags, details):
        output.append(
            {'test_id': test.id(),
             'status': status,
             'details': details,
             'duration': stop_time - start_time,
             })
    result = TestByTestResult(on_test)
    run_tests_from_stream(
        subunit_stream, result, passthrough_stream=StringIO())
    return output


def report_on_subunit(input_stream, output_stream):
    """Report interesting information from 'input_stream' to 'output_stream'.
    """
    w = output_stream.write
    results = parse_subunit(input_stream)
    successes, failures = calculate_success_ratio(results)
    w('Summary\n')
    w('-------\n')
    w(format_success_failure(successes, failures))
    w(format_total_time(calculate_total_time(results)))
    w('\n')
    w('Errors\n')
    w('------\n')
    errors = sorted(gather_errors(results).items())
    for error, count in errors:
        w('%s: %s\n' % (error.strip(), count))


def main():
    parser = make_options()
    args = parser.parse_args()
    report_on_subunit(args.subunit, sys.stdout)
    return 0
