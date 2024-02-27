import netCDF4
import os
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
##plt.ion()

class AztecMapPlot():
        
    def plot(self,mapFile=False,plot_filename=False):

        print 'plot_filename = ', plot_filename

        if plot_filename:
            plt.cla()
            plt.clf()
            plt.imshow(mapFile.z, extent=[mapFile.x.min(), mapFile.x.max(), mapFile.y.min(), mapFile.y.max()])
            plt.colorbar()
            self.dd = (mapFile.y.max()-mapFile.y.min())/2
#            plt.axis([-self.dd,self.dd,-self.dd,self.dd])
            plt.xlabel('Azimuth (arcsec)')
            plt.ylabel('Elevation (arcsec)')
            plt.grid()
#            plt.title('%s -- %s -- %s'%(mapFile.sourceName, mapFile.dateStr, mapFile.obsNum))
            plt.title('%s -- %s'%(mapFile.sourceName, mapFile.obsNum))

            self.textstr = 'C1 Offset: ' +str(round(mapFile.offset_x,3)) +' +/- ' +str(round(mapFile.offset_x_err,3)) +' ' +mapFile.offset_x_units +'\n'
            self.textstr = self.textstr + 'C2 Offset: ' +str(round(mapFile.offset_y,3)) +' +/- ' +str(round(mapFile.offset_y_err,3)) +' ' +mapFile.offset_y_units + '\n'
            self.textstr = self.textstr + 'C1 FWHM: ' +str(round(mapFile.fwhm_x,3)) +' +/- ' +str(round(mapFile.fwhm_x_err,3)) +' ' +mapFile.fwhm_x_units  + '\n'
            self.textstr = self.textstr + 'C2 FWHM: ' +str(round(mapFile.fwhm_y,3)) +' +/- ' +str(round(mapFile.fwhm_y_err,3)) +' ' +mapFile.fwhm_y_units  + '\n'
            self.textstr = self.textstr + 'Beam Amplitude: ' +str(round(mapFile.amplitude,3)) +' +/- ' +str(round(mapFile.amplitude_err,3)) +' ' +mapFile.amplitude_units
            self.xx = -(mapFile.x.max()-mapFile.x.min())/3
            self.yy = -(mapFile.y.max()-mapFile.y.min())/3

            textColor = 'yellow'
            faceColor = 'wheat'
            alphaVal = 0.5
            fontSize = 12
            if mapFile.offset_x > mapFile.x.min() and mapFile.offset_x < mapFile.x.max():
                plt.axvline(mapFile.offset_x, linestyle='--', color="white")
            else:
                x_err = True
                self.textstr = self.textstr + '\n    ERROR IN C1 OFFSET: OUTSIDE MAP'
                textColor = 'red'
                faceColor = 'wheat'
                alphaVal = 1.0
                fontSize = 16
            if mapFile.offset_y > mapFile.y.min() and mapFile.offset_y < mapFile.y.max():
                plt.axhline(mapFile.offset_y, linestyle='--', color="white")
            else:
                self.textstr = self.textstr + '\n    ERROR IN C2 OFFSET: OUTSIDE MAP'
                textColor = 'red'
                faceColor = 'wheat'
                alphaVal = 1.0
                fontSize = 16

            self.props = dict(boxstyle='round', facecolor=faceColor, alpha=alphaVal)
            plt.text(0, self.yy, self.textstr, fontsize=fontSize, bbox=self.props, color=textColor, horizontalalignment='center')
            ##plt.show()

            try:
                os.remove(plot_filename)
            except:
                pass
            
            plt.savefig(plot_filename, bbox_inches='tight')
        

        return 0
    
    

