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
import json
import datetime
import os
import sys
import shutil
import argparse
from gns3converter.converter import Converter
import gns3converter.version


def main():
    """
    Convert the topology
    :return:
    """
    print('GNS3 Topology Converter')

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Convert old ini-style GNS3 topologies (<=0.8.7) to the '
        'newer\nversion 1+ JSON format',
        epilog='Copyright (C) 2014 Daniel Lintott and licensed under the '
        'GPLv3+ license.\n\nPlease report any bugs to: '
        'https://github.com/dlintott/gns3-converter/issues')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' +
                        gns3converter.version.__version__)
    parser.add_argument('-o', '--output', help='Output the new topology to '
                        'this directory')
    parser.add_argument('topology', help='GNS3 .net topology file')
    parser.add_argument('--test_func',
                        help='Test Feature (remove before release)',
                        action='store_true')

    args = parser.parse_args()

    # Create a new instance of the the Converter
    gns3_conv = Converter(os.path.abspath(args.topology))
    # Read the old topology
    old_top = gns3_conv.read_topology()

    # Get the top-level sections from the topology
    sections = gns3_conv.get_instances(old_top)
    sections.append('GNS3-DATA')

    # Process the sections
    (devices, conf) = gns3_conv.process_topology(sections, old_top)

    # Generate the nodes
    topology_nodes = gns3_conv.generate_nodes(devices, conf)
    # Generate the links
    topology_links = gns3_conv.generate_links(topology_nodes)

    # Enter topology name
    topology_name = input('Please enter a name for this topology: ')
    topology_name = topology_name.replace(' ', '_')

    # Build the topology servers data
    topology_servers = [{'host': '127.0.0.1',
                         'id': 1,
                         'local': True,
                         'port': 8000}]
    # Compile the topology node
    topology = {'links': topology_links,
                'nodes': topology_nodes,
                'servers': topology_servers}
    # Compile all the sections ready for output
    assembled = {'name': topology_name,
                 'resources_type': 'local',
                 'topology': topology,
                 'type': 'topology',
                 'version': '1.0'}

    # Save the new topology
    try:
        date = datetime.datetime.now().strftime('%d%m%y-%H%M')
        config_err = False
        if args.output:
            output_dir = os.path.abspath(args.output)
        else:
            output_dir = os.getcwd()

        topology_dir = os.path.join(output_dir, topology_name)
        config_dir = os.path.join(topology_dir, topology_name + '-files',
                                  'dynamips', 'configs')
        # Prepare the directory structure
        if not os.path.exists(topology_dir):
            os.makedirs(config_dir)
        else:
            print('E: Topology folder for %s already exists, please choose a'
                  ' new name' % topology_name)
            sys.exit(1)
        # Move the config files to the new topology folder
        for config in gns3_conv.configs:
            old_config_file = os.path.abspath(config['old'])
            new_config_file = os.path.join(config_dir, config['new'])
            if os.path.isfile(old_config_file):
                # Copy and rename the config
                shutil.copy(old_config_file, new_config_file)
            else:
                config_err = True
                print('E: Unable to find %s' % config['old'])

        if config_err:
            print('W: Some router startup configurations could not be found\n'
                  '   to be copied to the new topology')

        filename = '%s-%s.gns3' % (topology_name, date)
        file_path = os.path.join(topology_dir, filename)
        with open(file_path, 'w') as file:
            json.dump(assembled, file, indent=4, sort_keys=True)
            print('Your topology has been converted and can found in:\n'
                  '     %s' % topology_dir)
    except OSError as error:
        print(error)

if __name__ == '__main__':
    main()
