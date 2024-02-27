import numpy as np
import glob
import os
import subprocess
import traceback

class AztecPath():
    def __init__(self):
        try:
            self.macanaPath = os.environ['MACANA_HOME']
        except:
            self.macanaPath = os.environ['HOME']+'/aztec_c++/'
        if self.macanaPath[-1] != '/':
            self.macanaPath = self.macanaPath+'/'
        self.pyPath = self.macanaPath+'aztec_py/'
        print 'mancaPath = ', self.macanaPath
        print 'pyPath = ', self.pyPath
        try:
            self.rawDataPath = os.environ['MACANA_RAWDATA_PATH']
        except:
            self.rawDataPath = '/data_lmt/aztec/'
        try:
            self.bsPath = os.environ['MACANA_BS_PATH']
        except:
            self.bsPath = './lmt/raw_data/'
        try:
            self.mapPath = os.environ['MACANA_MAP_PATH']
        except:
            self.mapPath = './lmt/reduced_maps/'
        if self.rawDataPath[-1] != '/':
            self.rawDataPath = self.rawDataPath+'/'
        if self.bsPath[-1] != '/':
            self.bsPath = self.bsPath+'/'
        if self.mapPath[-1] != '/':
            self.mapPath = self.mapPath+'/'

        if self.mapPath[0] == '.':
            self.mapPath = self.macanaPath+self.mapPath
        print 'RawDataPath = ', self.rawDataPath
        print 'BsPath = ', self.bsPath
        print 'MapPath = ', self.mapPath

    def toMap(self, filename=False):
        if(filename == False):
            return False
        dataPath = filename.partition('aztec_')[0]
        filename = filename.partition(dataPath)[2]
        mapFilename = filename.partition(".nc")[0]+"_map.nc"
        mapFilename = filename.split("_")[2]+"_map.nc"
        plotFilename = filename.split("_")[2]+"_map.png"
        return filename,mapFilename,plotFilename
