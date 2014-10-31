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

    def test_get_topology(self):
        topo_file = self.app.topology
        exp_res = (os.path.abspath('./tests/topology.net'),
                   os.path.abspath('./topology.net'))

        self.assertIn(topo_file, exp_res)

    def test_read_topology(self):
        self.maxDiff = None
        topology = self.app.read_topology()
        self.assertIsInstance(topology, ConfigObj)
        self.assertDictEqual(tests.data.old_top, topology)

    def test_get_sections(self):
        topology = self.app.read_topology()
        sections = self.app.get_sections(topology)
        self.assertEqual(['127.0.0.1:7200', 'GNS3-DATA'], sections)

    def test_process_topology(self):
        topology = self.app.read_topology()
        (processed) = self.app.process_topology(topology)
        self.assertDictEqual(tests.data.devices, processed['devices'])
        self.assertListEqual(tests.data.conf, processed['conf'])
        self.assertDictEqual(tests.data.artwork, processed['artwork'])

    def test_generate_shapes(self):
        shapes = {'1': {'type': 'ellipse', 'x': 20, 'y': 25, 'width': 500,
                        'height': 250, 'border_style': 2},
                  '2': {'type': 'rectangle', 'x': 40, 'y': 250, 'width': 250,
                        'height': 275, 'border_style': 2}}
        exp_res = {'ellipse': [{'x': 20, 'y': 25, 'width': 500,
                                'height': 250, 'border_style': 2}],
                   'rectangle': [{'x': 40, 'y': 250, 'width': 250,
                                  'height': 275, 'border_style': 2}]}
        res = self.app.generate_shapes(shapes)
        self.assertDictEqual(res, exp_res)

    def test_generate_notes(self):
        notes = {'1': {'text': 'SomeText', 'x': 20, 'y': 25,
                       'color': '#1a1a1a'}}
        exp_res = [{'text': 'SomeText', 'x': 20, 'y': 25, 'color': '#1a1a1a'}]

        res = self.app.generate_notes(notes)
        self.assertListEqual(res, exp_res)

if __name__ == '__main__':
    unittest.main()