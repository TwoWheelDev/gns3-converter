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
import os
import shutil
import argparse
import logging
import re
import glob
from gns3converter import __version__
from gns3converter.converter import Converter
from gns3converter.converterror import ConvertError
from gns3converter.topology import JSONTopology

LOG_MSG_FMT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] ' \
              '%(message)s'
LOG_DATE_FMT = '%y%m%d %H:%M:%S'


def main():
    """
    Entry point for gns3-converter
    """
    arg_parse = setup_argparse()
    args = arg_parse.parse_args()

    if not args.quiet:
        print('GNS3 Topology Converter')

    if args.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.WARNING

    logging.basicConfig(level=logging_level,
                        format=LOG_MSG_FMT, datefmt=LOG_DATE_FMT)

    logging.getLogger(__name__)

    # Add the main topology to the list of files to convert
    if args.topology == 'topology.net':
        args.topology = os.path.join(os.getcwd(), 'topology.net')

    topology_files = [{'file': topology_abspath(args.topology),
                       'snapshot': False}]

    # Add any snapshot topologies to be converted
    topology_files.extend(get_snapshots(args.topology))

    topology_name = name(args.topology, args.name)

    # Do the conversion
    for topology in topology_files:
        do_conversion(topology, topology_name, args.output, args.debug)


def setup_argparse():
    """
    Setup the argparse argument parser

    :return: instance of argparse
    :rtype: ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='Convert old ini-style GNS3 topologies (<=0.8.7) to '
                    'the newer version 1+ JSON format')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-n', '--name', help='Topology name (default uses the '
                                             'name of the old project '
                                             'directory)')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('topology', nargs='?', default='topology.net',
                        help='GNS3 .net topology file (default: topology.net)')
    parser.add_argument('--debug',
                        help='Enable debugging output',
                        action='store_true')
    parser.add_argument('-q', '--quiet',
                        help='Quiet-mode (no output to console)',
                        action='store_true')
    return parser


def do_conversion(topology_def, topology_name, output_dir=None, debug=False,
                  quiet=False):
    """
    Convert the topology

    :param dict topology_def: Dict containing topology file and snapshot bool.
                              For example:
                              ``{'file': filename, 'snapshot': False}``
    :param str topology_name: The name of the topology
    :param str output_dir: The directory in which to output the topology.
                           (Default: None)
    :param bool debug: Enable debugging (Default: False)
    """
    # Create a new instance of the the Converter
    gns3_conv = Converter(topology_def['file'], debug)
    # Read the old topology
    old_top = gns3_conv.read_topology()
    new_top = JSONTopology()

    # Process the sections
    (topology) = gns3_conv.process_topology(old_top)

    # Generate the nodes
    new_top.nodes = gns3_conv.generate_nodes(topology)
    # Generate the links
    new_top.links = gns3_conv.generate_links(new_top.nodes)

    new_top.notes = gns3_conv.generate_notes(topology['artwork']['NOTE'])
    new_top.shapes = gns3_conv.generate_shapes(topology['artwork']['SHAPE'])
    new_top.images = gns3_conv.generate_images(topology['artwork']['PIXMAP'])

    # Enter topology name
    new_top.name = topology_name

    # Save the new topology
    save(output_dir, gns3_conv, new_top, topology_def['snapshot'], quiet)


def topology_abspath(topology):
    """
    Get the absolute path of the topology file

    :param str topology: Topology file
    :return: Absolute path of topology file
    :rtype: str
    """
    return os.path.abspath(topology)


def topology_dirname(topology):
    """
    Get the directory containing the topology file

    :param str topology: topology file
    :return: directory which contains the topology file
    :rtype: str
    """
    return os.path.dirname(topology_abspath(topology))


def get_snapshots(topology):
    """
    Return the paths of any snapshot topologies

    :param str topology: topology file
    :return: list of dicts containing snapshot topologies
    :rtype: list
    """
    snapshots = []
    snap_dir = os.path.join(topology_dirname(topology), 'snapshots')
    if os.path.exists(snap_dir):
        snaps = os.listdir(snap_dir)
        for directory in snaps:
            snap_top = os.path.join(snap_dir, directory, 'topology.net')
            if os.path.exists(snap_top):
                snapshots.append({'file': snap_top,
                                  'snapshot': True})
    return snapshots


def name(topology_file, topology_name=None):
    """
    Calculate the name to save the converted topology as using either either
    a specified name or the directory name of the current project

    :param str topology_file: Topology filename
    :param topology_name: Optional topology name (Default: None)
    :type topology_name: str or None
    :return: new topology name
    :rtype: str
    """
    if topology_name is not None:
        logging.debug('topology name supplied')
        topo_name = topology_name
    else:
        logging.debug('topology name not supplied')
        topo_name = os.path.basename(topology_dirname(topology_file))
    return topo_name


def snapshot_name(topo_name):
    """
    Get the snapshot name

    :param str topo_name: topology file location. The name is taken from the
                          directory containing the topology file using the
                          following format: topology_NAME_snapshot_DATE_TIME
    :return: snapshot name
    :raises ConvertError: when unable to determine the snapshot name
    """
    topo_name = os.path.basename(topology_dirname(topo_name))
    snap_re = re.compile('^topology_(.+)(_snapshot_)(\d{6}_\d{6})$')
    result = snap_re.search(topo_name)

    if result is not None:
        snap_name = result.group(1) + '_' + result.group(3)
    else:
        raise ConvertError('Unable to get snapshot name')

    return snap_name


def save(output_dir, converter, json_topology, snapshot, quiet):
    """
    Save the converted topology

    :param str output_dir: Output Directory
    :param Converter converter: Converter instance
    :param JSONTopology json_topology: JSON topology layout
    :param bool snapshot: Is this a snapshot?
    :param bool quiet: No console printing
    """
    try:
        old_topology_dir = topology_dirname(converter.topology)

        if output_dir:
            output_dir = os.path.abspath(output_dir)
        else:
            output_dir = os.getcwd()

        topology_name = json_topology.name
        topology_files_dir = os.path.join(output_dir, topology_name + '-files')

        if snapshot:
            snap_name = snapshot_name(converter.topology)
            output_dir = os.path.join(topology_files_dir, 'snapshots',
                                      snap_name)
            topology_files_dir = os.path.join(output_dir, topology_name +
                                              '-files')

        # Prepare the directory structure
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Move the dynamips config files to the new topology folder
        config_err = copy_configs(converter.configs, old_topology_dir,
                                  topology_files_dir)

        # Copy any VPCS configurations to the the new topology
        copy_vpcs_configs(old_topology_dir, topology_files_dir)

        # Copy the topology images to the new topology
        copy_topology_image(old_topology_dir, output_dir)

        # Copy the instructions to the new topology folder
        if not snapshot:
            copy_instructions(old_topology_dir, output_dir)

        # Move the image files to the new topology folder
        image_err = copy_images(converter.images, old_topology_dir,
                                topology_files_dir)

        # Create the vbox working directories
        make_vbox_dirs(json_topology.get_vboxes(), output_dir, topology_name)

        # Create the qemu working directories
        make_qemu_dirs(json_topology.get_qemus(), output_dir, topology_name)

        if config_err:
            logging.warning('Some router startup configurations could not be '
                            'found to be copied to the new topology')

        if image_err:
            logging.warning('Some images could not be found to be copied to '
                            'the new topology')

        filename = '%s.gns3' % topology_name
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w') as file:
            json.dump(json_topology.get_topology(), file, indent=4,
                      sort_keys=True)
            if not snapshot and not quiet:
                print('Your topology has been converted and can found in:\n'
                      '     %s' % output_dir)
    except OSError as error:
        logging.error(error)


def copy_configs(configs, source, target):
    """
    Copy dynamips configs to converted topology

    :param configs: Configs to copy
    :param str source: Source topology directory
    :param str target: Target topology files directory
    :return: True when a config cannot be found, otherwise false
    :rtype: bool
    """
    config_err = False
    if len(configs) > 0:
        config_dir = os.path.join(target, 'dynamips', 'configs')
        os.makedirs(config_dir)
        for config in configs:
            old_config_file = os.path.join(source, config['old'])
            new_config_file = os.path.join(config_dir,
                                           os.path.basename(config['new']))
            if os.path.isfile(old_config_file):
                # Copy and rename the config
                shutil.copy(old_config_file, new_config_file)
            else:
                config_err = True
                logging.error('Unable to find %s' % config['old'])
    return config_err


def copy_vpcs_configs(source, target):
    """
    Copy any VPCS configs to the converted topology

    :param str source: Source topology directory
    :param str target: Target topology files directory
    """
    # Prepare a list of files to copy
    vpcs_files = glob.glob(os.path.join(source, 'configs', '*.vpc'))
    vpcs_hist = os.path.join(source, 'configs', 'vpcs.hist')
    vpcs_config_path = os.path.join(target, 'vpcs', 'multi-host')
    if os.path.isfile(vpcs_hist):
        vpcs_files.append(vpcs_hist)
    # Create the directory tree
    if len(vpcs_files) > 0:
        os.makedirs(vpcs_config_path)
    # Copy the files
    for old_file in vpcs_files:
        new_file = os.path.join(vpcs_config_path, os.path.basename(old_file))
        shutil.copy(old_file, new_file)


def copy_topology_image(source, target):
    """
    Copy any images of the topology to the converted topology

    :param str source: Source topology directory
    :param str target: Target Directory
    """
    files = glob.glob(os.path.join(source, '*.png'))

    for file in files:
        shutil.copy(file, target)


def copy_images(images, source, target):
    """
    Copy images to converted topology

    :param images: Images to copy
    :param source: Old Topology Directory
    :param target: Target topology files directory
    :return: True when an image cannot be found, otherwise false
    :rtype: bool
    """
    image_err = False
    if len(images) > 0:
        images_dir = os.path.join(target, 'images')
        os.makedirs(images_dir)
        for image in images:
            if os.path.isabs(image):
                old_image_file = image
            else:
                old_image_file = os.path.join(source, image)

            new_image_file = os.path.join(images_dir,
                                          os.path.basename(image))
            if os.path.isfile(os.path.abspath(old_image_file)):
                shutil.copy(old_image_file, new_image_file)
            else:
                image_err = True
                logging.error('Unable to find %s' % old_image_file)
    return image_err


def copy_instructions(source_project, dest_project):
    old_instructions = os.path.join(source_project, 'instructions')
    new_instructions = os.path.join(dest_project, 'instructions')

    if os.path.exists(old_instructions):
        try:
            shutil.copytree(old_instructions, new_instructions)
        except shutil.Error as error:
            raise ConvertError('Error copying instructions', error)


def make_vbox_dirs(max_vbox_id, output_dir, topology_name):
    """
    Create VirtualBox working directories if required

    :param int max_vbox_id: Number of directories to create
    :param str output_dir: Output directory
    :param str topology_name: Topology name
    """
    if max_vbox_id is not None:
        for i in range(1, max_vbox_id + 1):
            vbox_dir = os.path.join(output_dir, topology_name + '-files',
                                    'vbox', 'vm-%s' % i)
            os.makedirs(vbox_dir)


def make_qemu_dirs(max_qemu_id, output_dir, topology_name):
    """
    Create Qemu VM working directories if required

    :param int max_qemu_id: Number of directories to create
    :param str output_dir: Output directory
    :param str topology_name: Topology name
    """
    if max_qemu_id is not None:
        for i in range(1, max_qemu_id + 1):
            qemu_dir = os.path.join(output_dir, topology_name + '-files',
                                    'qemu', 'vm-%s' % i)
            os.makedirs(qemu_dir)


if __name__ == '__main__':
    main()
