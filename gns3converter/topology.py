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
This module is for processing a topology
"""
from gns3converter.models import MODEL_TRANSFORM, EXTRA_CONF


class LegacyTopology():
    """
    Legacy Topology (pre-1.0)

    :param list sections: list of sections from
        :py:meth:`gns3converter.converter.Converter.get_instances`
    :param ConfigObj old_top: Old topology as returned by
        :py:meth:`gns3converter.converter.Converter.read_topology`
    """
    def __init__(self, sections, old_top):
        self.topology = {'devices': {},
                         'conf': [],
                         'artwork': {'SHAPE': {}, 'NOTE': {}, 'PIXMAP': {}}}
        self.sections = sections
        self.old_top = old_top
        self._id = {'hv_id': 0,
                    'nid': 1,
                    'vbox_id': 1,
                    'qemu_id': 1}

    @property
    def artwork(self):
        """
        Return the Artwork dict

        :return: artwork dict
        :rtype: dict
        """
        return self.topology['artwork']

    @property
    def hv_id(self):
        """
        Return the Hypervisor ID

        :return: Hypervisor ID
        :rtype: int
        """
        return self._id['hv_id']

    @hv_id.setter
    def hv_id(self, value):
        """
        Set the Hypervisor ID

        :param int value: Hypervisor ID
        """
        self._id['hv_id'] = value

    @property
    def nid(self):
        """
        Return the node ID

        :return: Node ID
        :rtype: int
        """
        return self._id['nid']

    @nid.setter
    def nid(self, value):
        """
        Set the node ID
        :param int value: Node ID
        """
        self._id['nid'] = value

    @property
    def vbox_id(self):
        """
        Return the VBox ID
        :return: VBox ID
        :rtype: int
        """
        return self._id['vbox_id']

    @vbox_id.setter
    def vbox_id(self, value):
        """
        Set the VBox ID

        :param int value: VBox ID
        """
        self._id['vbox_id'] = value

    @property
    def qemu_id(self):
        """
        Return the Qemu VM ID
        :return: Qemu VM ID
        :rtype: int
        """
        return self._id['qemu_id']

    @qemu_id.setter
    def qemu_id(self, value):
        """
        Set the Qemu VM ID

        :param int value: Qemu VM ID
        """
        self._id['qemu_id'] = value

    def add_artwork_item(self, instance, item):
        """
        Add an artwork item e.g. Shapes, Notes and Pixmaps

        :param instance: Hypervisor instance
        :param item: Item to add
        """
        if 'interface' in self.old_top[instance][item]:
            pass
        else:
            (item_type, item_id) = item.split(' ')
            self.artwork[item_type][item_id] = {}
            for s_item in sorted(self.old_top[instance][item]):
                if self.old_top[instance][item][s_item] is not None:
                    s_detail = self.old_top[instance][item][s_item]
                    s_type = type(s_detail)

                    if item_type == 'NOTE' and s_type == str:
                        # Fix any escaped newline characters
                        s_detail = s_detail.replace('\\n', '\n')

                    if s_type == str and len(s_detail) > 1 \
                            and s_detail[0] == '"' and s_detail[-1] == '"':
                        s_detail = s_detail[1:-1]

                    if item_type == 'SHAPE' and s_item == 'fill_color':
                        s_item = 'color'
                    elif s_item == 'rotate':
                        s_item = 'rotation'
                        s_detail = float(s_detail)

                    self.artwork[item_type][item_id][s_item] = s_detail

            if item_type == 'SHAPE' and \
                    'color' not in self.artwork[item_type][item_id]:
                self.artwork[item_type][item_id]['color'] = '#ffffff'
                self.artwork[item_type][item_id]['transparency'] = 0

    def add_qemu_path(self, instance):
        """
        Add the qemu path to the hypervisor conf data

        :param instance: Hypervisor instance
        """
        tmp_conf = {'qemu_path': self.old_top[instance]['qemupath']}
        if len(self.topology['conf']) == 0:
            self.topology['conf'].append(tmp_conf)
        else:
            self.topology['conf'][self.hv_id].update(tmp_conf)

    def add_conf_item(self, instance, item):
        """
        Add a hypervisor configuration item

        :param instance: Hypervisor instance
        :param item: Item to add
        """
        tmp_conf = {}

        if item not in EXTRA_CONF:
            tmp_conf['model'] = MODEL_TRANSFORM[item]

        for s_item in sorted(self.old_top[instance][item]):
            if self.old_top[instance][item][s_item] is not None:
                tmp_conf[s_item] = self.old_top[instance][item][s_item]

        if item in EXTRA_CONF:
            tmp_conf = {item: tmp_conf}
            if len(self.topology['conf']) == 0:
                self.topology['conf'].append(tmp_conf)
            else:
                self.topology['conf'][self.hv_id].update(tmp_conf)
        else:
            self.topology['conf'].append(tmp_conf)
        self.hv_id = len(self.topology['conf']) - 1

    def add_physical_item(self, instance, item):
        """
        Add a physical item e.g router, cloud etc

        :param instance: Hypervisor instance
        :param item: Item to add
        """
        (name, dev_type) = self.device_typename(item)
        self.topology['devices'][name] = {}
        self.topology['devices'][name]['hv_id'] = self.hv_id
        self.topology['devices'][name]['node_id'] = self.nid
        self.topology['devices'][name]['from'] = dev_type['from']
        self.topology['devices'][name]['type'] = dev_type['type']
        self.topology['devices'][name]['desc'] = dev_type['desc']

        if 'ext_conf' in dev_type:
            self.topology['devices'][name]['ext_conf'] = dev_type['ext_conf']

        for s_item in sorted(self.old_top[instance][item]):
            if self.old_top[instance][item][s_item] is not None:
                self.topology['devices'][name][s_item] = \
                    self.old_top[instance][item][s_item]

        if instance != 'GNS3-DATA' and \
                self.topology['devices'][name]['type'] == 'Router':
            if 'model' not in self.topology['devices'][name]:
                self.topology['devices'][name]['model'] = \
                    self.topology['conf'][self.hv_id]['model']
            else:
                self.topology['devices'][name]['model'] = MODEL_TRANSFORM[
                    self.topology['devices'][name]['model']]
        elif dev_type['type'] == 'VirtualBoxVM':
            self.topology['devices'][name]['vbox_id'] = self.vbox_id
            self.vbox_id += 1
        elif dev_type['type'] == 'QemuVM':
            self.topology['devices'][name]['qemu_id'] = self.qemu_id
            self.qemu_id += 1

        if instance != 'GNS3-DATA' \
            and 'hx' not in self.topology['devices'][name] \
                and 'hy' not in self.topology['devices'][name]:
            self.topology['devices'][name]['hx'] = dev_type['label_x']
            self.topology['devices'][name]['hy'] = -25.0
        self.nid += 1

    @staticmethod
    def device_typename(item):
        """
        Convert the old names to new-style names and types

        :param str item: A device in the form of 'TYPE NAME'
        :return: tuple containing device name and type details
        """

        dev_type = {'ROUTER': {'from': 'ROUTER',
                               'desc': 'Router',
                               'type': 'Router',
                               'label_x': 19.5},
                    'QEMU': {'from': 'QEMU',
                             'desc': 'QEMU VM',
                             'type': 'QemuVM',
                             'ext_conf': 'QemuDevice',
                             'label_x': -12},
                    'ASA': {'from': 'ASA',
                            'desc': 'QEMU VM',
                            'type': 'QemuVM',
                            'ext_conf': '5520',
                            'label_x': 2.5},
                    'PIX': {'from': 'PIX',
                            'desc': 'QEMU VM',
                            'type': 'QemuVM',
                            'ext_conf': '525',
                            'label_x': -12},
                    'JUNOS': {'from': 'JUNOS',
                              'desc': 'QEMU VM',
                              'type': 'QemuVM',
                              'ext_conf': 'O-series',
                              'label_x': -12},
                    'IDS': {'from': 'IDS',
                            'desc': 'QEMU VM',
                            'type': 'QemuVM',
                            'ext_conf': 'IDS-4215',
                            'label_x': -12},
                    'VBOX': {'from': 'VBOX',
                             'desc': 'VirtualBox VM',
                             'type': 'VirtualBoxVM',
                             'ext_conf': 'VBoxDevice',
                             'label_x': -4.5},
                    'FRSW': {'from': 'FRSW',
                             'desc': 'Frame Relay switch',
                             'type': 'FrameRelaySwitch',
                             'label_x': 7.5},
                    'ETHSW': {'from': 'ETHSW',
                              'desc': 'Ethernet switch',
                              'type': 'EthernetSwitch',
                              'label_x': 15.5},
                    'Hub': {'from': 'Hub',
                            'desc': 'Ethernet hub',
                            'type': 'EthernetHub',
                            'label_x': 12.0},
                    'ATMSW': {'from': 'ATMSW',
                              'desc': 'ATM switch',
                              'type': 'ATMSwitch',
                              'label_x': 2.0},
                    'ATMBR': {'from': 'ATMBR',  # TODO: Investigate ATM Bridge
                              'desc': 'ATMBR',
                              'type': 'ATMBR'},
                    'Cloud': {'from': 'Cloud',
                              'desc': 'Cloud',
                              'type': 'Cloud',
                              'label_x': 47.5}}

        item_type = item.split(' ')[0]
        name = item.replace('%s ' % dev_type[item_type]['from'], '')
        return name, dev_type[item_type]


class JSONTopology():
    """
    v1.0 JSON Topology
    """
    def __init__(self):
        self._nodes = []
        self._links = []
        self._notes = []
        self._shapes = {'ellipse': None,
                        'rectangle': None}
        self._images = []
        self._servers = [{'host': '127.0.0.1', 'id': 1, 'local': True,
                          'port': 8000}]
        self._name = None

    @property
    def nodes(self):
        """
        Returns the nodes

        :return: topology nodes
        :rtype: list
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """
        Sets the nodes

        :param list nodes: List of nodes from
               :py:meth:`gns3converter.converter.Converter.generate_nodes`
        """
        self._nodes = nodes

    @property
    def links(self):
        """
        Returns the links

        :return: Topology links
        :rtype: list
        """
        return self._links

    @links.setter
    def links(self, links):
        """
        Sets the links

        :param list links: List of links from
               :py:meth:`gns3converter.converter.Converter.generate_links`
        """
        self._links = links

    @property
    def notes(self):
        """
        Returns the notes

        :return: Topology notes
        :rtype: list
        """
        return self._notes

    @notes.setter
    def notes(self, notes):
        """
        Sets the notes

        :param list notes: List of notes from
               :py:meth:`gns3converter.converter.Converter.generate_notes`
        """
        self._notes = notes

    @property
    def shapes(self):
        """
        Returns the shapes

        :return: Topology shapes
        :rtype: dict
        """
        return self._shapes

    @shapes.setter
    def shapes(self, shapes):
        """
        Sets the shapes

        :param dict shapes: List of shapes from
               :py:meth:`gns3converter.converter.Converter.generate_shapes`
        """
        self._shapes = shapes

    @property
    def images(self):
        """
        Returns the images

        :return: Topology images
        :rtype: list
        """
        return self._images

    @images.setter
    def images(self, images):
        """
        Sets the images

        :param list images: List of images from
               :py:meth:`gns3converter.converter.Converter.generate_images`
        """
        self._images = images

    @property
    def servers(self):
        """
        Returns the servers

        :return: Topology servers
        :rtype: list
        """
        return self._servers

    @servers.setter
    def servers(self, servers):
        """
        Sets the servers

        :param list servers: List of servers
        """
        self._servers = servers

    @property
    def name(self):
        """
        Returns the topology name

        :return: Topology name
        :rtype: None or str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the topology name
        :param str name: Topology name
        """
        self._name = name

    def get_topology(self):
        """
        Get the converted topology ready for JSON encoding

        :return: converted topology assembled into a single dict
        :rtype: dict
        """
        topology = {'name': self._name,
                    'resources_type': 'local',
                    'topology': {},
                    'type': 'topology',
                    'version': '1.0'}

        if self._links:
            topology['topology']['links'] = self._links
        if self._nodes:
            topology['topology']['nodes'] = self._nodes
        if self._servers:
            topology['topology']['servers'] = self._servers
        if self._notes:
            topology['topology']['notes'] = self._notes
        if self._shapes['ellipse']:
            topology['topology']['ellipses'] = self._shapes['ellipse']
        if self._shapes['rectangle']:
            topology['topology']['rectangles'] = \
                self._shapes['rectangle']
        if self._images:
            topology['topology']['images'] = self._images

        return topology

    def get_vboxes(self):
        """
        Get the maximum ID of the VBoxes

        :return: Maximum VBox ID
        :rtype: int
        """
        vbox_list = []
        vbox_max = None
        for node in self.nodes:
            if node['type'] == 'VirtualBoxVM':
                vbox_list.append(node['vbox_id'])

        if len(vbox_list) > 0:
            vbox_max = max(vbox_list)
        return vbox_max

    def get_qemus(self):
        """
        Get the maximum ID of the Qemu VMs

        :return: Maximum Qemu VM ID
        :rtype: int
        """
        qemu_vm_list = []
        qemu_vm_max = None
        for node in self.nodes:
            if node['type'] == 'QemuVM':
                qemu_vm_list.append(node['qemu_id'])

        if len(qemu_vm_list) > 0:
            qemu_vm_max = max(qemu_vm_list)
        return qemu_vm_max
