Using gns3-converter
********************

.. argparse::
    :module: gns3converter.main
    :func: setup_argparse
    :prog: gns3-converter

Example
=======
By default the converted topology will be output to the current working
directory.

To convert a topology from the folder containing the topology.net file just
type:

::

    gns3-converter

Alternatively you can specify a topology file to convert on the command line:

::

    gns3-converter ~/GNS3/Projects/CCNA_1/topology.net

If the relevant configs are also present alongside the topology file these will
be copied to the new topology and renamed accordingly.

If you wish to output the converted topology to a different destination this
can be done using the -o or --output argument like this:

::

    gns3-converter -o ../output

or

::

    gns3-converter --output ../output

The name of the converted topology is taken from the folder containing the
topology file. For example a topology in ~/GNS3/Projects/CCNA_1/topology.net
will be named CCNA_1.

It is also possible to specify a name for the new topology using the -n or
--name in the same way as specifying the output directory.