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
from gns3converter.node import Node
from gns3converter.converterror import ConvertError

class TestNode(unittest.TestCase):
    def setUp(self):
        hv_input = {'image': '/home/test/GNS3/Images/c3725.image',
                    'idlepc': '0x61616161',
                    'ram': '256',
                    'npe': 'npe-400',
                    'chassis': '3640',}

        self.app = Node(hv_input, 1)

    def test_add_wic(self):
        exp_res = {'wic0': 'WIC-1T'}

        self.app.add_wic('wic0/0', 'WIC-1T')
        self.assertDictEqual(exp_res, self.app.node['properties'])

    def test_add_wic_ports_wic1t(self):
        exp_res = [{'name': 'Serial0/0',
                    'id': 1,
                    'port_number': 16,
                    'slot_number': 0}]

        self.app.node['properties']['wic0'] = 'WIC-1T'

        self.app.add_wic_ports('wic0')
        self.assertListEqual(exp_res, self.app.node['ports'])
        self.assertEqual(self.app.port_id, 2)

    def test_add_wic_ports_wic2t(self):
        exp_res = [{'name': 'Serial0/0',
                    'id': 1,
                    'port_number': 16,
                    'slot_number': 0},
                   {'name': 'Serial0/1',
                    'id': 2,
                    'port_number': 17,
                    'slot_number': 0}]

        self.app.node['properties']['wic0'] = 'WIC-2T'

        self.app.add_wic_ports('wic0')
        self.assertListEqual(exp_res, self.app.node['ports'])
        self.assertEqual(self.app.port_id, 3)

    def test_add_wic_ports_wic2t_and_wic1t(self):
        exp_res = [{'name': 'Serial0/0',
                    'id': 1,
                    'port_number': 16,
                    'slot_number': 0},
                   {'name': 'Serial0/1',
                    'id': 2,
                    'port_number': 17,
                    'slot_number': 0},
                   {'name': 'Serial0/2',
                    'id': 3,
                    'port_number': 32,
                    'slot_number': 0}]

        self.app.node['properties']['wic0'] = 'WIC-2T'
        self.app.node['properties']['wic1'] = 'WIC-1T'

        self.app.add_wic_ports('wic0')
        self.app.add_wic_ports('wic1')
        self.assertListEqual(exp_res, self.app.node['ports'])
        self.assertEqual(self.app.port_id, 4)

    def test_add_info_from_hv(self):
        exp_res_node_prop = {'image': 'c3725.image',
                             'idlepc': '0x61616161',
                             'ram': '256',
                             'chassis': '3640'}
        exp_res_device_info = {'model': 'c3600',
                               'chassis': '3640',
                               'npe': 'npe-400'}

        self.app.device_info['model'] = 'c3600'

        self.app.add_info_from_hv()
        self.assertDictEqual(exp_res_node_prop, self.app.node['properties'])
        self.assertDictEqual(exp_res_device_info, self.app.device_info)

    def test_calc_mb_ports_c3725(self):
        exp_res = [{'name': 'FastEthernet0/0', 'id': 1, 'port_number': 0,
                    'slot_number': 0},
                   {'name': 'FastEthernet0/1', 'id': 2, 'port_number': 1,
                    'slot_number': 0}]

        self.app.device_info['model'] = 'c3725'

        self.app.calc_mb_ports()
        self.assertDictEqual(self.app.node['ports'][0], exp_res[0])
        self.assertDictEqual(self.app.node['ports'][1], exp_res[1])
        self.assertEqual(self.app.port_id, 3)

    def test_calc_mb_ports_c2600(self):
        exp_res = [{'name': 'Ethernet0/0', 'id': 1, 'port_number': 0,
                    'slot_number': 0}]

        self.app.device_info['model'] = 'c2600'
        self.app.device_info['chassis'] = '2610'

        self.app.calc_mb_ports()
        self.assertDictEqual(self.app.node['ports'][0], exp_res[0])
        self.assertEqual(self.app.port_id, 2)

    def test_calc_cloud_connection_4(self):
        exp_result = {'id': 1,
                      'name': 'nio_gen_eth:eth0',
                      'stub': True}
        self.app.connections = 'SW1:1:nio_gen_eth:eth0'
        self.app.calc_cloud_connection()
        #Check NIO String
        self.assertIsInstance(self.app.node['properties']['nios'], list)
        self.assertIsInstance(self.app.node['properties']['nios'][0], str)
        self.assertEqual(self.app.node['properties']['nios'][0],
                         'nio_gen_eth:eth0')
        #Check Port dictionary
        self.assertIsInstance(self.app.node['ports'][0], dict)
        self.assertDictEqual(self.app.node['ports'][0], exp_result)
        self.assertEqual(self.app.port_id, 2)

    def test_calc_cloud_connection_5(self):
        self.app.connections = 'SW1:1:nio_udp:30000:127.0.0.1'
        self.app.calc_cloud_connection()

        self.assertRaises(RuntimeError)

    def test_calc_cloud_connection_6(self):
        exp_result = {'id': 1,
                      'name': 'nio_udp:30000:127.0.0.1:20000',
                      'stub': True}
        self.app.connections = 'SW1:1:nio_udp:30000:127.0.0.1:20000'
        self.app.calc_cloud_connection()
        #Check NIO String
        self.assertIsInstance(self.app.node['properties']['nios'], list)
        self.assertIsInstance(self.app.node['properties']['nios'][0], str)
        self.assertEqual(self.app.node['properties']['nios'][0],
                         'nio_udp:30000:127.0.0.1:20000')
        #Check Port dictionary
        self.assertIsInstance(self.app.node['ports'][0], dict)
        self.assertDictEqual(self.app.node['ports'][0], exp_result)
        self.assertEqual(self.app.port_id, 2)

    def test_calc_cloud_connection_none(self):
        self.app.connections = None
        ret = self.app.calc_cloud_connection()
        self.assertIsNone(ret)

    def test_calc_ethsw_port_device(self):
        self.app.node['id'] = 1
        self.app.node['properties']['name'] = 'SW1'
        exp_port = {'id': 1, 'name': '1', 'port_number': 1,
                    'type': 'access', 'vlan': 1}
        exp_link = {'source_port_id': 1,
                    'source_node_id': 1,
                    'source_port_name': '1',
                    'dest_dev': 'SW2',
                    'source_dev': 'SW1',
                    'dest_port': '1'}

        self.app.calc_ethsw_port(1, 'access 1 SW2 1')
        self.assertIsInstance(self.app.node['ports'][0], dict)
        self.assertIsInstance(self.app.links[0], dict)

        self.assertDictEqual(self.app.node['ports'][0], exp_port)
        self.assertDictEqual(self.app.links[0], exp_link)

    def test_calc_ethsw_port_nio(self):
        self.app.node['id'] = 1
        self.app.node['properties']['name'] = 'SW1'
        exp_port = {'id': 1, 'name': '1', 'port_number': 1,
                    'type': 'access', 'vlan': 1}
        exp_link = {'source_port_id': 1,
                    'source_node_id': 1,
                    'source_port_name': '1',
                    'dest_dev': 'NIO',
                    'source_dev': 'SW1',
                    'dest_port': 'nio_gen_eth:eth0'}

        self.app.calc_ethsw_port(1, 'access 1 nio_gen_eth:eth0')
        self.assertIsInstance(self.app.node['ports'][0], dict)
        self.assertIsInstance(self.app.links[0], dict)

        self.assertDictEqual(self.app.node['ports'][0], exp_port)
        self.assertDictEqual(self.app.links[0], exp_link)

    def test_calc_link(self):
        self.app.node['properties']['name'] = 'R1'
        exp_res = {'source_node_id': 1,
                   'source_port_id': 2,
                   'source_port_name': 'FastEthernet0/0',
                   'source_dev': 'R1',
                   'dest_dev': 'SiteA',
                   'dest_port': 'f0/0'}

        self.app.calc_link(1, 2, 'FastEthernet0/0',
                           {'device': 'SiteA', 'port': 'f0/0'})
        self.assertIsInstance(self.app.links[0], dict)
        self.assertDictEqual(self.app.links[0], exp_res)

    def test_add_slot_ports(self):
        self.app.node['properties']['slot1'] = 'NM-4T'
        exp_res = [{'name': 'Serial1/0', 'id': 1, 'port_number': 0,
                    'slot_number': 1},
                   {'name': 'Serial1/1', 'id': 2, 'port_number': 1,
                    'slot_number': 1},
                   {'name': 'Serial1/2', 'id': 3, 'port_number': 2,
                    'slot_number': 1},
                   {'name': 'Serial1/3', 'id': 4, 'port_number': 3,
                    'slot_number': 1}]

        self.app.add_slot_ports('slot1')
        self.assertListEqual(self.app.node['ports'], exp_res)
        self.assertDictEqual(self.app.node['ports'][0], exp_res[0])
        self.assertDictEqual(self.app.node['ports'][1], exp_res[1])
        self.assertEqual(self.app.port_id, 5)

    def test_add_slot_ports_c7200(self):
        self.app.device_info['model'] = 'c7200'
        self.app.node['properties']['slot0'] = 'C7200-IO-2FE'
        exp_res = [{'name': 'FastEthernet0/0', 'id': 1, 'port_number': 0,
                    'slot_number': 0},
                   {'name': 'FastEthernet0/1', 'id': 2, 'port_number': 1,
                    'slot_number': 0}]

        self.app.add_slot_ports('slot0')
        self.assertListEqual(self.app.node['ports'], exp_res)
        self.assertDictEqual(self.app.node['ports'][0], exp_res[0])
        self.assertDictEqual(self.app.node['ports'][1], exp_res[1])
        self.assertEqual(self.app.port_id, 3)

    def test_set_description_router(self):
        self.app.device_info['type'] = 'Router'
        self.app.device_info['model'] = 'c3725'

        self.app.set_description()
        self.assertEqual(self.app.node['description'], 'Router c3725')

    def test_set_description_cloud(self):
        self.app.device_info['type'] = 'Cloud'
        self.app.device_info['desc'] = 'Cloud'

        self.app.set_description()
        self.assertEqual(self.app.node['description'], 'Cloud')

    def test_set_type_router(self):
        self.app.device_info['type'] = 'Router'
        self.app.device_info['model'] = 'c3725'

        self.app.set_type()
        self.assertEqual(self.app.node['type'], 'C3725')

    def test_set_type_cloud(self):
        self.app.device_info['type'] = 'Cloud'

        self.app.set_type()
        self.assertEqual(self.app.node['type'], 'Cloud')

    def test_get_nb_added_ports(self):
        self.app.node['properties']['slot1'] = 'NM-4T'
        self.app.add_slot_ports('slot1')

        nb_added = self.app.get_nb_added_ports(0)
        self.assertIsInstance(nb_added, int)
        self.assertEqual(nb_added, 5)

    def test_set_symbol_access_point(self):
        self.app.set_symbol('access_point')

        self.assertEqual(self.app.node['default_symbol'],
                         ':/symbols/access_point.normal.svg')
        self.assertEqual(self.app.node['hover_symbol'],
                         ':/symbols/access_point.selected.svg')

    def test_set_symbol_etherswitch_router(self):
        self.app.set_symbol('EtherSwitch router')

        self.assertEqual(self.app.node['default_symbol'],
                         ':/symbols/multilayer_switch.normal.svg')
        self.assertEqual(self.app.node['hover_symbol'],
                         ':/symbols/multilayer_switch.selected.svg')

    def test_set_symbol_host(self):
        self.app.set_symbol('Host')

        self.assertEqual(self.app.node['default_symbol'],
                         ':/symbols/computer.normal.svg')
        self.assertEqual(self.app.node['hover_symbol'],
                         ':/symbols/computer.selected.svg')

    def test_calc_device_links(self):
        self.app.interfaces.append({'to': 'R2 f0/0',
                                    'from': 'f0/0'})
        self.app.node['id'] = 1
        self.app.node['properties']['name'] = 'R1'
        self.app.device_info['model'] = 'c3725'
        self.app.calc_mb_ports()

        exp_res = {'source_node_id': 1,
                   'source_port_id': 1,
                   'source_port_name': 'FastEthernet0/0',
                   'source_dev': 'R1',
                   'dest_dev': 'R2',
                   'dest_port': 'f0/0'}

        self.app.calc_device_links()
        self.assertDictEqual(self.app.links[0], exp_res)

    def test_calc_device_links_nio(self):
        self.app.interfaces.append({'to': 'nio_gen_eth:eth0',
                                    'from': 'f0/0'})
        self.app.node['id'] = 1
        self.app.node['properties']['name'] = 'R1'
        self.app.device_info['model'] = 'c3725'
        self.app.calc_mb_ports()

        exp_res = {'source_node_id': 1,
                   'source_port_id': 1,
                   'source_port_name': 'FastEthernet0/0',
                   'source_dev': 'R1',
                   'dest_dev': 'NIO',
                   'dest_port': 'nio_gen_eth:eth0'}

        self.app.calc_device_links()
        self.assertDictEqual(self.app.links[0], exp_res)

    def test_add_mapping(self):
        self.app.add_mapping(('1:122', '2:221'))
        self.assertListEqual(self.app.mappings, [{'source': '1:122',
                                                  'dest': '2:221'}])

    def test_process_mappings(self):
        self.app.add_mapping(('1:122', '2:221'))
        self.app.add_mapping(('2:221', '1:122'))
        self.app.add_mapping(('3:321', '1:123'))

        self.app.process_mappings()

        exp_res = {'1:122': '2:221', '3:321': '1:123'}
        self.assertDictEqual(self.app.node['properties']['mappings'],
                             exp_res)

    def test_calc_frsw_port(self):
        self.app.node['id'] = 1
        self.app.node['properties']['name'] = 'FRSW1'
        exp_link = [{'source_port_id': 1,
                     'source_node_id': 1,
                     'source_port_name': '1',
                     'dest_dev': 'R1',
                     'source_dev': 'FRSW1',
                     'dest_port': 's0/0'}]
        self.app.calc_frsw_port('1', 'R1 s0/0')
        self.assertListEqual(self.app.node['ports'],
                             [{'id': 1, 'name': '1', 'port_number': 1}])
        self.assertListEqual(self.app.links, exp_link)
        self.assertEqual(self.app.port_id, 2)

    def test_set_qemu_symbol(self):
        self.app.device_info['from'] = 'ASA'
        self.app.set_qemu_symbol()

        self.assertEqual(self.app.node['default_symbol'],
                         ':/symbols/asa.normal.svg')
        self.assertEqual(self.app.node['hover_symbol'],
                         ':/symbols/asa.selected.svg')

    def test_add_vm_ethernet_ports(self):
        exp_res = [{'id': 1, 'name': 'Ethernet0', 'port_number': 0},
                   {'id': 2, 'name': 'Ethernet1', 'port_number': 1}]
        self.app.node['properties']['adapters'] = 2
        self.app.add_vm_ethernet_ports()

        self.assertListEqual(self.app.node['ports'], exp_res)
        self.assertEqual(self.app.port_id, 3)

    def test_add_to_qemu(self):
        self.app.node['qemu_id'] = 1
        self.app.device_info['ext_conf'] = 'QemuDevice'
        self.app.hypervisor['QemuDevice'] = {}
        self.app.hypervisor['qemu_path'] = '/bin/qemu'

        self.app.add_to_qemu()

        self.assertEqual(self.app.node['properties']['adapters'], 6)
        self.assertEqual(self.app.node['properties']['console'], 5001)
        self.assertEqual(self.app.node['properties']['qemu_path'], '/bin/qemu')
        self.assertEqual(self.app.node['properties']['ram'], 256)

    def test_add_to_qemu_asa(self):
        self.app.node['qemu_id'] = 1
        self.app.device_info['ext_conf'] = '5520'
        self.app.hypervisor['QemuDevice'] = {}
        self.app.hypervisor['qemu_path'] = '/bin/qemu'

        try:
            self.app.add_to_qemu()
        except ConvertError:
            self.assertRaises(ConvertError)

    def test_add_to_virtualbox(self):
        self.app.node['vbox_id'] = 1
        self.app.hypervisor['VBoxDevice'] = {}
        self.app.hypervisor['VBoxDevice']['image'] = 'image_name'
        self.app.hypervisor['VBoxDevice']['nics'] = 2

        self.app.add_to_virtualbox()

        self.assertEqual(self.app.node['properties']['vmname'], 'image_name')
        self.assertEqual(self.app.node['properties']['adapters'], 2)
        self.assertEqual(self.app.node['properties']['console'], 3501)

    @unittest.skip
    def test_add_device_items(self):
        # TODO
        self.fail()


if __name__ == '__main__':
    unittest.main()
