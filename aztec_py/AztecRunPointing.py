from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
import glob
import os
import subprocess
import traceback
from time import gmtime, strftime, sleep
from AztecDataFile import AztecDataFile
from AztecPath import AztecPath
from AztecMapFile import AztecMapFile
from AztecMapPlot import AztecMapPlot

class AztecRunPointing():
    def run(self, argv, filelist=False,obsNumArg=False,plotFilename=False,autoGenFilename=False):
        print "AztecRunPointing filelist = ", filelist
        print argv 

        despikeSigma = False
        neigToCut = False
        approximateWeights = False

        l = len(argv)
        for i in range (0,l):
            a = argv[i]
            if a == "--DespikeSigma":
                if i+1 < l:
                    i = i+1
                    despikeSigma = '    <despikeSigma> %s </despikeSigma>\n'%argv[i]
            elif a == "--NeigToCut":
                if i+1 < l:
                    i = i+1
                    neigToCut = '    <neigToCut> %s </neigToCut>\n'%argv[i]
            elif a == "--ApproximateWeights":
                if i+1 < l:
                    i = i+1
                    approximateWeights = '    <approximateWeights> %s </approximateWeights>\n'%argv[i]
            
        aztecPath = AztecPath()

        # put filenames in apPoint.xml
        # read the template and output it
        try:
          fout = open(aztecPath.macanaPath+"apPoint.xml", "wt")
          with open(aztecPath.pyPath+"aztecApPoint.xml", "rt") as fin:
            for line in fin:
                if (despikeSigma != False) and (line.strip().startswith('<despikeSigma>')):
                    fout.write(despikeSigma)
                elif (neigToCut != False) and (line.strip().startswith('<neigToCut>')):
                    fout.write(neigToCut)
                elif (approximateWeights != False) and (line.strip().startswith('<approximateWeights>')):
                    fout.write(approximateWeights)
                else:
                    fout.write(line)

          # now put the different paths
          apRawDataPath = '    <rawDataPath>%s</rawDataPath>\n'%aztecPath.rawDataPath
          apBsPath = '    <bsPath>%s</bsPath>\n'%aztecPath.bsPath
          apMapPath = '    <mapPath>%s</mapPath>\n'%aztecPath.mapPath
          fout.write(apRawDataPath)
          fout.write(apBsPath)
          fout.write(apMapPath)
          
          # now put the files
          lenFilelist = len(filelist)
          fout.write('    <nFiles>%d</nFiles>\n'%lenFilelist)
          for i in range (0,lenFilelist):
              fout.write('    <f%d>\n'%i)
              filename,mapFilename,tmpFilename = aztecPath.toMap(filelist[i])
              if autoGenFilename == False:
                  mapFilename = ('aztec_map_%d.nc'%i)
              fout.write('      <bsName>aztec.bstats</bsName>\n')
              fout.write('      <fileName>%s</fileName>\n'%filename)
              fout.write('      <mapName>%s</mapName>\n'%mapFilename)
              fout.write('      <bsOffset_0>0.0</bsOffset_0>\n')
              fout.write('      <bsOffset_1>0.0</bsOffset_1>\n')
              fout.write('    </f%d>\n'%i)
          # now finish the file
          fout.write('  </observations>\n')
          fout.write('</analysis>\n')
          fout.close()
        except:
          print 'macana setup failed'
          traceback.print_exc()
          return -1

        print ''
        print '-------------- start macana --------------------'
        print '-------------- start macana --------------------'
        print '-------------- start macana --------------------'
        print '-------------- start macana --------------------'
        print ''

        # run macan
        res = subprocess.call(['./macana', 'apPoint.xml'], cwd = aztecPath.macanaPath)

        print ''
        print '-------------- end macana --------------------'
        print '-------------- end macana --------------------'
        print '-------------- end macana --------------------'
        print '-------------- end macana --------------------'
        print ''

        print 'macana status = ', res

        if res < 0:
          print 'macana failed'
          return res


        aztecDataFile = AztecDataFile(filelist[0])
        self.Receiver = aztecDataFile.Receiver
        self.ObsPgm = aztecDataFile.ObsPgm

        if lenFilelist == 1:
            print 'one data file'
            aztecMapFile = AztecMapFile(mapFilename, aztecPath.mapPath)
            self.offset_x = aztecMapFile.offset_x
            self.offset_y = aztecMapFile.offset_y
            self.offset_x_err = aztecMapFile.offset_x_err
            self.offset_y_err = aztecMapFile.offset_y_err
            self.fwhm_x = aztecMapFile.fwhm_x
            self.fwhm_y = aztecMapFile.fwhm_y
            
            if isinstance(plotFilename, basestring):
                print 'one plot file'
                aztecMapPlot = AztecMapPlot()
                res = aztecMapPlot.plot(aztecMapFile, plotFilename)

                if res < 0:
                    print 'aztecMapPlot failed'
                    return res
                
        elif lenFilelist > 1 and autoGenFilename == True:
            print 'multiple data files, auto generate plot files'
            aztecMapPlot = AztecMapPlot()
            for i in range (0,lenFilelist):
                filename,mapFilename,plotFilename = aztecPath.toMap(filelist[i])
                aztecMapFile = AztecMapFile(mapFilename, aztecPath.mapPath)
                res = aztecMapPlot.plot(aztecMapFile, aztecPath.mapPath+plotFilename)
                if res < 0:
                    print 'aztecMapPlot failed'
              

        return 0


    





