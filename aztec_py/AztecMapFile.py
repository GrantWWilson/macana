import netCDF4
import os
import numpy as np
import math

class AztecMapFile():
        
    def __init__(self,filename,path=''):

        self.res = 0
        self.offset_x = 0
        self.offset_y = 0
        self.filename = path+filename

        if os.path.isfile(self.filename):
            self.nc = netCDF4.Dataset(self.filename)
            self.sourceName = getattr(self.nc,'source')
            self.M2x = getattr(self.nc,'M2XReq')
            self.M2y = getattr(self.nc,'M2YReq')
            self.M2z = getattr(self.nc,'M2ZReq')
            self.obsNum = getattr(self.nc,'ObsNum')
            self.x = self.nc.variables['rowCoordsPhys'][:]*3600*180/math.pi
            self.y = self.nc.variables['colCoordsPhys'][:]*3600*180/math.pi
            self.z_var = self.nc.variables['signal']
            self.offset_x = self.z_var.getncattr('offset_x')
            self.offset_x_err = self.z_var.getncattr('offset_x_err')
            self.offset_x_units = self.z_var.getncattr('offset_x_units')
            self.offset_y = self.z_var.getncattr('offset_y')
            self.offset_y_err = self.z_var.getncattr('offset_y_err')
            self.offset_y_units = self.z_var.getncattr('offset_y_units')
            self.fwhm_x = self.z_var.getncattr('FWHM_x')
            self.fwhm_x_err = self.z_var.getncattr('FWHM_x_err')
            self.fwhm_x_units = self.z_var.getncattr('FWHM_x_units')
            self.fwhm_y = self.z_var.getncattr('FWHM_y')
            self.fwhm_y_err = self.z_var.getncattr('FWHM_y_err')
            self.fwhm_y_units = self.z_var.getncattr('FWHM_y_units')
            self.amplitude = self.z_var.getncattr('amplitude')
            self.amplitude_err = self.z_var.getncattr('amplitude_err')
            self.amplitude_units = self.z_var.getncattr('amplitude_units')
            self.z = self.z_var[:]
            self.z = np.clip(self.z, -self.amplitude_err, 1.05*self.amplitude)
            self.z = np.rot90(self.z)

            self.filename = self.filename[self.filename.rfind('/')+1:]
#            self.dateStr = self.filename.partition("aztec_")[2].partition("_")[0]
#            self.obsNum = self.filename.partition(self.dateStr+"_")[2].partition("_")[0]
            self.nc.close()

        else:
            print self.filename+' does not exist'
            self.res = -1
    
    

