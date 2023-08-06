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

import json

from testtools import TestCase

from pkgme_service_client.utils import parse_json


class TestParseJSON(TestCase):

    def test_good(self):
        good = '{"a": 1, "b": "good"}'
        self.assertEqual(json.loads(good), parse_json(good))

    def test_None(self):
        bad = None
        e = self.assertRaises(TypeError, parse_json, bad)
        self.assertEqual('expected string or buffer, got None', str(e))

    def test_bad(self):
        bad = 'not json'
        e = self.assertRaises(ValueError, parse_json, bad)
        self.assertIn(bad, str(e))
