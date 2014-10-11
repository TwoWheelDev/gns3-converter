Welcome to gns3-converter's documentation!
==========================================

GNS3 Converter is designed to convert old ini-style GNS3 topologies (<=0.8.7)
to the newer version v1+ JSON format for use in GNS3 v1+

The converter will convert all IOS, Cloud and VirtualBox devices to the new
format. It will also convert all QEMU based devices (QEMU VM, ASA, PIX, JUNOS &
IDS). VPCS nodes will be converted to cloud devices due to lack of information
the 0.8.7 topology files.

For topologies containing snapshots, the snapshots will not currently be saved
until snapshots have been implemented in GNS3 v1

Contents:

.. toctree::
   :maxdepth: 2

   installation
   usage
   gns3converter

Development
===========
If you find a bug in gns3-converter please feel free to report it to the issue
tracker listed below. If the problem occurs with a particular topology, please
include the topology with the issue report.

* Public Repository: https://github.com/dlintott/gns3-converter
* Issue Tracker: https://github.com/dlintott/gns3-converter/issues
* License: GPL-3+
