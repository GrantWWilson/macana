import netCDF4
import os
import numpy as np
import math
import matplotlib.pyplot as plt

class AztecDataFile():
        
    def __init__(self,filename):

        self.filename = filename
        self.Receiver = ''
        self.Backend = ''
        self.ObsPgm = ''

        if os.path.isfile(self.filename):
            self.nc = netCDF4.Dataset(self.filename)
            self.Receiver = ''.join(self.nc.variables['Header.Dcs.Receiver'][:]).strip()
            self.Backend = 'AztecBackend'
            self.ObsPgm = ''.join(self.nc.variables['Header.Dcs.ObsPgm'][:]).strip()
            self.nc.close()

        else:
            print self.filename+' does not exist'

    

