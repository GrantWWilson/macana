import os
import glob
import netCDF4
import numpy as np
from scipy.io.idl import readsav
import aztecLMTGetBeammapParams

#aztec_ancillary_data_to_xml.pro
#this is a utility to take a netcdf file and its associated bolostats
#and goodflag files and reformat all key information into an xml file

#xml formatter
def printXMLVar(varname, value, units=''):
	bstats.write('  <'+varname+'>\n')
	if units != '':
		bstats.write('    <value>'+str(value)+'</value><units>'+str(units)+'</units>\n')
	else:
		bstats.write('    <value>'+str(value)+'</value>\n')
	bstats.write('  </'+varname+'>\n')

#working dir
workingDir = '/data4/pdrew/sample/raw_data/'
os.chdir(workingDir)
ncList = workingDir +'aztec*.nc'

#collect files to use
ncdfFile = glob.glob(ncList)
outFile = [f.replace('.nc','.bstats') for f in ncdfFile]
nFiles = len(ncdfFile)

#set up some filenames and constants
variablePreface = 'Data.AztecBackend.'
boloStatsFile = '/home/pdrew/aztec_idl_utilities/parameters_LMT13A/bolostats_default.txt'
bListFile = '/home/pdrew/aztec_idl_utilities/parameters_LMT13A/bololist.csv'
bDC2TauSave = '/home/pdrew/aztec_idl_utilities/parameters_LMT13A/fit_parameters_bolodc2tau_LMT13A.sav'
bDC2ResSave = '/home/pdrew/aztec_idl_utilities/parameters_LMT13A/fit_parameters_bolodc2responsivity_LMT13A.sav'

# create number identifiers for bolonames
h = []
b = []
for j in range(6):
	for i in range(24):
		h.append(j+1)
		b.append(i+1)
		

#run through the .nc files and collect the data
for i in range(nFiles):
	ncFile = netCDF4.Dataset(ncdfFile[i],'r')
	boloNames = []
	boloID = []
	boloNCDFLocation = []
	for j in range(144):
		boloNames.append(variablePreface+'h'+str(h[j])+'b'+str(b[j]))
		boloID.append('d'+str(j))
		boloNCDFLocation.append(188+j-1)
	ncFile.close()
	
	# read in bolo stats file
	bstxt = open(boloStatsFile,'r')
	bsheader1 = bstxt.readline() # skips over header line 1
	bsheader2 = bstxt.readline() # skips line 2
	bsheader3 = bstxt.readline() # skips line 3
	goodflag = np.zeros(144,dtype = int)
	
	l = []
	for line in bstxt: # convert the boloStatsFile into an array of strings
		line = line.strip()
		columns = line.split()
		l.append(line)
	bstxt.close()
	
	for j in range(len(l)):
		if len(l[j]) > 4: #record goodflag for bolometers
			goodflag[j] = 1
	
	k = []
	bltxt = open(bListFile,'r') # convert bListFile into an array of strings
	for line in bltxt:
		line = line.strip()
		columns = line.split()
		k.append(line)
	bltxt.close()
	
	for j in range(len(k)): # record goodflag for bolometers
		if '0' in k[j]:
			goodflag[j] = 0

	u = readsav(bDC2TauSave,verbose=False) # read in the savset and retrieve variables
	try:
		u.p0 #see if variable p0 exists in s. if not use the user defined offsets
	except:
		offsetDC2Tau = offset
		slopeDC2Tau = slope
		quadDC2Tau = np.zeros(len(offsets))
		offsetErrDC2Tau = offset_err
		slopeErrDC2Tau = slope_err
		quadErrDC2Tau = np.zeros(len(offsets))
	else:
		offsetDC2Tau = u.p0
		slopeDC2Tau = u.p1
		quadDC2Tau = u.p2
		offsetErrDC2Tau = u.p0_err
		slopeErrDC2Tau = u.p1_err
		quadErrDC2Tau = u.p2_err
	
	#get offsets, slopes and errors for bolodc to responsivity conversion
	t = readsav(bDC2ResSave,verbose=False)
	offsetDC2Res = t.offset
	slopeDC2Res = t.slope
	offsetErrDC2Res = t.offset_err
	slopeErrDC2Res = t.slope_err
	
	# get the gain, az and el offsets and az and el FWHM using the utility
	offinfo = aztecLMTGetBeammapParams.aztecLMTGetBeammapParams(ncdfFile[i])
	
	# now the output xml
	bstats = open(outFile[i], 'wb')
	npts = len(boloNames)
	
	printXMLVar('nBolos', 144)
	for j in range(npts):
		bstats.write('<'+boloID[j]+'>\n')
		printXMLVar('name', boloNames[j])
		printXMLVar('ncdf_location', boloNCDFLocation[j],)
		printXMLVar('az_fwhm', offinfo['az_fwhm'][j],units='arcseconds')
		printXMLVar('el_fwhm', offinfo['el_fwhm'][j],units='arcseconds')
		printXMLVar('az_offset', offinfo['az_offset'][j], units='arcseconds')
		printXMLVar('el_offset', offinfo['el_offset'][j], units='arcseconds')
		printXMLVar('bologain', offinfo['bologain'][j], units='mJy/nW')
		printXMLVar('bologain_err', offinfo['bologain_err'][j], units='mJy/nW')
		printXMLVar('bolosens', offinfo['bolosens'][j], units='mJy-rt(s)')
		printXMLVar('offset_dc2tau',offsetDC2Tau[j])
		printXMLVar('offset_err_dc2tau', offsetErrDC2Tau[j])
		printXMLVar('slope_dc2tau', slopeDC2Tau[j])
		printXMLVar('slope_err_dc2tau', slopeErrDC2Tau[j])
		printXMLVar('quad_dc2tau', quadDC2Tau[j])
		printXMLVar('quad_err_dc2tau', quadErrDC2Tau[j])
		printXMLVar('offset_dc2responsivity',offsetDC2Res[j])
		printXMLVar('offset_err_dc2responsivity', offsetErrDC2Res[j])
		printXMLVar('slope_dc2responsivity', slopeDC2Res[j])
		printXMLVar('slope_err_dc2responsivity', slopeErrDC2Res[j])
		printXMLVar('goodflag', goodflag[j])
		bstats.write('</'+boloID[j]+'>\n')
	bstats.close()
	
	
	
	
	
	
	
	
	