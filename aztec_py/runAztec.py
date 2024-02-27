#!/usr/bin/env python


import sys
import traceback
from AztecRunPointing import AztecRunPointing
from AztecRunFocus import AztecRunFocus

wwwPath = './'
plotFilename = 'aztec.png'
obsNumArg = ''

doFocus = False;

if len(sys.argv) >= 2 and (sys.argv[1].startswith('f')):
    doFocus = True


if doFocus:
    print "aztec focus"
    filelist=['/data_lmt/aztec/aztec_2014-02-20_016514_00_0001.nc', '/data_lmt/aztec/aztec_2014-02-21_016623_00_0001.nc', '/data_lmt/aztec/aztec_2014-02-21_016625_00_0001.nc', '/data_lmt/aztec/aztec_2014-03-28_017941_00_0001.nc']
    filelist=['/data_lmt/aztec/aztec_2014-11-05_027451_00_0001.nc','/data_lmt/aztec/aztec_2014-11-05_027452_00_0001.nc','/data_lmt/aztec/aztec_2014-11-05_027453_00_0001.nc','/data_lmt/aztec/aztec_2014-11-05_027454_00_0001.nc','/data_lmt/aztec/aztec_2014-11-05_027455_00_0001.nc']
    filelist=['/data_lmt/aztec/aztec_2014-11-10_027942_00_0001.nc','/data_lmt/aztec/aztec_2014-11-10_027943_00_0001.nc','/data_lmt/aztec/aztec_2014-11-10_027944_00_0001.nc','/data_lmt/aztec/aztec_2014-11-10_027945_00_0001.nc','/data_lmt/aztec/aztec_2014-11-10_027946_00_0001.nc']
    aztec = AztecRunFocus();
    try:
        res = aztec.run(sys.argv,filelist,obsNumArg,wwwPath+plotFilename)
    except:
        print 'AztecRunFocus failed'
        traceback.print_exc()
        sys.exit

    if res < 0:
        if res == -2:
            print 'AztecRunPointing in Focus failed'
        else:
            print 'AztecRunFocus failed'
        sys.exit
    
    # set focus
    print 'm2x = ', aztec.M2XOffset
    print 'm2y = ', aztec.M2YOffset
    print 'm2z = ', aztec.M2ZOffset

#pointing
else:
    print "aztec pointing"
    filelist=['/data_lmt/aztec/aztec_2014-11-02_027167_00_0001.nc']
    filelist=['/data_lmt/aztec/aztec_2014-11-02_027181_00_0001.nc']
    filelist=['/data_lmt/aztec/aztec_2014-03-28_017941_00_0001.nc']
    filelist=['/data_lmt/aztec/aztec_2014-11-10_027946_00_0001.nc']
    aztec = AztecRunPointing();
    try:
        res = aztec.run(sys.argv,filelist,obsNumArg,wwwPath+plotFilename)
    except:
        print 'AztecRunPointing failed'
        traceback.print_exc()
        sys.exit

    if res < 0:
        print 'AztecRunPointing failed'
        sys.exit

    # set pointing
    print 'az_offset = ', aztec.offset_x
    print 'el_offset = ', aztec.offset_y
