Welcome to gns3-converter's documentation!
==========================================

GNS3 Converter is designed to convert old ini-style GNS3 topologies (<=0.8.7)
to the newer version v1+ JSON format for use in GNS3 v1+

The converter should convert all IOS and Cloud Devices to the new format, but
currently will not convert VirtualBox and QEMU nodes.

Due to the change in implementation of VPCS nodes these will be converted to
cloud objects.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   usage

Development
===========
If you find a bug in gns3-converter please feel free to report it to the issue
tracker listed below. If the problem occurs with a particular topology, please
include the topology with the issue report.

* Public Repository: https://github.com/dlintott/gns3-converter
* Issue Tracker: https://github.com/dlintott/gns3-converter/issues
* License: GPL-3+

