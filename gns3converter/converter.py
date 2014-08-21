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
 This class is the main gns3-converter class
"""
from configobj import ConfigObj, flatten_errors
from validate import Validator
import sys
import os.path
from pkg_resources import resource_stream
from gns3converter.adapters import PORT_TYPES
from gns3converter.models import MODEL_TRANSFORM
from gns3converter.node import Node
from gns3converter.interfaces import INTERFACE_RE
from gns3converter.topology import LegacyTopology
from gns3converter.utils import fix_path


class Converter():
    """
    GNS3 Topology Converter Class

    :param str topology: Filename of the ini-style topology
    :param bool debug: enable debugging (Default: False)
    """
    def __init__(self, topology, debug=False):
        self._topology = topology
        self._debug = debug

        self.port_id = 1
        self.links = []
        self.configs = []
        self.images = []

    def read_topology(self):
        """
        Read the ini-style topology file using ConfigObj

        :return config: Topology parsed by :py:mod:`ConfigObj`
        :rtype: ConfigObj
        """
        configspec = resource_stream(__name__, 'configspec')
        config = None
        try:
            handle = open(self._topology)
            handle.close()
            try:
                config = ConfigObj(self._topology,
                                   configspec=configspec,
                                   raise_errors=True,
                                   list_values=False,
                                   encoding='utf-8')
            except SyntaxError:
                print('Error loading .net file')
                exit()
        except IOError:
            print('Can\'t open topology file')
            exit()

        vtor = Validator()
        res = config.validate(vtor, preserve_errors=True)
        if res and self._debug:
            print('Validation Passed')
        elif not res:
            for entry in flatten_errors(config, res):
                # each entry is a tuple
                (section_list, key, error) = entry
                if key is not None:
                    section_list.append(key)
                else:
                    section_list.append('[missing section]')
                section_string = ', '.join(section_list)

                if error is False:
                    error = 'Missing value or section'
                print(section_string, ' = ', error)
                input('Press ENTER to continue')
                sys.exit(1)

        configspec.close()
        return config

    def process_topology(self, old_top):
        """
        Processes the sections returned by get_instances

        :param ConfigObj old_top: old topology as processed by
                                  :py:meth:`read_topology`
        :returns: tuple of dicts containing hypervisors, devices and artwork
        :rtype: tuple
        """
        sections = self.get_sections(old_top)
        topo = LegacyTopology(sections, old_top)

        for instance in sorted(sections):
            for item in sorted(old_top[instance]):
                if isinstance(old_top[instance][item], dict):
                    if item in MODEL_TRANSFORM:
                        # A configuration item (topo.conf)
                        topo.add_conf_item(instance, item)
                    elif instance == 'GNS3-DATA' and \
                            (item.startswith('SHAPE')
                             or item.startswith('NOTE')
                             or item.startswith('PIXMAP')):
                        # Item is an artwork item e.g. shapes and notes from
                        # GNS3-DATA
                        topo.add_artwork_item(instance, item)
                    else:
                        # It must be a physical item (topo.devices)
                        topo.add_physical_item(instance, item)
            topo.hv_id += 1
        return topo.devices, topo.conf, topo.artwork

    @staticmethod
    def get_sections(config):
        """
        Get a list of Hypervisor instances

        :param ConfigObj config: Configuration from :py:meth:`read_topology`
        :return: configuration sections
        :rtype: list
        """
        return config.sections

    def generate_nodes(self, devices, hypervisors):
        """
        Generate a list of nodes for the new topology

        :param list devices: list of devices from :py:meth:`process_topology`
        :param list hypervisors: list of hypervisors from
                                 :py:meth:`process_topology`
        :return: a list of dicts on nodes
        :rtype: list
        """
        nodes = []

        for device in sorted(devices):
            hv_id = devices[device]['hv_id']
            if hv_id in hypervisors:
                tmp_node = Node(hypervisors[hv_id], self.port_id)
            else:
                tmp_node = Node({}, self.port_id)
            # Start building the structure
            tmp_node.node['properties']['name'] = device
            tmp_node.node['label']['text'] = device
            tmp_node.node['id'] = devices[device]['node_id']
            tmp_node.node['x'] = devices[device]['x']
            tmp_node.node['y'] = devices[device]['y']
            tmp_node.device_info['type'] = devices[device]['type']

            if 'model' in devices[device]:
                tmp_node.device_info['model'] = devices[device]['model']
            else:
                tmp_node.device_info['model'] = ''

            tmp_node.set_description()
            tmp_node.set_type()

            # Now lets process the rest
            for item in sorted(devices[device]):
                tmp_node.add_device_items(item, devices[device])

            if tmp_node.device_info['type'] == 'Router':
                tmp_node.add_info_from_hv()
                tmp_node.node['router_id'] = devices[device]['node_id']
                tmp_node.calc_mb_ports()

                for item in sorted(tmp_node.node['properties']):
                    if item.startswith('slot'):
                        tmp_node.add_slot_ports(item)
                    elif item.startswith('wic'):
                        tmp_node.add_wic_ports(item)

                # Add default ports to 7200 and 3660
                if tmp_node.device_info['model'] == 'c7200':
                    tmp_node.add_slot_ports('slot0')
                elif tmp_node.device_info['model'] == 'c3600' \
                        and tmp_node.device_info['chassis'] == '3660':
                    tmp_node.node['properties']['slot0'] = 'Leopard-2FE'

                # Calculate the router links
                tmp_node.calc_router_links()

            elif tmp_node.device_info['type'] == 'Cloud':
                try:
                    tmp_node.calc_cloud_connection()
                except RuntimeError as err:
                    print(err)

            # Get the data we need back from the node instance
            self.links.extend(tmp_node.links)
            self.configs.extend(tmp_node.config)
            self.port_id += tmp_node.get_nb_added_ports(self.port_id)

            nodes.append(tmp_node.node)

        return nodes

    def generate_links(self, nodes):
        """
        Generate a list of links

        :param list nodes: A list of nodes from :py:meth:`generate_nodes`
        :return: list of links
        :rtype: list
        """
        links = []

        for link in self.links:
            # Expand port name if required
            if INTERFACE_RE.search(link['dest_port']):
                int_type = link['dest_port'][0]
                dest_port = link['dest_port'].replace(
                    int_type, PORT_TYPES[int_type.upper()])
            else:
                dest_port = link['dest_port']

            # Convert dest_dev and port to id's
            dest_details = self.convert_destination_to_id(
                link['dest_dev'], dest_port, nodes)

            desc = 'Link from %s port %s to %s port %s' % \
                   (link['source_dev'], link['source_port_name'],
                    dest_details['name'], dest_port)

            links.append({'description': desc,
                          'destination_node_id': dest_details['id'],
                          'destination_port_id': dest_details['pid'],
                          'source_port_id': link['source_port_id'],
                          'source_node_id': link['source_node_id']})

        # Remove duplicate links and add link_id
        link_id = 1
        for link in links:
            t_link = str(link['source_node_id']) + ':' + \
                str(link['source_port_id'])
            for link2 in links:
                d_link = str(link2['destination_node_id']) + ':' + \
                    str(link2['destination_port_id'])
                if t_link == d_link:
                    links.remove(link2)
                    break
            link['id'] = link_id
            link_id += 1

            self.add_node_connection(link, nodes)
        return links

    @staticmethod
    def device_id_from_name(device_name, nodes):
        """
        Get the device ID when given a device name

        :param str device_name: device name
        :param list nodes: list of nodes from :py:meth:`generate_nodes`
        :return: device ID
        :rtype: int
        """
        device_id = None
        for node in nodes:
            if device_name == node['properties']['name']:
                device_id = node['id']
                break
        return device_id

    @staticmethod
    def port_id_from_name(port_name, device_id, nodes):
        """
        Get the port ID when given a port name

        :param str port_name: port name
        :param str device_id: device ID
        :param list nodes: list of nodes from :py:meth:`generate_nodes`
        :return: port ID
        :rtype: int
        """
        port_id = None
        for node in nodes:
            if device_id == node['id']:
                for port in node['ports']:
                    if port_name == port['name']:
                        port_id = port['id']
                        break
                break
        return port_id

    @staticmethod
    def convert_destination_to_id(destination_node, destination_port, nodes):
        """
        Convert a destination to device and port ID

        :param str destination_node: Destination node name
        :param str destination_port: Destination port name
        :param list nodes: list of nodes from :py:meth:`generate_nodes`
        :return: dict containing device ID, device name and port ID
        :rtype: dict
        """
        device_id = None
        device_name = None
        port_id = None
        if destination_node != 'NIO':
            for node in nodes:
                if destination_node == node['properties']['name']:
                    device_id = node['id']
                    device_name = destination_node
                    for port in node['ports']:
                        if destination_port == port['name']:
                            port_id = port['id']
                            break
                    break
        else:
            for node in nodes:
                if node['type'] == 'Cloud':
                    for port in node['ports']:
                        if destination_port.lower() == port['name']:
                            device_id = node['id']
                            device_name = node['properties']['name']
                            port_id = port['id']
                            break
                    break
        info = {'id': device_id,
                'name': device_name,
                'pid': port_id}
        return info

    @staticmethod
    def get_node_name_from_id(node_id, nodes):
        """
        Get the name of a node when given the node_id

        :param int node_id: The ID of a node
        :param list nodes: list of nodes from :py:meth:`generate_nodes`
        :return: node name
        :rtype: str
        """
        node_name = ''
        for node in nodes:
            if node['id'] == node_id:
                node_name = node['properties']['name']
                break
        return node_name

    @staticmethod
    def get_port_name_from_id(node_id, port_id, nodes):
        """
        Get the name of a port for a given node and port ID

        :param int node_id: node ID
        :param int port_id: port ID
        :param list nodes: list of nodes from :py:meth:`generate_nodes`
        :return: port name
        :rtype: str
        """
        port_name = ''
        for node in nodes:
            if node['id'] == node_id:
                for port in node['ports']:
                    if port['id'] == port_id:
                        port_name = port['name']
                        break
        return port_name

    def add_node_connection(self, link, nodes):
        """
        Add a connection to a node

        :param dict link: link definition
        :param list nodes: list of nodes from :py:meth:`generate_nodes`
        """
        # Description
        src_desc = 'connected to %s on port %s' % \
                   (self.get_node_name_from_id(link['destination_node_id'],
                                               nodes),
                    self.get_port_name_from_id(link['destination_node_id'],
                                               link['destination_port_id'],
                                               nodes))
        dest_desc = 'connected to %s on port %s' % \
                    (self.get_node_name_from_id(link['source_node_id'],
                                                nodes),
                     self.get_port_name_from_id(link['source_node_id'],
                                                link['source_port_id'],
                                                nodes))
        # Add source connections
        for node in nodes:
            if node['id'] == link['source_node_id']:
                for port in node['ports']:
                    if port['id'] == link['source_port_id']:
                        port['link_id'] = link['id']
                        port['description'] = src_desc
                        break
            elif node['id'] == link['destination_node_id']:
                for port in node['ports']:
                    if port['id'] == link['destination_port_id']:
                        port['link_id'] = link['id']
                        port['description'] = dest_desc
                        break

    @staticmethod
    def generate_shapes(shapes):
        """
        Generate the shapes for the topology

        :param dict shapes: A dict of converted shapes from the old topology
        :return: dict containing two lists (ellipse, rectangle)
        :rtype: dict
        """
        new_shapes = {'ellipse': [], 'rectangle': []}

        for shape in shapes:
            tmp_shape = {}
            for shape_item in shapes[shape]:
                if shape_item != 'type':
                    tmp_shape[shape_item] = shapes[shape][shape_item]

            new_shapes[shapes[shape]['type']].append(tmp_shape)
        return new_shapes

    @staticmethod
    def generate_notes(notes):
        """
        Generate the notes list

        :param dict notes: A dict of converted notes from the old topology
        :return: List of notes for the the topology
        :rtype: list
        """
        new_notes = []

        for note in notes:
            tmp_note = {}
            for note_item in notes[note]:
                tmp_note[note_item] = notes[note][note_item]

            new_notes.append(tmp_note)
        return new_notes

    def generate_images(self, pixmaps):
        """
        Generate the images list and store the images to copy

        :param dict pixmaps: A dict of converted pixmaps from the old topology
        :return: A list of images
        :rtype: list
        """
        new_images = []

        for image in pixmaps:
            tmp_image = {}
            for img_item in pixmaps[image]:
                if img_item == 'path':
                    path = os.path.join('images',
                                        os.path.basename(
                                            pixmaps[image][img_item]))
                    tmp_image['path'] = fix_path(path)
                    self.images.append(pixmaps[image][img_item])
                else:
                    tmp_image[img_item] = pixmaps[image][img_item]

            new_images.append(tmp_image)
        return new_images