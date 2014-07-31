# Copyright (C) 2014 Daniel Lintott.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import unittest
from configobj import ConfigObj
import os.path
from gns3converter.converter import Converter
import tests.data


class TestConverter(unittest.TestCase):
    def setUp(self):
        if os.path.isfile(os.path.abspath('./tests/topology.net')):
            self._topology = os.path.abspath('./tests/topology.net')
        else:
            self._topology = os.path.abspath('./topology.net')
        self.app = Converter(self._topology)

    def test_read_topology(self):
        topology = self.app.read_topology()
        self.assertIsInstance(topology, ConfigObj)
        self.assertEqual(tests.data.old_top, topology)

    def test_get_instances(self):
        topology = self.app.read_topology()
        sections = self.app.get_instances(topology)
        self.assertEqual(['127.0.0.1:7200'], sections)

    def test_process_topology(self):
        topology = self.app.read_topology()
        sections = self.app.get_instances(topology)
        sections.append('GNS3-DATA')
        (devices, conf) = self.app.process_topology(sections, topology)
        self.assertDictEqual(tests.data.devices, devices)
        self.assertDictEqual(tests.data.conf, conf)

if __name__ == '__main__':
    unittest.main()