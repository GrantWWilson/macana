import netCDF4
import os
import numpy as np

class AztecPointSource():
    def __init__(self,filename,path='',number=0):

        self.res = 0
        self.filename = path+filename
        if (os.path.isfile(self.filename) == 0):
            raise ValueError(self.filename+' does not exist')

        self.nc = netCDF4.Dataset(self.filename)
        self.varname = 'pointSource_'+str(number)
        self.nSources = len(self.nc.dimensions['nSources'])
        
        if (self.nSources == 0):
            raise ValueError("There are no point sources detected.")

        if (self.nSources < number):
            raise ValueError("There are only "+str(self.nSources)+
                             " sources in this file.")

        #read in the pointsource imaging data and coordinates
        self.sv = self.nc.variables[self.varname]
        self.signal = self.sv[:]
        self.rcp = self.nc.variables[self.varname+'_rcp'][:]
        self.ccp = self.nc.variables[self.varname+'_ccp'][:]
        
        self.centerRaAbs = self.sv.centerRaAbs
        self.centerDecAbs = self.sv.centerDecAbs
        self.centerRaPhys = self.sv.centerRaPhys
        self.centerDecPhys = self.sv.centerDecPhys
        self.centerXPos = self.sv.centerXPos
        self.centerYPos = self.sv.centerYPos
        self.raCentroid = self.sv.raCentroid
        self.decCentroid = self.sv.decCentroid
        self.raPhysCentroid = self.sv.raPhysCentroid
        self.decPhysCentroid = self.sv.decPhysCentroid
        self.xCentroid = self.sv.xCentroid
        self.yCentroid = self.sv.yCentroid
        self.centerFlux = self.sv.centerFlux
        self.centerNoise = self.sv.centerNoise
        self.centerS2N = self.sv.centerS2N
        self.dc_offset = self.sv.dc_offset
        self.dc_offset_err = self.sv.dc_offset_err
        self.dc_offset_units = self.sv.dc_offset_units
        self.amplitude = self.sv.amplitude
        self.amplitude_err = self.sv.amplitude_err
        self.amplitude_units = self.sv.amplitude_units
        self.FWHM_x = self.sv.FWHM_x
        self.FWHM_x_err = self.sv.FWHM_x_err
        self.FWHM_x_units = self.sv.FWHM_x_units
        self.FWHM_y = self.sv.FWHM_y
        self.FWHM_y_err = self.sv.FWHM_y_err
        self.FWHM_y_units = self.sv.FWHM_y_units
        self.offset_x = self.sv.offset_x
        self.offset_x_err = self.sv.offset_x_err
        self.offset_x_units = self.sv.offset_x_units
        self.offset_y = self.sv.offset_y
        self.offset_y_err = self.sv.offset_y_err
        self.offset_y_units = self.sv.offset_y_units
        self.pos_Angle = self.sv.pos_Angle
        self.pos_Angle_err = self.sv.pos_Angle_err
        self.pos_Angle_units = self.sv.pos_Angle_units
        self.pixelSize = self.sv.pixelSize
        self.centroidWin = self.sv.centroidWin
        self.parentMapFile = self.sv.parentMapFile
        
