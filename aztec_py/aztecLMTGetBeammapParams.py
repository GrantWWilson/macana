# NAME: aztecLMTGetBeammapParams

# PURPOSE: 
# generates set of interpolated values for 5 parameters for aztec
# observations made on LMT, and optionally their
# errors. For observations bracketed by
# beammaps, a linear interpolation is used, for observations near a
# beammap and not bracketed, values from that beammap are used, for
# observations on nights where no good beammaps exist, the median
# value of the 5 parameters is used. 
# In each case these values are compared to the model prediction.
# If the model looks reasonably good, the model is used in place
# of the 

# This procedure generates a set of values for the five parameters
# used in calibrating the AzTEC observation on the LMT.  Because
# of the elevation dependence of the gain this model is a bit complex.
# See ray:/data/wilson/LMT_2014/beammaps/generate...pro for the code
# that generates the model saveset.
#
# In order to get the best accuracy out of the model we need to know
# the standard deviation of the fwhm in the az fit to the closest 
# beammap.  This is a proxy for how out of focus the telescope is.
# To find the right az_fwhm_stddev to use we do the following:
# For observations bracketed by
# beammaps, a linear interpolation is used, for observations near a
# beammap and not bracketed, values from that beammap are used, for
# observations on nights where no good beammaps exist, the median
# value of az_fwhm_stddev is used.  We do the same for the detector
# offsets and the FWHM values.
#
# For errors, the max error for
# each parameter and bolometer is used, and if no observation exists
# for that night the standard deviation of the values are returned as error.

# CALLING SEQUENCE: 
# structure = aztec_lmt_get_beammap_params(filename)
# 
# INPUTS:
#    filename - name if netCDF file containing observation
# KEYWORDS:
#    calflag - set if you would like to know the interpolation type
#              calflag = 0 is interpolated between 2 beammaps
#              calflag = 1 is values returned belong to nearest
#              beammap on the same night
#              calflag = 2 is for median value of parameters over
#              whole set, in case no beammaps occured on night
#              observation was made
#    calsource - set to an unnamed variable that on return will
#                indicate which source(s) was the beammap target, for
#                the beammap(s) from which the parameters to use was
#                determined. For calflag=0, will be a two-element
#                vector indicating the two beammap targets. For
#                calflag=1, will be the single beammap target. For
#                calflag=0, this will equal "MEDIAN".
#    errors -  Will store a structure called errors which
#             hold the errors for az and el fwhm and offsets.
#
# MODIFICATION HISTORY:
#
# 5/19/14 - GW - Created by GW, closely based on aztec_aste_get_beam...
# 11/16/14 - PD - translated from IDL to python
#--------------------------------------------------------------------

import numpy as np
import netCDF4
from scipy.io.idl import readsav
from scipy import interpolate
from astropy.time import Time
import sys

# the gain model as a function of elevation and beammap az fwhm stddev
# p[0:5] - the coefficients of the elev. polynomial
# p[6] - the scaling with the az_fwhm_stddev
# p[7:ndet+7] - the offsets for each detector
# el - the elevation angles in degrees
# afs - the standard deviation in az_fwhm measured values (arcsec)
# good_bolos - an array of indexes of good bolometers

def fcf_model(p, el, afs, good_bolos):
  el_model = p[0] + p[1]*el + p[2]*el**2 + p[3]*el**3 + p[4]*el**4 + p[5]*el**5
  afs_model = p[6]*afs
  fcf = np.zeros(144)
  fcf[:] = np.NAN
  for i in range(len(good_bolos)):
	fcf[good_bolos[i]] = p[7+i]*(el_model + afs_model)
  return fcf

#here's the main function
def aztecLMTGetBeammapParams(filename, calflag = None, errors = None, calsource=None, bm_file_used=None):
	
  # get data UT date to decide which parameter files to use
  # convert decimal date into a usable format for the current
  # version of Astropy (0.4.2).  Later versions will be able to
  # skip portions of this code:
  data = netCDF4.Dataset(filename,'r') # read in data file
  UTDate = data.variables['Header.TimePlace.UTDate'][:] # retrieve UTDate from header
  UTDate = UTDate[0] 
  
  # organize date into a format astropy 0.4.2 will accept
  year = np.floor(UTDate)
  decimal = UTDate - year
  a = np.arange(2016.,2100.,4.) # set up a list of leap years
  if year in a: # if leap year, it needs 366 days
    dayDecimal = decimal*366.
  else:
    dayDecimal = decimal*365.
    day = np.floor(dayDecimal)
    hourDecimal = (dayDecimal - day)*24.
    hour = np.floor(hourDecimal)
    minuteDecimal = (hourDecimal - hour)*60.
    minute = np.floor(minuteDecimal)
    secondDecimal = np.round((minuteDecimal - minute)*60.)
    second = np.floor(secondDecimal)
    time = str(int(year))+':'+str(int(day))+':'+str(int(hour))+':'+str(int(minute))+':'+str(int(second)) #this is the actual date we will give to astropy
    prevNoon = str(int(year))+':'+str(int(day))+':'+str(12)+':'+str(0)+':'+str(0)
    nextNoon = str(int(year))+':'+str(int(day+1))+':'+str(12)+':'+str(0)+':'+str(0)
	
  # noons of bracketing days.  Need these to determine if
  # closest bolo file is on the previous night.
  obsNoon = Time(prevNoon, format='yday')
  obsNextNoon = Time(nextNoon, format='yday')
	
  # pre-LMT?
  if UTDate < 2013.:
    raise Exception('There is some mistake - this is the LMT calibration routine but you seem to have ASTE or JCMT data.')
    sys.exit()
  # LMT13A and afterwards.
  if (2013. < UTDate < 2013.833):
    path = '/lab/cdl/home/pdrew/aztec_idl_utilities/parameters_LMT13A' # note, this path needs to be set. temporary hack!!!
    # path.replace('05B','LMT13A') # note, this needs to be set. temporary hack!!!
    path += '/aztec_LMT_params_beammap.sav'
    s = readsav(path,verbose=False)
  else:
    path = '/lab/cdl/home/pdrew/aztec_idl_utilities/parameters_LMT13A' # note, this path needs to be set. temporary hack!!!
    # path.replace('sample replace', 'sample replace') # note, this needs to be set. temporary hack!!!
    path += '/aztec_LMT_params_beammap.sav'
    s = readsav(path, verbose = False)

  # this may be a useful keyword later
  useMedian=0
	
  # get the elevation of the data from the file
  el = data.variables['Header.Source.El'][:]
  el = el[0]
		
  # ---------------------------------------
  # get beammap info sorted by julian date
  # ---------------------------------------
  numf = len(s.jd_beammap)
  ss = np.argsort(s.jd_beammap)
  azfwhm = s.az_fwhm_array[:,ss]
  azfwhmerr = s.det_std_az_fwhm
  elfwhm = s.el_fwhm_array[:,ss]
  elfwhmerr = s.det_std_el_fwhm
  azoff = s.az_offset_array[:,ss]
  azofferr = s.det_std_az_off
  eloff = s.el_offset_array[:,ss]
  elofferr = s.det_std_el_off
  sens = s.sens_array[:,ss]
  senserr = s.det_std_sens
  jdAll = s.jd_beammap[ss]
  ncfiles = s.ncfiles[ss]
  savfiles = s.savfiles[ss]
  sources = s.sources[ss]
  el_beammap = s.el_beammap[ss]
	
  #----------------------------------------
  #make storage arrays for returned offsets
  #----------------------------------------
  nBoloTot = 144
  #initialize with NaN's
  azfwhm_144 = np.zeros(nBoloTot)
  azfwhm_144[:] = np.NAN
  elfwhm_144 = np.zeros(nBoloTot)
  elfwhm_144[:] = np.NAN
  azoff_144 = np.zeros(nBoloTot)
  azoff_144[:] = np.NAN
  eloff_144 = np.zeros(nBoloTot)
  eloff_144[:] = np.NAN
  azfwhmerr_144 = np.zeros(nBoloTot)
  azfwhmerr_144[:] = np.NAN
  elfwhmerr_144 = np.zeros(nBoloTot)
  elfwhmerr_144[:] = np.NAN
  azofferr_144 = np.zeros(nBoloTot)
  azofferr_144[:] = np.NAN
  elofferr_144 = np.zeros(nBoloTot)
  elofferr_144[:] = np.NAN
  gain_144 = np.zeros(nBoloTot)
  gain_144[:] = np.NAN
  gainerr_144 = np.zeros(nBoloTot)
  gainerr_144[:] = np.NAN
  sens_144 = np.zeros(nBoloTot)
  sens_144[:] = np.NAN
  senserr_144 = np.zeros(nBoloTot)
  senserr_144[:] = np.NAN
  bolonames_144 = []
  for j in range(144/24):
    for i in range(24):
      bolonames_144.append('h'+str(j+1)+'b'+str(i+1))
	
  # find where good bolometers are
  goodflag = np.zeros(nBoloTot)
  goodflag[s.good_bolos] = 1
  whGood = s.good_bolos
  nGood = len(whGood)
	
  # returns element (beammap #) of closest beammap to observation
  beammapDate = Time(jdAll, format='jd')
  obsDate = Time(time, format='yday')
  obsJD = obsDate.jd
  bin = np.argmin(np.abs(obsDate - beammapDate))
	
  # pick out bracketing observations
  if (bin == -1 or bin == len(jdAll)-1):
    #file taken before(after) the very first(last)
    #beammap.  Use values from first(last) beammap.
    if obsDate < beammapDate[0]:
      bin1 = 0
      bin2 = 0
    if obsDate > max(beammapDate):
      bin1 = numf-1
      bin2 = numf-1
  else:
    #determine bracketing observations
    if obsDate > beammapDate[bin]:
      bin1 = bin
      bin2 = bin+1
      # was observation after the very last beammap?
    if bin2 == numf:
      bin2 = bin1
    if obsDate == beammapDate[bin]:
      bin1 = bin
      bin2 = bin
    if obsDate < beammapDate[bin]:
      bin1 = bin-1
      bin2 = bin
		
  #At this point we've got our bracketing beammaps. Now to check
  #that the bracketing maps are from the same night.  If not,
  #only use the map on the same night as the observation.  Use
  #5pm UTC (approximately noon MEX) as the dividing line between
  #nights.  This corresponds to floor(jd_est[bin1])+5./24.+1.
	
  # did the first beammap take place on the previous night?
  if beammapDate[bin1] < obsNoon:
    bin1 = bin2
	
  # did the second beammap take place on the following night?
  if beammapDate[bin2] > obsNextNoon:
    bin2 = bin1
	
  # is there no good beammap for this night?
  if (beammapDate[bin1] < obsNoon and beammapDate[bin2] > obsNextNoon):
    print 'No Beammap this night. Using Median values for det. params'
    useMedian = 1
	
  # Before we go further we need to have storage for the beammap az fwhm
  # standard deviation.  This is different from the error in the az
  # fwhm for a particular detector.
  mapAfs = 0.
	
  # IF NO BRACKETING OBSERVATIONS, RETURN EXACT VALUES FROM CHOSEN
  # BEAMMAP
  if (bin1 == bin2 and useMedian == 0):
    azfwhm_144[whGood] = azfwhm[whGood,bin1]
    elfwhm_144[whGood] = elfwhm[whGood,bin1]
    azoff_144[whGood] = azoff[whGood,bin1]
    eloff_144[whGood] = eloff[whGood,bin1]
    sens_144[whGood] = sens[whGood,bin1]
    azfwhmerr[whGood] = azfwhmerr[whGood]
    elfwhmerr[whGood] = elfwhmerr[whGood]
    azofferr_144[whGood] = azofferr[whGood]
    elofferr_144[whGood] = elofferr[whGood]
    senserr_144[whGood] = senserr[whGood]
    map_afs = s.map_az_fwhm_stddev[ss[bin1]]
    calsource = sources[bin1]
    bm_file_used = ncfiles[bin1]
  if (bin1 == 0 or bin1 == numf-1):
    calflag = 3
  else:
    calflag = 1
      
  if (bin1 != bin2 and useMedian == 0):
    # beammaps bracket observation so interpolate values
    for i in range(nGood):
      azfwhmInterpol = interpolate.interp1d([beammapDate[bin1].value, beammapDate[bin2].value],[azfwhm[whGood[i],bin1],azfwhm[whGood[i],bin2]])
      azfwhm_144[whGood[i]] = azfwhmInterpol(obsJD)
      elfwhmInterpol = interpolate.interp1d([beammapDate[bin1].value, beammapDate[bin2].value], [elfwhm[whGood[i],bin1],elfwhm[whGood[i],bin2]])
      elfwhm_144[whGood[i]] = elfwhmInterpol(obsJD)
      azoffInterpol = interpolate.interp1d([beammapDate[bin1].value, beammapDate[bin2].value], [azoff[whGood[i],bin1],azoff[whGood[i],bin2]])
      azoff_144[whGood[i]] = azoffInterpol(obsJD)
      eloffInterpol = interpolate.interp1d([beammapDate[bin1].value, beammapDate[bin2].value], [eloff[whGood[i],bin1],eloff[whGood[i],bin2]])
      eloff_144[whGood[i]] = eloffInterpol(obsJD)
      sensInterpol = interpolate.interp1d([beammapDate[bin1].value, beammapDate[bin2].value], [sens[whGood[i],bin1],sens[whGood[i],bin2]])
      sens_144[whGood[i]] = sensInterpol(obsJD)	
      azfwhmerr_144[whGood] = azFWHMErr[whGood]
      elfwhmerr_144[whGood] = elFWHMErr[whGood]
      azofferr_144[whGood] = azOffErr[whGood]
      elofferr_144[whGood] = elOffErr[whGood]
      senserr_144[whGood] = sensErr[whGood]
      mapafsInterpol = interpolate.interp1d([beammapDate[bin1].value, beammapDate[bin2].value], [s.map_az_fwhm_stddev[ss[bin1]]])
      mapsafs = mapafsInterpol(obsJD)
      calSource = [sources[bin1], sources[bin2]]
      bmFileUsed = [ncfiles[bin1], ncfiles[bin2]]
      calflag = 0
	
  # if both beammaps outside of the shift, return median values
  if useMedian == 1:
    for i in nGood:
      azFWHM_144[whGood[i]] = s.det_med_az_fwhm[whGood[i]]
      elFWHM_144[whGood[i]] = s.det_Med_El_FWHM[whGood[i]]
      azOff_144[whGood[i]] = s.det_Med_Az_Off[whGood[i]]
      elOff_144[whGood[i]] = s.det_Med_El_Off[whGood[i]]
      sens_144[whGood[i]] = s.det_Med_Sens[whGood[i]]
      azFWHMErr_144[whGood] = azFWHMErr[whGood]
      elFWHMErr_144[whGood] = elFWHMErr[whGood]
      azOffErr_144[whGood] = azOffErr[whGood]
      elOffErr_144[whGood] = elOffErr[whGood]
      sensErr_144[whGood] = sensErr[whGood]
      mapAfs = 0.
      calSource = 'Median'
      bmFileUsed = 'Median'
      calflag = 2
      
  # use the gain model to calculate the gain for this map's
  # particular elevation. 
  gain_144 = fcf_model(s.p, el, mapAfs, whGood)
  gainErr_144 = gain_144*0.1 # this is a temporary hack
	
  offsets = {'boloname': bolonames_144,
             'az_fwhm': azfwhm_144,
             'el_fwhm': elfwhm_144,
             'az_offset': azoff_144,
             'el_offset': eloff_144,
             'bologain': gain_144,
             'bologain_err': gainerr_144,
             'bolosens': sens_144}
  errors ={'azFWHMerr': azfwhmerr_144,
           'elfwhmerr': elfwhmerr_144,
           'azofferr': azofferr_144,
           'elofferr': elofferr_144}
  
  return offsets
