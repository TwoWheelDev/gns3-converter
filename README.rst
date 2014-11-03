gns3-converter: GNS3 Topology Converter
***************************************

.. image:: https://travis-ci.org/dlintott/gns3-converter.svg?branch=master
    :target: https://travis-ci.org/dlintott/gns3-converter

.. image:: https://img.shields.io/coveralls/dlintott/gns3-converter/master.svg
    :target: https://coveralls.io/r/dlintott/gns3-converter?branch=master 

.. image:: https://img.shields.io/pypi/v/gns3-converter.svg
    :target: https://pypi.python.org/pypi/gns3-converter

.. image:: https://img.shields.io/pypi/l/gns3-converter.svg
    :target: https://pypi.python.org/pypi/gns3-converter

GNS3 Converter is designed to convert old ini-style GNS3 topologies (<=0.8.7)
to the newer version v1+ JSON format for use in GNS3 v1+

The converter will convert all IOS, Cloud and VirtualBox devices to the new
format. It will also convert all QEMU based devices (QEMU VM, ASA, PIX, JUNOS &
IDS). VPCS nodes will be converted to cloud devices due to lack of information
the 0.8.7 topology files.

For topologies containing snapshots, the snapshots will also be converted to
the new format automatically.

Documentation
=============
Current documentation for gns3-converter can be found here:
 http://gns3-converter.readthedocs.org/en/latest/