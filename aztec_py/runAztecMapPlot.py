#!/usr/bin/env python


import sys
from AztecPath import AztecPath
from AztecMapFile import AztecMapFile
from AztecMapPlot import AztecMapPlot

#filename = "~/lmt/reduced_maps/aztec_2014-03-28_017941_00_0001_maps.nc"

if len(sys.argv) >= 2:
    aztecMapFile = AztecMapFile(sys.argv[1])
    aztecMapPlot = AztecMapPlot()
    aztecMapPlot.plot(aztecMapFile, 'aztec.png')
else:
    print 'must provide map file name'

