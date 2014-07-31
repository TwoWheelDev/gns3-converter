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
from gns3converter.topology import LegacyTopology


class TestTopology(unittest.TestCase):
    def setUp(self):
        self.app = LegacyTopology('', '')

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

if __name__ == '__main__':
    unittest.main()