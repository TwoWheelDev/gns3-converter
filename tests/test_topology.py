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
from gns3converter.topology import LegacyTopology, JSONTopology


class TestLegacyTopology(unittest.TestCase):
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

    def test_add_artwork_item(self):
        self.app.old_top['GNS3-DATA'] = {
            'NOTE 1': {'text': 'SomeText', 'x': 20, 'y': 25,
                       'color': '#1a1a1a'},
            'NOTE 2': {'text': 'f0/0', 'x': 20, 'y': 25,
                       'color': '#1a1a1a', 'interface': 'f0/0'},
            'SHAPE 1': {'type': 'ellipse', 'x': 20, 'y': 25, 'width': 500,
                        'height': 250, 'border_style': 2}
        }

        exp_res = {'SHAPE': {'1': {'type': 'ellipse',
                                   'x': 20, 'y': 25,
                                   'color': '#ffffff',
                                   'transparency': 0,
                                   'width': 500,
                                   'height': 250,
                                   'border_style': 2}},
                   'PIXMAP': {},
                   'NOTE': {'1': {'text': 'SomeText',
                                  'x': 20, 'y': 25,
                                  'color': '#1a1a1a'}}
                   }

        self.app.add_artwork_item('GNS3-DATA', 'SHAPE 1')
        self.app.add_artwork_item('GNS3-DATA', 'NOTE 1')
        self.app.add_artwork_item('GNS3-DATA', 'NOTE 2')

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
                          'from': 'ROUTER',
                          'cnfg': 'configs/R1.cfg',
                          'console': 2101,
                          'aux': 2501,
                          'model': 'c3725',
                          'hx': 19.5, 'hy': -25}}

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
                          'from': 'ROUTER',
                          'cnfg': 'configs/R1.cfg',
                          'console': 2101,
                          'aux': 2501,
                          'model': 'c7200',
                          'hx': 19.5, 'hy': -25}}

        self.app.old_top['127.0.0.1:7200']['ROUTER R1']['model'] = '7200'

        self.app.add_physical_item(instance, item)
        self.assertDictEqual(self.app.topology['devices'], exp_res)

    def test_device_typename(self):
        exp_result = {'ROUTER R1': {'name': 'R1', 'type': 'Router'},
                      'QEMU Q1': {'name': 'Q1', 'type': 'QemuVM'},
                      'ASA ASA1': {'name': 'ASA1', 'type': 'QemuVM'},
                      'PIX PIX1': {'name': 'PIX1', 'type': 'QemuVM'},
                      'JUNOS JUNOS1': {'name': 'JUNOS1', 'type': 'QemuVM'},
                      'IDS IDS1': {'name': 'IDS1', 'type': 'QemuVM'},
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

    def test_vbox_id(self):
        self.assertEqual(self.app.vbox_id, 1)
        self.app.vbox_id = 5
        self.assertEqual(self.app.vbox_id, 5)

    def test_qemu_id(self):
        self.assertEqual(self.app.qemu_id, 1)
        self.app.qemu_id = 5
        self.assertEqual(self.app.qemu_id, 5)


class TestJSONTopology(unittest.TestCase):
    def setUp(self):
        self.app = JSONTopology()

    def test_nodes(self):
        self.assertListEqual(self.app.nodes, [])
        self.app.nodes = [{'node_id': 1}]
        self.assertListEqual(self.app.nodes, [{'node_id': 1}])

    def test_links(self):
        self.assertListEqual(self.app.links, [])
        self.app.links = [{'id': 1}]
        self.assertListEqual(self.app.links, [{'id': 1}])

    def test_notes(self):
        self.assertListEqual(self.app.notes, [])
        self.app.notes = [{'id': 1}]
        self.assertListEqual(self.app.notes, [{'id': 1}])

    def test_shapes(self):
        self.assertDictEqual(self.app.shapes,
                             {'ellipse': None, 'rectangle': None})
        self.app.shapes = {'ellipse': {'id': 1},
                           'rectangle': {'id': 2}}
        self.assertDictEqual(self.app.shapes, {'ellipse': {'id': 1},
                                               'rectangle': {'id': 2}})

    def test_images(self):
        self.assertListEqual(self.app.images, [])
        self.app.images = [{'id': 1}]
        self.assertListEqual(self.app.images, [{'id': 1}])

    def test_servers(self):
        exp_res = [{'host': '127.0.0.1', 'id': 1, 'local': True, 'port': 8000}]
        self.assertListEqual(self.app.servers, exp_res)
        self.app.servers = [{'host': '127.0.0.1', 'id': 2, 'local': True,
                            'port': 8001}]
        exp_res = [{'host': '127.0.0.1', 'id': 2, 'local': True,
                    'port': 8001}]
        self.assertListEqual(self.app.servers, exp_res)

    def test_name(self):
        self.assertIsNone(self.app.name)
        self.app.name = 'Super Topology'
        self.assertEqual(self.app.name, 'Super Topology')

    def test_get_topology(self):
        exp_res = {'name': None,
                   'resources_type': 'local',
                   'topology': {'servers': [{'host': '127.0.0.1', 'id': 1,
                                             'local': True, 'port': 8000}]},
                   'type': 'topology',
                   'version': '1.0'}

        result = self.app.get_topology()
        self.assertDictEqual(result, exp_res)

    def test_get_vboxes(self):
        # TODO
        pass

    def test_get_qemus(self):
        # TODO
        pass

if __name__ == '__main__':
    unittest.main()