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
"""
This module is used for building Nodes
"""
import os
from .ports import ADAPTER_MATRIX, PORT_TYPES


class Node():
    """
    This class defines a node used for building the Nodes configuration
    """
    def __init__(self):
        self.node = {'ports': [],
                     'server_id': 1}
        self.node_label = {'x': 15,
                           'y': -25}
        self.node_prop = {}
        self.device_info = {'chassis': '',
                            'model': '',
                            'npe': None}

    def add_wic(self, old_wic, wic):
        """
        Convert the old style WIC slot to a new style WIC slot and add the WIC
        to the node properties
        :param old_wic: Old WIC slot
        :param wic: WIC name
        """
        new_wic = 'wic' + old_wic[-1]
        self.node_prop[new_wic] = wic

    def add_wic_ports(self, wic, wic_slot_number, port_id):
        """
        Add the ports for a specific WIC to the node['ports'] dictionary
        :param wic: WIC name
        :param wic_slot_number: WIC Slot Number (integer)
        """
        num_ports = ADAPTER_MATRIX[wic]['ports']
        port_type = ADAPTER_MATRIX[wic]['type']
        ports = []

        # Dynamips WICs port number start on a multiple of 16.
        base = 16 * (wic_slot_number + 1)
        # WICs are always in adapter slot 0.
        slot = 0

        for port_number in range(num_ports):
            port_name = PORT_TYPES[port_type] + '%s/%s' % (slot, port_number)
            port_temp = {'name': port_name,
                         'id': port_id,
                         'port_number': base + port_number,
                         'slot_number': slot}
            ports.append(port_temp)
            port_id += 1
        self.node['ports'].extend(ports)
        return num_ports

    def add_info_from_hv(self, hv):
        self.node_prop['image'] = os.path.basename(hv['image'])

        # IDLE-PC
        if 'idlepc' in hv:
            self.node_prop['idlepc'] = hv['idlepc']
        # Router RAM
        if 'ram' in hv:
            self.node_prop['ram'] = hv['ram']
        # 7200 NPE
        if 'npe' in hv:
            self.device_info['npe'] = hv['npe']
        # Device Chassis
        if 'chassis' in hv:
            self.device_info['chassis'] = hv['chassis']
