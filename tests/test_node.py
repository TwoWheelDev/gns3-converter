import unittest
from gns3converter.node import Node


class TestNode(unittest.TestCase):
    def setUp(self):
        self.app = Node()
        self.app.node['ports'] = []

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
