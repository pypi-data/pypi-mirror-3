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


def parse_json(json_data):
    """Return a Python data structure corresponding to ``json_data``.

    Use this rather than ``json.loads`` directly to get a richer error message
    when JSON data cannot be decoded.

    :param json_data: A string containing JSON data.
    :raises ValueError: If the JSON data could not be parsed.
    :return: A Python data structure.
    """
    try:
        return json.loads(json_data)
    except ValueError:
        raise ValueError('No JSON object could be decoded: %r' % (json_data,))
    except TypeError, e:
        raise TypeError('%s, got %r' % (e, json_data))

