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

    def test_generate_nodes(self):
        topology = {}
        topology['conf'] = [
            {'sparsemem': True,
             'ghostios': True,
             'idlepc': '0x60bec828',
             'ram': 128,
             'model': 'c3725',
             'image': 'c3725-adventerprisek9-mz.124-15.T5.image'
            }
        ]
        topology['devices'] = {
            'GooglISP': {
                'model': 'c7200',
                'aux': 2512,
                'hx': 19.5,
                'z': 1.0,
                'type': 'Router',
                'node_id': 11,
                'p1/0': 'VerISPon p1/0',
                'hv_id': 3,
                'x': -261.643648086,
                'cnfg': 'configs\\GooglISP.cfg',
                'f0/0': 'SW1 f0/0',
                'y': -419.773080371,
                'console': 2012,
                'from': 'ROUTER',
                'hy': -25.0,
                'slot0': 'C7200-IO-FE',
                'desc': 'Router',
                'slot1': 'PA-POS-OC3'
            }
        }

        config = self.app.generate_nodes(topology)
        self.assertEqual(self.app.datas, [
            {'new': 'c7200_i11_rom', 'old': 'working/c7200_GooglISP_rom'},
            {'new': 'c7200_i11_nvram', 'old': 'working/c7200_GooglISP_nvram'},
            {'new': 'c7200_i11_bootflash', 'old': 'working/c7200_GooglISP_bootflash'},
            {'new': 'c7200_i11_disk0', 'old': 'working/c7200_GooglISP_disk0'}
        ])

if __name__ == '__main__':
    unittest.main()
