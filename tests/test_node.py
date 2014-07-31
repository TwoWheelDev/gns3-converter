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


class TestNode(unittest.TestCase):
    def setUp(self):
        hv_input = {'image': '/home/test/GNS3/Images/c3725.image',
                    'idlepc': '0x61616161',
                    'ram': '256',
                    'npe': 'npe-400',
                    'chassis': '2620XM'}

        self.app = Node(hv_input)

    def test_add_wic(self):
        exp_res = {'wic0': 'WIC-1T'}

        self.app.add_wic('wic0/0', 'WIC-1T')
        self.assertDictEqual(exp_res, self.app.node_prop)

    def test_add_wic_ports(self):
        exp_res = [{'name': 'Serial0/0',
                    'id': 1,
                    'port_number': 16,
                    'slot_number': 0}]

        self.app.add_wic_ports('WIC-1T', 0, 1)
        self.assertDictEqual(exp_res[0], self.app.node['ports'][0])

    def test_add_info_from_hv(self):
        exp_res_node_prop = {'image': 'c3725.image',
                             'idlepc': '0x61616161',
                             'ram': '256'}
        exp_res_device_info = {'model': '',
                               'chassis': '2620XM',
                               'npe': 'npe-400'}

        self.app.add_info_from_hv()
        self.assertDictEqual(exp_res_node_prop, self.app.node_prop)
        self.assertDictEqual(exp_res_device_info, self.app.device_info)
