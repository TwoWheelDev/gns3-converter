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

    def test_device_typename(self):
        exp_result = {'ROUTER R1': {'name': 'R1', 'type': 'Router'},
                      'QEMU Q1': {'name': 'Q1', 'type': 'QEMU'},
                      'VBOX V1': {'name': 'V1', 'type': 'VBOX'},
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

    def test_calc_cloud_connection(self):
        exp_result = {'id': 1,
                      'name': 'nio_gen_eth:eth0',
                      'stub': True}
        (port, nio) = self.app.calc_cloud_connection('SW1:1:nio_gen_eth:eth0')
        #Check NIO String
        self.assertIsInstance(nio, str)
        self.assertEqual(nio, 'nio_gen_eth:eth0')
        #Check Port dictionary
        self.assertIsInstance(port, dict)
        self.assertDictEqual(port, exp_result)

    def test_calc_ethsw_port_device(self):
        exp_port = {'id': 1, 'name': 1, 'port_number': 1,
                    'type': 'access', 'vlan': 1}
        exp_dest = {'device': 'SW2', 'port': '1'}

        (port, dest) = self.app.calc_ethsw_port(1, 'access 1 SW2 1')
        self.assertIsInstance(dest, dict)
        self.assertIsInstance(port, dict)
        self.assertDictEqual(port, exp_port)
        self.assertDictEqual(dest, exp_dest)

    def test_calc_ethsw_port_nio(self):
        exp_port = {'id': 1, 'name': 1, 'port_number': 1,
                    'type': 'access', 'vlan': 1}
        exp_dest = {'device': 'NIO', 'port': 'nio_gen_eth:eth0'}

        (port, dest) = self.app.calc_ethsw_port(1, 'access 1 nio_gen_eth:eth0')
        self.assertIsInstance(dest, dict)
        self.assertIsInstance(port, dict)
        self.assertDictEqual(port, exp_port)
        self.assertDictEqual(dest, exp_dest)

    def test_calc_link(self):
        exp_res = {'source_node_id': 1,
                   'source_port_id': 2,
                   'source_port_name': 'FastEthernet0/0',
                   'source_dev': 'R1',
                   'dest_dev': 'SiteA',
                   'dest_port': 'f0/0'}

        res = self.app.calc_link(1, 2, 'FastEthernet0/0', 'R1',
                                 {'device': 'SiteA', 'port': 'f0/0'})
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, exp_res)

    def test_calc_mb_ports_c3725(self):
        exp_res = [{'name': 'FastEthernet0/0', 'id': 1, 'port_number': 0,
                    'slot_number': 0},
                   {'name': 'FastEthernet0/1', 'id': 2, 'port_number': 1,
                    'slot_number': 0}]

        res = self.app.calc_mb_ports('c3725')
        self.assertIsInstance(res, list)
        self.assertDictEqual(res[0], exp_res[0])
        self.assertDictEqual(res[1], exp_res[1])

    def test_calc_mb_ports_c2600(self):
        exp_res = [{'name': 'Ethernet0/0', 'id': 1, 'port_number': 0,
                    'slot_number': 0}]

        res = self.app.calc_mb_ports('c2600', '2610')
        self.assertIsInstance(res, list)
        self.assertDictEqual(res[0], exp_res[0])

    def test_calc_slot_ports(self):
        exp_res = [{'name': 'Serial1/0', 'id': 1, 'port_number': 0,
                    'slot_number': 1},
                   {'name': 'Serial1/1', 'id': 2, 'port_number': 1,
                    'slot_number': 1},
                   {'name': 'Serial1/2', 'id': 3, 'port_number': 2,
                    'slot_number': 1},
                   {'name': 'Serial1/3', 'id': 4, 'port_number': 3,
                    'slot_number': 1}]

        res = self.app.calc_slot_ports('NM-4T', 1)
        self.assertIsInstance(res, list)
        self.assertDictEqual(res[0], exp_res[0])
        self.assertDictEqual(res[1], exp_res[1])
        self.assertDictEqual(res[2], exp_res[2])
        self.assertDictEqual(res[3], exp_res[3])

if __name__ == '__main__':
    unittest.main()