
;script to generate ap.xml for a set of netcdf files

;paths and files
outfile = '/data/wilson/EGS/aztec_c++/ap.xml'
rawDataPath = '/data/wilson/EGS/aztec_c++/raw_data/'
bsPath = rawDataPath
mapPath = repstr(rawDataPath,'raw_data/', 'reduced_maps/')
files = file_search(rawDataPath,'*.nc')
files = repstr(files,rawDataPath,'')
bstats = repstr(files,'.nc','.bstats')
maps = repstr(files,'.nc','_maps.nc')
nFiles = n_elements(files)

;coadded file and path
coaddOutPath = repstr(rawDataPath,'raw_data/', 'coadded_maps/')
coaddOutFile = 'coadded_rxj1347.nc'

;noise realizations
nNoise = 100
noisePath = repstr(rawDataPath,'raw_data','noise_maps')
avgNoisePsdFile = 'average_noise_psd.nc'
avgNoiseHistFile = 'average_noise_histogram.nc'


;which analysis steps would you like to do?
mapIndividualObservations = 1
coaddObservations = 1
fitCoadditionToGaussian = 1
produceNoiseMaps = 1
applyWienerFilter = 1


;set analysis parameters and switches here
despike = 7.0
lowpassFilter = 4.0
timeOffset = 0.125
timeChunk = 0
cutStd = 0
neig2cut = 9
CM_splineOrder = 0              ;Spline order 0 deactivates CM
                                ;must 3 (quadratic spline), 4 (cubic spline)
CM_cleanPixelSize = 4           ;Pixel size for Cottingham method
CM_cleanStripe = 1              ;
CM_controlChunk = 0.0           ;Time separation for control points supporting 
                                ;globally the basis-spline, If 0 number of 
                                ;control points is set to 
                                ;(timeChunk*samplingFreq)+order + 1). 
                                ;Must be less than timeChunkValue.
approx_weights = 0
masterGrid = [0.,0.]
pixsize = 0.75

;set to apply a wiener filter
wiener_filter=1

;number of threads to use
nThreads=4

;get the pointings
;restore, '/data/wilson/EGS/pointing/EGS_pointing_offsets.sav'
bs_az = dblarr(nfiles)
bs_el = dblarr(nfiles)

;generate the xml
openw, 6, outfile
printf, 6, '<analysis>'
printf, 6, '  <!-- analysis steps -->'
printf, 6, '  <analysisSteps>'
printf, 6, '    '+strcompress('<mapIndividualObservations> '+string(mapIndividualObservations)+' </mapIndividualObservations>')
printf, 6, '    '+strcompress('<coaddObservations> '+string(coaddObservations)+' </coaddObservations>')
printf, 6, '    '+strcompress('<fitCoadditionToGaussian> '+string(fitCoadditionToGaussian)+' </fitCoadditionToGaussian>')
printf, 6, '    '+strcompress('<produceNoiseMaps> '+string(produceNoiseMaps)+'  </produceNoiseMaps>')
printf, 6, '    '+strcompress('<applyWienerFilter> '+string(applyWienerFilter)+' </applyWienerFilter>')
printf, 6, '  </analysisSteps>'
printf, 6, ''

printf, 6, '  <!-- start with analysis parameters and switches -->'
printf, 6, '  <parameters>'
printf, 6, '    '+strcompress('<despikeSigma> '+string(despike)+' </despikeSigma>')
printf, 6, '    '+strcompress('<lowpassFilterKnee> '+string(lowpassFilter)+' </lowpassFilterKnee>')
printf, 6, '    '+strcompress('<timeOffset> '+string(timeOffset)+' </timeOffset>')
printf, 6, '    '+strcompress('<timeChunk> '+string(timeChunk)+' </timeChunk>')
printf, 6, '    '+strcompress('<cutStd> '+string(cutStd)+' </cutStd>')
printf, 6, '    '+strcompress('<neigToCut> '+string(neig2cut)+' </neigToCut>')
printf, 6, '    '+strcompress('<splineOrder> '+string(CM_splineOrder)+' </splineOrder>')
printf, 6, '    '+strcompress('<cleanPixelSize> '+string(CM_cleanPixelSize)+' </cleanPixelSize>')
printf, 6, '    '+strcompress('<cleanStripe> '+string(CM_cleanStripe)+' </cleanStripe>')
printf, 6, '    '+strcompress('<controlChunk> '+string(CM_controlChunk)+' </controlChunk>')
printf, 6, '    '+strcompress('<approximateWeights> '+string(approx_weights)+' </approximateWeights>')
printf, 6, '    '+strcompress('<masterGridJ2000_0> '+string(masterGrid[0])+' </masterGridJ2000_0>')
printf, 6, '    '+strcompress('<masterGridJ2000_1> '+string(masterGrid[1])+' </masterGridJ2000_1>')
printf, 6, '    '+strcompress('<pixelSize> '+string(pixsize)+' </pixelSize>')
printf, 6, '    '+strcompress('<threadNumber> '+string(nThreads)+' </threadNumber>')
printf, 6, '  </parameters>'

printf, 6, ''
printf, 6, '  <!-- apply a wiener filter -->'
printf, 6, '  <wienerFilter>'
printf, 6, '    <gaussianTemplate> 0 </gaussianTemplate>'
printf, 6, '    <gaussianTemplateFWHM> 0 </gaussianTemplateFWHM>'
printf, 6, '    <lowpassOnly> 0 </lowpassOnly>'
printf, 6, '    <highpassOnly> 0 </highpassOnly>'
printf, 6, '    <normalizeErrors> 1 </normalizeErrors>'
printf, 6, '  </wienerFilter>'

printf, 6, ''
printf, 6, '  <!-- coaddition path and files -->'
printf, 6, '  <coaddition>'
printf, 6, '    '+strcompress('<mapPath>'+coaddOutPath+'</mapPath>')
printf, 6, '    '+strcompress('<mapFile>'+coaddOutFile+'</mapFile>')
printf, 6, '  </coaddition>'

printf, 6, ''
printf, 6, '  <!-- noise realization path and files -->'
printf, 6, '  <noiseRealization>' 
printf, 6, '    <nRealizations>'+strcompress(string(nNoise),/rem)+'</nRealizations>'
printf, 6, '    <noisePath>'+noisePath+'</noisePath>'
printf, 6, '    <avgNoisePsdFile>'+avgNoisePsdFile+'</avgNoisePsdFile>'
printf, 6, '    <avgNoiseHistFile>'+avgNoiseHistFile+'</avgNoiseHistFile>'
printf, 6, '  </noiseRealization>'

printf, 6, ''
printf, 6, '  <!-- observation filelist -->'
printf, 6, '  <observations>'
printf, 6, '    <rawDataPath>'+rawDataPath+'</rawDataPath>'
printf, 6, '    <bsPath>'+bsPath+'</bsPath>'
printf, 6, '    <mapPath>'+mapPath+'</mapPath>'
printf, 6, '    <nFiles> '+strcompress(string(nFiles),/rem)+'</nFiles>'
for i=0,nFiles-1 do begin
   printf, 6, '    '+strcompress('<f'+string(i)+'>',/rem)
   printf, 6, '      <fileName>'+files[i]+'</fileName>'
   printf, 6, '      <bsName>'+bstats[i]+'</bsName>'
   printf, 6, '      <mapName>'+maps[i]+'</mapName>'
   printf, 6, '      <bsOffset_0>'+string(bs_az[i])+'</bsOffset_0>'
   printf, 6, '      <bsOffset_1>'+string(bs_el[i])+'</bsOffset_1>'
   printf, 6, '    '+strcompress('</f'+string(i)+'>',/rem)
endfor
printf, 6, '  </observations>'
printf, 6, '</analysis>'
close, 6




end
