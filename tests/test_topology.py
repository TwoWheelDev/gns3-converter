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
from gns3converter.topology import LegacyTopology


class TestTopology(unittest.TestCase):
    def setUp(self):
        conf = ConfigObj()
        conf['127.0.0.1:7200'] = {'3725': {'image': 'c3725.image',
                                           'ram': 128,
                                           'x': None,
                                           'y': None},
                                  'ROUTER R1': {'cnfg': 'configs/R1.cfg',
                                                'console': 2101,
                                                'aux': 2501,
                                                'model': None}}
        self.app = LegacyTopology([], conf)

    def add_hv_details(self):
        instance = '127.0.0.1:7200'
        item = '3725'

        self.app.add_conf_item(instance, item)

    def add_artwork_item(self):
        self.app.topology['conf']['GNS3-DATA'] = {
            'NOTE 1': {'text': 'SomeText', 'x': 20, 'y': 25,
                       'color': '#1a1a1a'},
            'SHAPE 1': {'type': 'ellipse', 'x': 20, 'y': 25, 'width': 500,
                        'height': 250, 'border_style': 2}}

        exp_res = {'SHAPE': {'1': {'type': 'ellipse',
                                   'x': 20, 'y': 25,
                                   'width': 500,
                                   'height': 250,
                                   'border_style': 2}},
                   'NOTE': {'1': {'text': 'SomeText',
                                  'x': 20, 'y': 25,
                                  'color': '#1a1a1a'}}
                   }

        self.app.add_artwork_item('GNS3-DATA', 'SHAPE 1')
        self.app.add_artwork_item('GNS3-DATA', 'NOTE 1')

        self.assertDictEqual(self.app.topology['artwork'], exp_res)

    def test_add_conf_item(self):
        instance = '127.0.0.1:7200'
        item = '3725'

        exp_res = [{'image': 'c3725.image', 'model': 'c3725', 'ram': 128}]

        self.app.add_conf_item(instance, item)
        self.assertListEqual(self.app.topology['conf'], exp_res)

    def test_add_physical_item_no_model(self):
        self.add_hv_details()

        instance = '127.0.0.1:7200'
        item = 'ROUTER R1'

        exp_res = {'R1': {'hv_id': 0,
                          'node_id': 1,
                          'type': 'Router',
                          'desc': 'Router',
                          'cnfg': 'configs/R1.cfg',
                          'console': 2101,
                          'aux': 2501,
                          'model': 'c3725'}}

        self.app.add_physical_item(instance, item)
        self.assertDictEqual(self.app.topology['devices'], exp_res)

    def test_add_physical_item_with_model(self):
        self.add_hv_details()

        instance = '127.0.0.1:7200'
        item = 'ROUTER R1'

        exp_res = {'R1': {'hv_id': 0,
                          'node_id': 1,
                          'type': 'Router',
                          'desc': 'Router',
                          'cnfg': 'configs/R1.cfg',
                          'console': 2101,
                          'aux': 2501,
                          'model': 'c7200'}}

        self.app.old_top['127.0.0.1:7200']['ROUTER R1']['model'] = '7200'

        self.app.add_physical_item(instance, item)
        self.assertDictEqual(self.app.topology['devices'], exp_res)

    def test_device_typename(self):
        exp_result = {'ROUTER R1': {'name': 'R1', 'type': 'Router'},
                      'QEMU Q1': {'name': 'Q1', 'type': 'QEMU'},
                      'VBOX V1': {'name': 'V1', 'type': 'VirtualBoxVM'},
                      'FRSW FR1': {'name': 'FR1', 'type': 'FrameRelaySwitch'},
                      'ETHSW SW1': {'name': 'SW1', 'type': 'EthernetSwitch'},
                      'Hub Hub1': {'name': 'Hub1', 'type': 'EthernetHub'},
                      'ATMSW SW1': {'name': 'SW1', 'type': 'ATMSwitch'},
                      'ATMBR BR1': {'name': 'BR1', 'type': 'ATMBR'},
                      'Cloud C1': {'name': 'C1', 'type': 'Cloud'}}

        for device in exp_result:
                (name, dev_type) = self.app.device_typename(device)
                self.assertEqual(exp_result[device]['name'], name)
                self.assertEqual(exp_result[device]['type'], dev_type['type'])

if __name__ == '__main__':
    unittest.main()