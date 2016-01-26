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
import re
from gns3converter.adapters import ADAPTER_MATRIX, PORT_TYPES
from gns3converter.models import MODEL_MATRIX
from gns3converter.interfaces import INTERFACE_RE, NUMBER_RE, MAPINT_RE, \
    VBQ_INT_RE, Interfaces
from gns3converter.utils import fix_path
from gns3converter.converterror import ConvertError


class Node(Interfaces):
    """
    This class defines a node used for building the Nodes configuration

    :param hypervisor: Hypervisor
    :param int port_id: starting port ID for this node
    """

    def __init__(self, hypervisor, port_id):
        super().__init__(port_id)
        self.node = {'ports': [],
                     'server_id': 1,
                     'label': {'x': 15, 'y': -25},
                     'properties': {}}
        self.device_info = {'chassis': '',
                            'model': '',
                            'npe': None}
        self.hypervisor = hypervisor
        self.config = []
        self.base_ports = {'vbox_console': 3501,
                           'qemu_console': 5001}

    def add_wic(self, old_wic, wic):
        """
        Convert the old style WIC slot to a new style WIC slot and add the WIC
        to the node properties

        :param str old_wic: Old WIC slot
        :param str wic: WIC name
        """
        new_wic = 'wic' + old_wic[-1]
        self.node['properties'][new_wic] = wic

    def add_wic_ports(self, wic_slot):
        """
        Add the ports for a specific WIC to the node['ports'] dictionary

        :param str wic_slot: WIC Slot (wic0)
        """
        wic_slot_number = int(wic_slot[3])
        wic_adapter = self.node['properties'][wic_slot]

        num_ports = ADAPTER_MATRIX[wic_adapter]['ports']
        port_type = ADAPTER_MATRIX[wic_adapter]['type']
        ports = []

        # Dynamips WICs port number start on a multiple of 16.
        base = 16 * (wic_slot_number + 1)
        # WICs are always in adapter slot 0.
        slot = 0

        for port_number in range(num_ports):
            phy_port_number = port_number + self.port_numbering[port_type]
            port_name = PORT_TYPES[port_type] + '%s/%s' % (slot,
                                                           phy_port_number)
            port_temp = {'name': port_name,
                         'id': self.port_id,
                         'port_number': base + port_number,
                         'slot_number': slot}
            ports.append(port_temp)
            self.port_id += 1
        self.port_numbering[port_type] += num_ports
        self.node['ports'].extend(ports)

    def add_slot_ports(self, slot):
        """
        Add the ports to be added for a adapter card

        :param str slot: Slot name
        """
        slot_nb = int(slot[4])
        # slot_adapter = None
        # if slot in self.node['properties']:
        #     slot_adapter = self.node['properties'][slot]
        # elif self.device_info['model'] == 'c7200':
        #     if self.device_info['npe'] == 'npe-g2':
        #         slot_adapter = 'C7200-IO-GE-E'
        #     else:
        #         slot_adapter = 'C7200-IO-2FE'

        slot_adapter = self.node['properties'][slot]

        num_ports = ADAPTER_MATRIX[slot_adapter]['ports']
        port_type = ADAPTER_MATRIX[slot_adapter]['type']
        ports = []

        for i in range(num_ports):
            port_name = PORT_TYPES[port_type] + '%s/%s' % (slot_nb, i)
            port_temp = {'name': port_name,
                         'id': self.port_id,
                         'port_number': i,
                         'slot_number': slot_nb}
            ports.append(port_temp)
            self.port_id += 1
        self.node['ports'].extend(ports)

    def add_info_from_hv(self):
        """
        Add the information we need from the old hypervisor section
        """
        # Router Image
        if 'image' in self.hypervisor:
            self.node['properties']['image'] = \
                os.path.basename(self.hypervisor['image'])
        # IDLE-PC
        if 'idlepc' in self.hypervisor:
            self.node['properties']['idlepc'] = self.hypervisor['idlepc']
        # Router RAM
        if 'ram' in self.hypervisor:
            self.node['properties']['ram'] = self.hypervisor['ram']
        # 7200 NPE
        if 'npe' in self.hypervisor:
            self.device_info['npe'] = self.hypervisor['npe']
        # Device Chassis
        if 'chassis' in self.hypervisor:
            self.device_info['chassis'] = self.hypervisor['chassis']
            if self.device_info['model'] == 'c3600':
                self.node['properties']['chassis'] = \
                    self.device_info['chassis']

    def add_device_items(self, item, device):
        """
        Add the various items from the device to the node

        :param str item: item key
        :param dict device: dictionary containing items
        """
        if item in ('aux', 'console'):
            self.node['properties'][item] = device[item]
        elif item.startswith('slot'):
            # if self.device_info['model'] == 'c7200':
            #     if item != 'slot0':
            #         self.node['properties'][item] = device[item]
            # else:
            self.node['properties'][item] = device[item]
        elif item == 'connections':
            self.connections = device[item]
        elif INTERFACE_RE.search(item) or VBQ_INT_RE.search(item):
            self.interfaces.append({'from': item,
                                    'to': device[item]})
        elif NUMBER_RE.search(item):
            if self.device_info['type'] == 'EthernetSwitch':
                self.calc_ethsw_port(item, device[item])
            elif self.device_info['type'] == 'FrameRelaySwitch':
                self.calc_frsw_port(item, device[item])
        elif MAPINT_RE.search(item):
            self.add_mapping((item, device[item]))
        elif item == 'cnfg':
            new_config = os.path.join('configs', 'i%s_startup-config.cfg' %
                                      self.node['id'])
            self.node['properties']['startup_config'] = new_config

            self.config.append({'old': fix_path(device[item]),
                                'new': new_config})
        elif item.startswith('wic'):
            self.add_wic(item, device[item])
        elif item == 'symbol':
            self.set_symbol(device[item])
        elif item == 'nics':
            self.node['properties']['adapters'] = device[item]
        elif item == 'image':
            self.node['properties']['vmname'] = device[item]
        elif item == 'vbox_id' or item == 'qemu_id':
            self.node[item] = device[item]

    def add_to_virtualbox(self):
        """
        Add additional parameters that were in the VBoxDevice section or not
        present
        """
        # VirtualBox Image
        if 'vmname' not in self.node['properties']:
            self.node['properties']['vmname'] = \
                self.hypervisor['VBoxDevice']['image']
        # Number of adapters
        if 'adapters' not in self.node['properties']:
            self.node['properties']['adapters'] = \
                self.hypervisor['VBoxDevice']['nics']
        # Console Port
        if 'console' not in self.node['properties']:
            self.node['properties']['console'] = \
                self.base_ports['vbox_console'] + self.node['vbox_id'] - 1

    def add_to_qemu(self):
        """
        Add additional parameters to a QemuVM Device that were present in its
        global conf section
        """
        device = self.device_info['ext_conf']

        if device == "5520":
            raise ConvertError("ASA 8 is not supported by GNS3 1.4. You should switch to ASAv. This topology can not be converted.")

        node_prop = self.node['properties']
        hv_device = self.hypervisor[device]
        # QEMU HDD Images
        if 'hda_disk_image' not in node_prop:
            if 'image' in hv_device:
                node_prop['hda_disk_image'] = hv_device['image']
            elif 'image1' in hv_device:
                node_prop['hda_disk_image'] = hv_device['image1']
        if 'hdb_disk_image' not in node_prop and 'image2' in hv_device:
            node_prop['hdb_disk_image'] = hv_device['image2']
        # RAM
        if 'ram' not in node_prop and 'ram' in hv_device:
            node_prop['ram'] = hv_device['ram']
        else:
            node_prop['ram'] = 256
        # QEMU Options
        if 'options' not in node_prop and 'options' in hv_device:
            node_prop['options'] = hv_device['options']
        # Kernel Image
        if 'kernel_image' not in node_prop and 'kernel' in hv_device:
            node_prop['kernel_image'] = hv_device['kernel']
        # Kernel Command Line
        if 'kernel_command_line' not in node_prop and \
                'kernel_cmdline' in hv_device:
            node_prop['kernel_command_line'] = hv_device['kernel_cmdline']
        # initrd
        if 'initrd' not in node_prop and 'initrd' in hv_device:
            node_prop['initrd'] = hv_device['initrd']
        # Number of adapters
        if 'adapters' not in node_prop and 'nics' in hv_device:
            node_prop['adapters'] = hv_device['nics']
        elif 'adapters' not in node_prop and 'nics' not in hv_device:
            node_prop['adapters'] = 6
        # Adapter type
        if 'adapter_type' not in node_prop and 'netcard' in hv_device:
            node_prop['adapter_type'] = hv_device['netcard']
        # Console Port
        if 'console' not in node_prop:
            node_prop['console'] = self.base_ports['qemu_console'] + \
                self.node['qemu_id'] - 1
        # Qemu Path
        if 'qemu_path' not in node_prop:
            qemu_path = self.hypervisor['qemu_path']
            # Modify QEMU Path if flavor is specified
            if 'flavor' in hv_device:
                qemu_path = re.sub(r'qemu-system-.*',
                                   'qemu-system' + hv_device['flavor'],
                                   qemu_path)
            node_prop['qemu_path'] = qemu_path

    def add_vm_ethernet_ports(self):
        """
        Add ethernet ports to Virtualbox and Qemu nodes
        """
        for i in range(self.node['properties']['adapters']):
            port = {'id': self.port_id,
                    'name': 'Ethernet%s' % i,
                    'port_number': i}
            self.node['ports'].append(port)
            self.port_id += 1

    def set_qemu_symbol(self):
        """
        Set the appropriate symbol for QEMU Devices
        """
        valid_devices = {'ASA': 'asa', 'PIX': 'PIX_firewall',
                         'JUNOS': 'router', 'IDS': 'ids'}
        if self.device_info['from'] in valid_devices \
                and 'default_symbol' not in self.node \
                and 'hover_symbol' not in self.node:
            self.set_symbol(valid_devices[self.device_info['from']])

    def set_symbol(self, symbol):
        """
        Set a symbol for a device

        :param str symbol: Symbol to use
        """
        if symbol == 'EtherSwitch router':
            symbol = 'multilayer_switch'
        elif symbol == 'Host':
            symbol = 'computer'

        normal = ':/symbols/%s.normal.svg' % symbol
        selected = ':/symbols/%s.selected.svg' % symbol

        self.node['default_symbol'] = normal
        self.node['hover_symbol'] = selected

    def calc_ethsw_port(self, port_num, port_def):
        """
        Split and create the port entry for an Ethernet Switch

        :param port_num: port number
        :type port_num: str or int
        :param str port_def: port definition
        """
        # Port String - access 1 SW2 1
        # 0: type 1: vlan 2: destination device 3: destination port
        port_def = port_def.split(' ')
        if len(port_def) == 4:
            destination = {'device': port_def[2],
                           'port': port_def[3]}
        else:
            destination = {'device': 'NIO',
                           'port': port_def[2]}
        # port entry
        port = {'id': self.port_id,
                'name': str(port_num),
                'port_number': int(port_num),
                'type': port_def[0],
                'vlan': int(port_def[1])}
        self.node['ports'].append(port)
        self.calc_link(self.node['id'], self.port_id, port['name'],
                       destination)
        self.port_id += 1

    def calc_frsw_port(self, port_num, port_def):
        """
        Split and create the port entry for a Frame Relay Switch

        :param port_num: port number
        :type port_num: str or int
        :param str port_def: port definition
        """
        port_def = port_def.split(' ')
        destination = {'device': port_def[0],
                       'port': port_def[1]}
        # port entry
        port = {'id': self.port_id,
                'name': str(port_num),
                'port_number': int(port_num)}
        self.node['ports'].append(port)
        self.calc_link(self.node['id'], self.port_id, port['name'],
                       destination)

        self.port_id += 1

    def calc_mb_ports(self):
        """
        Add the default ports to add to a router
        """
        model = self.device_info['model']
        chassis = self.device_info['chassis']
        num_ports = MODEL_MATRIX[model][chassis]['ports']
        ports = []

        if num_ports > 0:
            port_type = MODEL_MATRIX[model][chassis]['type']

            # Create the ports dict
            for i in range(num_ports):
                port_temp = {'name': PORT_TYPES[port_type] + '0/' + str(i),
                             'id': self.port_id,
                             'port_number': i,
                             'slot_number': 0}
                ports.append(port_temp)
                self.port_id += 1
        self.node['ports'].extend(ports)

    def calc_link(self, src_id, src_port, src_port_name, destination):
        """
        Add a link item for processing later

        :param int src_id: Source node ID
        :param int src_port: Source port ID
        :param str src_port_name: Source port name
        :param dict destination: Destination
        """
        if destination['device'] == 'NIO':
            destination['port'] = destination['port'].lower()

        link = {'source_node_id': src_id,
                'source_port_id': src_port,
                'source_port_name': src_port_name,
                'source_dev': self.node['properties']['name'],
                'dest_dev': destination['device'],
                'dest_port': destination['port']}

        self.links.append(link)

    def add_mapping(self, mapping):
        mapping = {'source': mapping[0],
                   'dest': mapping[1]}
        self.mappings.append(mapping)

    def set_description(self):
        """
        Set the node description
        """
        if self.device_info['type'] == 'Router':
            self.node['description'] = '%s %s' % (self.device_info['type'],
                                                  self.device_info['model'])
        else:
            self.node['description'] = self.device_info['desc']

    def set_type(self):
        """
        Set the node type
        """
        if self.device_info['type'] == 'Router':
            self.node['type'] = self.device_info['model'].upper()
        else:
            self.node['type'] = self.device_info['type']

    def get_nb_added_ports(self, old_port_id):
        """
        Get the number of ports add to the node

        :param int old_port_id: starting port_id
        :return: number of ports added
        :rtype: int
        """
        return self.port_id - old_port_id

    def calc_device_links(self):
        """
        Calculate a router or VirtualBox link
        """
        for connection in self.interfaces:
            int_type = connection['from'][0]
            int_name = connection['from'].replace(int_type,
                                                  PORT_TYPES[int_type.upper()])
            # Get the source port id
            src_port = None
            for port in self.node['ports']:
                if int_name == port['name']:
                    src_port = port['id']
                    break
            dest_temp = connection['to'].split(' ')

            if len(dest_temp) == 2:
                conn_to = {'device': dest_temp[0],
                           'port': dest_temp[1]}
            else:
                conn_to = {'device': 'NIO',
                           'port': dest_temp[0]}

            self.calc_link(self.node['id'], src_port, int_name, conn_to)

    def calc_cloud_connection(self):
        """
        Add the ports and nios for a cloud connection

        :return: None on success or RuntimeError on error
        """
        # Connection String - SW1:1:nio_gen_eth:eth0
        # 0: Destination device 1: Destination port
        # 2: NIO 3: NIO Destination
        self.node['properties']['nios'] = []
        if self.connections is None:
            return None
        else:
            self.connections = self.connections.split(' ')

        for connection in sorted(self.connections):
            connection = connection.split(':')
            connection_len = len(connection)
            if connection_len == 4:
                nio = '%s:%s' % (connection[2], connection[3])
            elif connection_len == 6:
                nio = '%s:%s:%s:%s' % (connection[2].lower(), connection[3],
                                       connection[4], connection[5])
            else:
                return RuntimeError('Error: Unknown connection string length '
                                    '(Length: %s)' % connection_len)
            self.node['properties']['nios'].append(nio)
            # port entry
            self.node['ports'].append({'id': self.port_id,
                                       'name': nio,
                                       'stub': True})
            self.port_id += 1
            return None

    def process_mappings(self):
        """
        Process the mappings for a Frame Relay switch. Removes duplicates and
        adds the mappings to the node properties
        """
        for mapping_a in self.mappings:
            for mapping_b in self.mappings:
                if mapping_a['source'] == mapping_b['dest']:
                    self.mappings.remove(mapping_b)
                    break

        self.node['properties']['mappings'] = {}
        mappings = self.node['properties']['mappings']
        for mapping in self.mappings:
            mappings[mapping['source']] = mapping['dest']
