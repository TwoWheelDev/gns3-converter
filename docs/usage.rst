Using gns3-converter
********************

.. argparse::
    :module: gns3converter.main
    :func: setup_argparse
    :prog: gns3-converter

Example
=======
By default the converted topology will be output to a sub-directory of the
current working directory. The only argument that must be supplied, is the
topology file to be converted.

To convert a topology just type:

::

    gns3-converter topology1.net

If the relevant are also present alongside the topology file these will be
copied to the new topology and renamed accordingly.

If you wish to output the converted topology to a different destination this
can be done using the -o, --output argument like this:

::

    gns3-converter -o ../output topology.net

or

::

    gns3-converter --output ../output topology.net

