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
from gns3converter.models import MODEL_TRANSFORM


class LegacyTopology():
    """
    Legacy Topology (pre-1.0)

    :param list sections: list of sections from
        :py:meth:`gns3converter.converter.Converter.get_instances`
    :param ConfigObj old_top: Old topology as returned by
        :py:meth:`gns3converter.converter.Converter.read_topology`
    """
    def __init__(self, sections, old_top):
        self.devices = {}
        self.conf = {}
        self.hv_id = 0
        self.nid = 1
        self.sections = sections
        self.old_top = old_top
        self.artwork = {'SHAPE': {}, 'NOTE': {}, 'PIXMAP': {}}

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

                    self.artwork[item_type][item_id][s_item] = s_detail

    def add_conf_item(self, instance, item):
        """
        Add a hypervisor configuration item

        :param instance: Hypervisor instance
        :param item: Item to add
        """
        self.conf[self.hv_id] = {}
        self.conf[self.hv_id]['model'] = MODEL_TRANSFORM[item]
        for s_item in sorted(self.old_top[instance][item]):
            if self.old_top[instance][item][s_item] is not None:
                self.conf[self.hv_id][s_item] = \
                    self.old_top[instance][item][s_item]

    def add_physical_item(self, instance, item):
        """
        Add a physical item e.g router, cloud etc

        :param instance: Hypervisor instance
        :param item: Item to add
        """
        (device_name, device_type) = self.device_typename(item)
        self.devices[device_name] = {}
        self.devices[device_name]['hv_id'] = self.hv_id
        self.devices[device_name]['node_id'] = self.nid
        self.devices[device_name]['type'] = device_type['type']

        for s_item in sorted(self.old_top[instance][item]):
            if self.old_top[instance][item][s_item] is not None:
                self.devices[device_name][s_item] = \
                    self.old_top[instance][item][s_item]

        if instance != 'GNS3-DATA' and \
                self.devices[device_name]['type'] == 'Router':
            if 'model' not in self.devices[device_name]:
                self.devices[device_name]['model'] = \
                    self.conf[self.hv_id]['model']
            else:
                self.devices[device_name]['model'] = \
                    MODEL_TRANSFORM[self.devices[device_name]['model']]
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
                               'type': 'Router'},
                    'QEMU': {'from': 'QEMU',
                             'desc': 'QEMU',
                             'type': 'QEMU'},
                    'VBOX': {'from': 'VBOX',
                             'desc': 'VBOX',
                             'type': 'VBOX'},
                    'FRSW': {'from': 'FRSW',
                             'desc': 'Frame Relay switch',
                             'type': 'FrameRelaySwitch'},
                    'ETHSW': {'from': 'ETHSW',
                              'desc': 'Ethernet switch',
                              'type': 'EthernetSwitch'},
                    'Hub': {'from': 'Hub',
                            'desc': 'Ethernet hub',
                            'type': 'EthernetHub'},
                    'ATMSW': {'from': 'ATMSW',
                              'desc': 'ATM switch',
                              'type': 'ATMSwitch'},
                    'ATMBR': {'from': 'ATMBR',
                              'desc': 'ATMBR',
                              'type': 'ATMBR'},
                    'Cloud': {'from': 'Cloud',
                              'desc': 'Cloud',
                              'type': 'Cloud'}}

        item_type = item.split(' ')[0]
        name = item.replace('%s ' % dev_type[item_type]['from'], '')
        return name, dev_type[item_type]


class JSONTopology():
    """
    v1.0 JSON Topology
    """
    def __init__(self):
        self._nodes = None
        self._links = None
        self._notes = None
        self._shapes = None
        self._images = None
        self._servers = [{'host': '127.0.0.1', 'id': 1, 'local': True,
                          'port': 8000}]
        self._name = None

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        self._nodes = nodes

    @property
    def links(self):
        return self._links

    @links.setter
    def links(self, links):
        self._links = links

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, notes):
        self._notes = notes

    @property
    def shapes(self):
        return self._shapes

    @shapes.setter
    def shapes(self, shapes):
        self._shapes = shapes

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, images):
        self._images = images

    @property
    def servers(self):
        return self._servers

    @servers.setter
    def servers(self, servers):
        self._servers = servers

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
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

        if self._links is not None:
            topology['topology']['links'] = self._links
        if self._nodes is not None:
            topology['topology']['nodes'] = self._nodes
        if self._servers is not None:
            topology['topology']['servers'] = self._servers
        if self._notes is not None:
            topology['topology']['notes'] = self._notes
        if self._shapes['ellipse'] is not None:
            topology['topology']['ellipses'] = self._shapes['ellipse']
        if self._shapes['rectangle'] is not None:
            topology['topology']['rectangles'] = \
                self._shapes['rectangle']
        if self._images is not None:
            topology['topology']['images'] = self._images

        return topology
