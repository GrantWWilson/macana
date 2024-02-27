#python program to extract the best-fit focus from a set of macana-produced
#map files in .nc format
#Grant Wilson - 17 October, 2014

import netCDF4
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
import glob
import os
from AztecPath import AztecPath
from AztecRunPointing import AztecRunPointing
from AztecMapFile import AztecMapFile
import traceback
import sys

class AztecRunFocus():
    def run(self, argv, filelist=False,obsNumArg=False,plot_filename=False):
        print "AztecRunFocus filelist = ", filelist

        aztecPath = AztecPath()
        self.msg = ''

        # run pointing and build reduced maps list
        aztec = AztecRunPointing();
        try:
            res = aztec.run(sys.argv,filelist,obsNumArg)
        except:
            traceback.print_exc()
            return -1
          
        if res < 0:
            self.msg = 'AztecRunFocus: failed in AztecRunPointing'
            return res

        nfiles = len(filelist)

        M2x = np.zeros(nfiles)
        M2y = np.zeros(nfiles)
        M2z = np.zeros(nfiles)
        amp = np.zeros(nfiles)
        amp_err = np.zeros(nfiles)
        offset_x = np.zeros(nfiles)
        offset_y = np.zeros(nfiles)
        fwhmx = np.zeros(nfiles)
        fwhmx_err = np.zeros(nfiles)
        fwhmy = np.zeros(nfiles)
        fwhmy_err = np.zeros(nfiles)
        
        titleString = ''

        print 'nfiles = ', nfiles

        #run through the files
        for i in range(nfiles):
            filename,mapFilename,tmpFilename = aztecPath.toMap(filelist[i])
            mapFilename = ('aztec_map_%d.nc'%i)
            ncfile = netCDF4.Dataset(aztecPath.mapPath+mapFilename,'r')
            M2x[i] = getattr(ncfile,'M2XReq')
            M2y[i] = getattr(ncfile,'M2YReq')
            M2z[i] = getattr(ncfile,'M2ZReq')
            signal = ncfile.variables['signal']
            amp[i] = signal.amplitude
            amp_err[i] = signal.amplitude_err
            offset_x[i] = signal.offset_x
            offset_y[i] = signal.offset_y
            fwhmx[i] = signal.FWHM_x
            fwhmx_err[i] = signal.FWHM_x_err
            fwhmy[i] = signal.FWHM_y
            fwhmy_err[i] = signal.FWHM_y_err
            ncfile.close()

        #check for bad fits as an error check
        #added 10/30/14 by GW
        goodfit = np.zeros(nfiles)
        for i in range(nfiles):
            if (fwhmx[i]>5 and fwhmx[i]<20 and fwhmy[i]>5 and fwhmy[i]<20):
                goodfit[i] = 1
        w = np.where(goodfit == 1.)
        ngood = len(w[0])
        goodindex = w[0]
        M2x = M2x[goodindex]
        M2y = M2y[goodindex]
        M2z = M2z[goodindex]
        amp = amp[goodindex]
        amp_err = amp_err[goodindex]
        fwhmx = fwhmx[goodindex]
        fwhmx_err = fwhmx_err[goodindex]
        fwhmy = fwhmy[goodindex]
        fwhmy_err = fwhmy_err[goodindex]

        print 'ngood = ', ngood
        if (ngood <= 1):
            self.msg = "Not enough good fits in these files."
            M2fit = M2z
            self.M2txt = 'M2z'
            return -2

        #figure out which of M2x, M2y, and M2z are changing
        dx=M2x.max()-M2x.min()
        dy=M2y.max()-M2y.min()
        dz=M2z.max()-M2z.min()
        if (dx == dy and dx == dz and dx == 0):
            #nothing's changing, an error should be thrown
            self.msg = "M2 offsets are not changing in these files."
            return -2
        if (dx != 0):
            if (dy != 0 or dz != 0):
                #more than one offset changing, throw an error
                self.msg = "More than one M2 offset is changing in these files."
                return -2
            M2fit = M2x
            self.M2txt = 'M2x'
        elif (dy != 0):
            if (dx != 0 or dz != 0):
                #more than one offset changing, throw an error
                self.msg = "More than one M2 offset is changing in these files."
                return -2
            M2fit = M2y
            self.M2txt = 'M2y'
        elif (dz != 0):
            if (dx != 0 or dy != 0):
                #more than one offset changing, throw an error
                self.msg = "More than one M2 offset is changing in these files."
                return -2
            M2fit = M2z
            self.M2txt = 'M2z'

        print 'M2txt = ', self.M2txt
        print 'M2x = ', M2x
        print 'M2y = ', M2y
        print 'M2z = ', M2z
        print 'Amp = ', amp

        #fit the amplitudes to a quadratic
        #changed fitting approach and added error calculation - GW 10/30/14
        def func(x, a0, a1, a2):
            return a2 + a1*x + a0*x**2
        w = 1./amp_err
        yp = amp/amp_err
        x = M2fit
        npts = len(x)
        M = np.zeros((npts,3))
        for i in range(npts):
            M[i,2] = 1./amp_err[i]
            M[i,1] = x[i]/amp_err[i]
            M[i,0] = x[i]**2/amp_err[i]
        Mt = M.transpose()
        alpha = np.dot(Mt,M)
        alphai = np.linalg.inv(alpha)
        b = np.dot(Mt,yp)
        p = np.dot(alphai,b)
        cov = alphai
        a = p
        #a,cov = curve_fit(func,M2fit,amp,sigma=amp_err,absolute_sigma=False)
        x = np.linspace(M2fit.min()-0.5,M2fit.max()+0.5,100)
        y = a[2] + a[1]*x + a[0]*x**2
        xp = -a[1]/(2.*a[0])
        yp = a[2] + a[1]*xp + a[0]*xp**2
        xperr = np.sqrt((1./(2.*a[0]))**2*cov[1,1] + (a[1]/(2.*a[0]**2))**2*cov[0,0])

        if self.M2txt == 'M2x':
            self.M2XOffset = xp
            self.M2YOffset = M2y.max()
            self.M2ZOffset = M2z.max()
        elif self.M2txt == 'M2y':
            self.M2XOffset = M2x.max()
            self.M2YOffset = xp
            self.M2ZOffset = M2z.max()
        elif self.M2txt == 'M2z':
            self.M2XOffset = M2x.max()
            self.M2YOffset = M2y.max()
            self.M2ZOffset = xp

        self.Receiver = aztec.Receiver
        self.ObsPgm = aztec.ObsPgm

        #make some plots
        if plot_filename:
            plt.clf()
            plt.axes([0, 0, 1, 1])
            plt.plot(M2fit,amp,'o')
            plt.errorbar(M2fit,amp,yerr=amp_err*5,fmt='o')
            plt.plot(x,y)
            plt.plot([xp,xp],[0,yp*2],'--')
            plt.ylim(0,amp.max()*1.2)
            ax = plt.gca()
            xx = x.min()+(x.max()-x.min())/3
            yy = 0+amp.max()*1.2/3
            boxstr = 'Peak Location (mm): '+"%.3f"%xp + '+/-%.3f'%xperr
            ax.text(xx,yy,boxstr,style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
            plt.xlabel(self.M2txt+'-position [mm]')
            plt.ylabel('Peak Amplitude [Jy]')
            plt.title(obsNumArg)

            #for the little plots, sort by the parameter that is being fit
            si = np.argsort(M2fit)
            print si

            xx = 0
            dx = 1.0/nfiles
            doff_x = doff_y = max(abs(offset_x)+abs(offset_y))+10
            for i in si:
                filename,mapFilename,tmpFilename = aztecPath.toMap(filelist[i])
                mapFilename = ('aztec_map_%d.nc'%i)
                mapFile = AztecMapFile(mapFilename, aztecPath.mapPath)
                xx = i*dx
                plt.axes([xx, 0, dx, dx])
                plt.gca().get_xaxis().set_visible(False);
                plt.gca().get_yaxis().set_visible(False);
                plt.imshow(mapFile.z, extent=[mapFile.x.min(), mapFile.x.max(), mapFile.y.min(), mapFile.y.max()])
                plt.xlim(-doff_x+offset_x[i],doff_x+offset_x[i])
                plt.ylim(-doff_y+offset_y[i],doff_y+offset_y[i])
                plt.title(str(mapFile.obsNum) +': ' +str(round(mapFile.amplitude,3)) +' ' +mapFile.amplitude_units, fontsize=10)

            try:
                os.remove(plot_filename)
            except:
                pass
        
            plt.savefig(plot_filename, bbox_inches='tight')
        

        return 0
