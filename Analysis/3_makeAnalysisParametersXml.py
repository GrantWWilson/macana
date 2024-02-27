import glob
import csv
import os
import numpy as np
from scipy import interpolate
import netCDF4
from scipy.io.idl import readsav

# script to generate ap.xml for a set of netcdf files

#paths and files
outfile = 'ap.xml'
rawDataPath = 'raw_data/'
pointingOffsetsSaveset = ''
pointingOffsetsDatabase = '/data/wilson/LMT_ES3/pointing/pointing_database.csv'

# which analysis steps would you like to do?
mapIndividualObservations = 1
coaddObservations = 1
fitCoadditionToGaussian = 1 
produceNoiseMaps = 1
applyWienerFilter = 1

# Apply a Wiener Filter
gaussianTemplate = 0
gaussianTemplateFWHM = 0
lowPassOnly = 0
highPassOnly = 0
normalizeErrors = 1

#set analysis parameters and switches here
despike = 8.0
lowpassFilter = 4.0
timeOffset = 0.125
timeChunk = 40
approxWeights = 0
masterGrid = [0.,0.]
pixSize = 0.75
azelMap = 0
nNoiseMapsPerObs = 5
nNoise = 20
nThreads = 4

# pca cleaning
cutStd = 0
neig2Cut = 9

#polynomial atmosphere cleaning
CM_tOrder = 0

#cottingham method
CM_splineOrder = 0
CM_cleanPixelSize = 8
CM_cleanStripe = 1
CM_controlChunk = 0.01
CM_resample = 1.


#A description of the Cottingham Parameters
#splineOrder - Is the order (degree) of the spline basis.
#			   3 is for quadratic splines
#			   4 is for cubic splines.
#			   Recommended value: 4
#cleanPixelSize - Defines the pixel size to use in the projection matrix. 
#                 The Hincks' paper suggest a factor 0.3-1.0 beamsize. 
#                 I have tested up to 2*beamsize in the ASTE data with no 
#                 significant changes in the template estimation. 
#cleanStripe -  the cutoff frequency of the high-pass filtering, 
#               Recommended value: 0.25 - 0.75 Hz.
#controlChunk - the number of control points (aka knots) of the bspline, 
#               i.e. the maximum frequency (in time-stream domain) that 
#               the spline will fit. This parameter is relative to the 
#               timeChunk so the number of control points is:
#                     nPoints = round (timeChunk/controlChunk)
#               therefore the frequency of the spline is approximately:
#                     f_spline ~ nPoints/timeChunk
#resample - the decimation factor for the data when producing 
#           the atmos. template


#---------end user inputs ---------

bsPath = rawDataPath
mapPath = rawDataPath.replace('raw_data/', 'reduced_maps/')
rawDataPath_nc = rawDataPath + '*.nc'
files = glob.glob(rawDataPath_nc)
files.sort()
files = [f.replace(rawDataPath,'') for f in files]
bstats = [f.replace('.nc','.bstats') for f in files]
maps = [f.replace('.nc','_maps.nc') for f in files]
nFiles = len(files)

#do some error checking and recommendations
if(nFiles <= 2 and nNoiseMapsPerObs < nNoise):
	print "These settings are not likely to produce independent noise realizations."
	print "Consider increasing nNoiseMapsPerObs - the number of jackknifed noise maps"
	print "created for each observation."
	print "nFiles = " + str(nFiles)
	print "nNoiseMapsPerObs = " + str(nNoiseMapsPerObs)
	print "nNoise = " + str(nNoise)

cleanCount=0
if(cutStd != 0): cleanCount = cleanCount+1
if(neig2Cut != 0): cleanCount = cleanCount+1
if(CM_tOrder != 0): cleanCount = cleanCount+1
if(CM_splineOrder != 0): cleanCount = cleanCount+1
if(cleanCount != 1):
	print "One and only one of [cutStd, neig2Cut, CM_tOrder, CM_splineOrder] can be set."

#coadded file and path
coaddOutPath = rawDataPath.replace('raw_data/', 'coadded_maps/')
coaddOutFile = 'coadded.nc'

#noise realizations
noisePath = rawDataPath.replace('raw_data/', 'noise_maps/')
avgNoisePsdFile = 'average_noise_psd.nc'
avgNoiseHistFile = 'average_noise_histogram.nc'

#if the directories don't exist, create them
if not os.path.exists(mapPath):
	os.makedirs(mapPath)
if not os.path.exists(noisePath):
	os.makedirs(noisePath)
if not os.path.exists(coaddOutPath):
	os.makedirs(coaddOutPath)
	
#get the pointings
if pointingOffsetsSaveset != '':
	s = np.load(pointingOffsetsSaveset)
	bs_az = s['bs_az']
	bs_el = s['bs_el']
elif pointingOffsetsDatabase != '':
	#get utDates from data files
	dutDate = []
	dID = []
	for ncfile in files:
		nc = netCDF4.Dataset(rawDataPath+ncfile)
		dutDate.append(nc.variables['Header.TimePlace.UTDate'][:])
		dID.append(''.join(list(nc.variables['Header.Dcs.ProjectId'][:])).rstrip())
	#get pointing offsets from pointing database
	putDate = []
	pazoff = []
	peloff = []
	pID = []
	with open(pointingOffsetsDatabase,'rb') as f:
		reader = csv.reader(f)
		reader.next()
		reader.next()
		for row in reader:
			putDate.append(float(row[1]))
			pazoff.append(float(row[2]))
			peloff.append(float(row[3]))
			pID.append(row[4].rstrip())
	#go through data files one by one and pick the right pointing offsets
	bs_az = []
	bs_el = []
	for i in range(len(files)):
		#find the bracketing pointing files
		npput = np.array(putDate)
		wbefore = np.where(dutDate[i]-npput >= 0)
		wbefore = wbefore[0]
		wbefore = wbefore.max()
		wafter = np.where(dutDate[i]-npput <= 0)
		wafter = wafter[0]
		wafter = wafter.min()
		#how many of these are from the same pid?
		count=0
		if pID[wbefore] == dID[i]: count = count+1
		if pID[wafter] == dID[i]: count = count+1
		#count=0 or count=2 means we get to interpolate
		if(wbefore == wafter):
			bs_az.append(-pazoff[wbefore])
			bs_el.append(-peloff[wafter])
		elif(count == 0 or count==2):
			azf = interpolate.interp1d(putDate[wbefore:wafter+1],
						   pazoff[wbefore:wafter+1])
			elf = interpolate.interp1d(putDate[wbefore:wafter+1],
						   peloff[wbefore:wafter+1])
			bs_az.append(-azf(dutDate[i]))
			bs_el.append(-elf(dutDate[i]))
		elif(count == 1):
			if pID[wbefore] == dID[i]:
				bs_az.append(-pazoff[wbefore])
				bs_el.append(-peloff[wbefore])
			else:
				bs_az.append(-pazoff[wafter])
				bs_el.append(-peloff[wafter])
else: 
	bs_az = np.zeros(nFiles)
	bs_el = np.zeros(nFiles)
	b = raw_input('No pointing offset saveset or database entered. Continue (y/n)? ')
	if b == 'n' or b == 'N':
		raise Exception('Set the pointingOffsetsSaveset.')

#generate the xml
ap = open(outfile,'w')
seq = ['<analysis>\n', 
'  <!-- analysis steps -->\n',
'  <analysisSteps>\n',
'    <mapIndividualObservations> ',str(mapIndividualObservations),' </mapIndividualObservations>\n',
'    <coaddObservations> ',str(coaddObservations),' </coaddObservations>\n',
'    <fitCoadditionToGaussian> ',str(fitCoadditionToGaussian),' </fitCoadditionToGaussian>\n' ,
'    <produceNoiseMaps> ',str(produceNoiseMaps),' </produceNoiseMaps>\n',
'    <applyWienerFilter> ',str(applyWienerFilter),' </applyWienerFilter>\n',
'  </analysisSteps>\n',
'\n',

'  <!-- start with analysis parameters and switches -->\n',
'  <parameters>\n',
'    <despikeSigma> ',str(despike),' </despikeSigma>\n',
'    <lowpassFilterKnee> ',str(lowpassFilter),' </lowpassFilterKnee>\n',
'    <timeOffset> ',str(timeOffset),' </timeOffset>\n',
'    <timeChunk> ',str(timeChunk),' </timeChunk>\n',
'    <cutStd> ',str(cutStd),' </cutStd>\n',
'    <neigToCut> ',str(neig2Cut),' </neigToCut>\n',
'    <splineOrder> ',str(CM_splineOrder),' </splineOrder>\n',
'    <tOrder> ',str(CM_tOrder),' </tOrder>\n',
'    <cleanPixelSize> ',str(CM_cleanPixelSize),' </cleanPixelSize>\n',
'    <cleanStripe> ',str(CM_cleanStripe),' </cleanStripe>\n',
'    <controlChunk> ',str(CM_controlChunk),' </controlChunk>\n',
'    <resample> ',str(CM_resample),' </resample>\n',
'    <approximateWeights> ',str(approxWeights),' </approximateWeights>\n',
'    <masterGridJ2000_0> ',str(masterGrid[0]),' </masterGridJ2000_0>\n',
'    <masterGridJ2000_1> ',str(masterGrid[1]),' </masterGridJ2000_1>\n',
'    <pixelSize> ',str(pixSize),' </pixelSize>\n',
'    <nNoiseMapsPerObs> ',str(nNoiseMapsPerObs),' </nNoiseMapsPerObs>\n',
'    <azelMap> ',str(azelMap),' </azelMap>\n',
'    <threadNumber> ',str(nThreads),' </threadNumber>\n',
'  </parameters>\n',

'\n',
'  <!-- apply a wiener filter -->\n',
'  <wienerFilter>\n',
'    <gaussianTemplate> ',str(gaussianTemplate),' </gaussianTemplate>\n',
'    <gaussianTemplateFWHM> ',str(gaussianTemplateFWHM),' </gaussianTemplateFWHM>\n',
'    <lowpassOnly> ',str(lowPassOnly),' </lowpassOnly>\n',
'    <highpassOnly> ',str(highPassOnly),' </highpassOnly>\n',
'    <normalizeErrors> ',str(normalizeErrors),' </normalizeErrors>\n',
'  </wienerFilter>\n',

'\n',
'  <!-- coaddition path and files -->\n',
'  <coaddition>\n',
'    <mapPath>',coaddOutPath,'</mapPath>\n',
'    <mapFile>',coaddOutFile,'</mapFile>\n',
'  </coaddition>\n',

'\n',
'  <!-- noise realization path and files -->\n',
'  <noiseRealization>\n',
'    <nRealizations>',str(nNoise),'</nRealizations>\n',
'    <noisePath>',noisePath,'</noisePath>\n',
'    <avgNoisePsdFile>',avgNoisePsdFile,'</avgNoisePsdFile>\n',
'    <avgNoiseHistFile>',avgNoiseHistFile,'</avgNoiseHistFile>\n',
'  </noiseRealization>\n',

'\n',
'  <!-- observation filelist -->\n',
'  <observations>\n',
'    <rawDataPath>',rawDataPath,'</rawDataPath>\n',
'    <bsPath>',bsPath,'</bsPath>\n',
'    <mapPath>',mapPath,'</mapPath>\n',
'    <nFiles>',str(nFiles),'</nFiles>\n'
]
for line in seq:
	ap.writelines(line)

for i in range(nFiles):
	seq=['    <f',str(i),'>\n',
	'      <fileName>',files[i],'</fileName>\n',
	'      <bsName>',bstats[i],'</bsName>\n',
	'      <mapName>',maps[i],'</mapName>\n',
	'      <bsOffset_0>',str(bs_az[i]),'</bsOffset_0>\n',
	'      <bsOffset_1>',str(bs_el[i]),'</bsOffset_1>\n',
	'    </f',str(i),'>\n']
	ap.writelines(seq)

seq = ['  </observations>\n',
'</analysis>']
ap.writelines(seq)
ap.close()


