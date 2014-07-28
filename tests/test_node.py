import unittest
from gns3converter.node import Node


class TestNode(unittest.TestCase):
    def setUp(self):
        self.app = Node()

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
        hv_input = {'image': '/home/test/GNS3/Images/c3725.image',
                    'idlepc': '0x61616161',
                    'ram': '256',
                    'npe': 'npe-400',
                    'chassis': '2620XM'}

        exp_res_node_prop = {'image': 'c3725.image',
                             'idlepc': '0x61616161',
                             'ram': '256'}
        exp_res_device_info = {'model': '',
                               'chassis': '2620XM',
                               'npe': 'npe-400'}

        self.app.add_info_from_hv(hv_input)
        self.assertDictEqual(exp_res_node_prop, self.app.node_prop)
        self.assertDictEqual(exp_res_device_info, self.app.device_info)
