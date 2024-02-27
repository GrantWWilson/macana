from matplotlib import pyplot as plt
from lmfit import Parameters, minimize, fit_report
import netCDF4
import os
import numpy as np
import math

class AztecNoiseRealizationFile():
    def __init__(self,filename,path=''):

        #check if file exists and open if it does
        self.filename = path+filename
        if(os.path.isfile(self.filename)):
            self.nc = netCDF4.Dataset(self.filename)
        else:
            print self.filename+' does not exist'
        
    def getAll(self):
        self.getNoiseMap()
        self.getFilteredNoiseMap()
        self.getWeightMap()
        self.getFilteredWeightMap()
        self.getXCoordsAbs()
        self.getYCoordsAbs()
        self.getRowCoordsPhys()
        self.getColCoordsPhys()
        self.getHistBins()
        self.getHistVals()
        self.getHistBinsFilteredNoise()
        self.getHistValsFilteredNoise()

    def getUnfilteredMaps():
        self.getNoiseMap()
        self.getWeightMap()
        self.getKernelMap()
        self.getXCoordsAbs()
        self.getYCoordsAbs()
        self.getRowCoordsPhys()
        self.getColCoordsPhys()
        self.getHistBins()
        self.getHistVals()

    def getFilteredMaps():
        self.getFilteredNoiseMap()
        self.getFilteredWeightMap()
        self.getFilteredKernelMap()
        self.getXCoordsAbs()
        self.getYCoordsAbs()
        self.getRowCoordsPhys()
        self.getColCoordsPhys()
        self.getHistBinsFilteredNoise()
        self.getHistValsFilteredNoise()

    def getNoiseMap(self):
        self.signal = self.nc.variables['signal'][:]
        
    def getFilteredNoiseMap(self):
        self.filteredNoise = self.nc.variables['filteredNoise'][:]

    def getWeightMap(self):
        self.weight = self.nc.variables['weight'][:]
        
    def getFilteredWeightMap(self):
        self.filteredWeight = self.nc.variables['filteredWeight'][:]

    def getKernelMap(self):
        self.kernel = self.nc.variables['kernel'][:]
        
    def getFilteredKernelMap(self):
        self.filteredKernel = self.nc.variables['filteredKernel'][:]

    def getXCoordsAbs(self):
        self.xCoordsAbs = self.nc.variables['xCoordsAbs'][:]

    def getYCoordsAbs(self):
        self.yCoordsAbs = self.nc.variables['yCoordsAbs'][:]

    def getRowCoordsPhys(self):
        self.rowCoordsPhys = self.nc.variables['rowCoordsPhys'][:]

    def getColCoordsPhys(self):
        self.colCoordsPhys = self.nc.variables['colCoordsPhys'][:]

    def getHistBins(self):
        self.histBins = self.nc.variables['histBins'][:]

    def getHistVals(self):
        self.histVals = self.nc.variables['histVals'][:]

    def getHistBinsFilteredNoise(self):
        self.histBinsFilteredNoise = self.nc.variables['histBins_filteredNoise'][:]

    def getHistValsFilteredNoise(self):
        self.histValsFilteredNoise = self.nc.variables['histVals_filteredNoise'][:]


    def plotHistogram(self, normalize=0, log=0, legend=0, filtered=0):
        if(not filtered):
            try: 
                self.histBins
            except:
                self.getHistBins()
                self.getHistVals()
            plotbins = self.histBins
            plotvals = self.histVals
        else:
            try: 
                self.histBinsFilteredNoise
            except:
                self.getHistBinsFilteredNoise()
                self.getHistValsFilteredNoise()
            plotbins = self.histBinsFilteredNoise
            plotvals = self.histValsFilteredNoise

        if(normalize):
            plotvals = plotvals/plotvals.max()

        plt.ion()

        plt.step(plotbins*1000., plotvals, label=self.filename)
        if(log): plt.yscale('log')
        plt.xlabel('Noise [mJy]')
        plt.ylabel('Counts')
        plt.title(self.filename)
        if(legend): plt.legend()
        plt.show()

    def clf(self):
        plt.clf()

    def closeNC(self):
        self.nc.close()

    def fitHistogram(self, filtered=0):
        if(not filtered):
            try: 
                self.histBins
            except:
                self.getHistBins()
                self.getHistVals()
            fitbins = self.histBins
            fitvals = self.histVals
        else:
            try: 
                self.histBinsFilteredNoise
            except:
                self.getHistBinsFilteredNoise()
                self.getHistValsFilteredNoise()
            fitbins = np.array(self.histBinsFilteredNoise)
            fitvals = np.array(self.histValsFilteredNoise)
            
        params = Parameters()
        params.add('amp',value=fitvals.max())
        params.add('sig',value=0.00011)
        params.add('offset',value=0.0001)
        ws = np.where(fitvals >= 0.01*fitvals.max())
        ws = ws[0]
        out = minimize(resid, params, args=(fitbins[ws],fitvals[ws],100.))
        self.fittedHistogramSigma = params['sig'].value*1.e3
        self.fittedHistogramAmplitude = params['amp'].value
        self.fittedHistogramOffset = params['offset'].value*1.e3


def resid(params, x, y, sigma):
    amp = params['amp'].value
    sig = params['sig'].value
    offset = params['offset'].value
    model = amp*np.exp(-(x-offset)**2/(2.*sig**2))
    return (y-model)/sigma



