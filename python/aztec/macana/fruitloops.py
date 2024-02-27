from aztec import *
from aztec.map import AztecMap
from aztec.macana import runMacana
from aztec.macana.aptools import apFileCreator
from aztec.gaussfit import fitgaussian2d,gaussian2d


class Fruit:
    ''' This implements Flux Recovery Using Iterations (FRUIT) on macana. You need to provide a Analysis Parameter file
        with all the parameters and ncfiles being reduced. 
        
        Data must have been already reduced at least once with the Analysis Parameter file
    '''
    def __init__(self, baseApFile, maxIt=10, outputFile = None):
        self.apFile = baseApFile
        self.maxIt = maxIt
        self.outputFile = outputFile
        self.intlimit = 255.0
        if self.outputFile is None:
                self.outputFile = os.join(path0,'fruit_total.nc')
        
    
    def calculateMorphoKernel (self,amap):
        pixSize = npy.abs(amap.RaCoords[0]-amap.RaCoords[1]).value
        cKernel = amap.fKernel.copy()
        valid, pars = fitgaussian2d(cKernel, amap.RaCoords.value, amap.DecCoords.value)
        bsizex = int(npy.ceil (pars[4]/0.425/pixSize))
        bsizey = int(npy.ceil (pars[5]/0.425/pixSize))
        

        ara = npy.abs(amap.RaCoords)
        adec = npy.abs(amap.DecCoords)
        xc = npy.where(ara == ara.min())
        yc = npy.where(adec == adec.min())
        xc = int(xc[0][0])
        yc = int(yc[0][0])
        bra = amap.RaCoords[xc-bsizex:xc+bsizex+1]
        bdec = amap.DecCoords[yc-bsizey:yc+bsizey+1]
        xx, yy = npy.meshgrid(bra,bdec)
        xx = xx.transpose()
        yy = yy.transpose()
        pars[0]=0.0
        cKernel = gaussian2d((xx,yy), *pars)
        #
        cKernelDilation = npy.array(npy.round (cKernel/cKernel.max()*self.intlimit),dtype='int')
        #cKernelDilation = npy.where (cKernel > 0.05*self.intlimit, cKernelDilation, 0.0)
        #cKernelErode = npy.where (cKernel > 0.75*pars[1], True, False)
        return cKernelDilation#,cKernelErode

    def getMask (self, amap, cutThreshold, iterations = 1):
        '''This routine is designed to create a mask of pixel that should be added to the final map
           It works by:
               
                1. Find all the pixels that exceed a signal to noise ration given by cutThreshold
                2. Use mathematical morphology analysis to remove isolated pixel by a erotion transformation
                3. Use mathematical morphology analysis to increase the mask size by a beam size using a dilation
                   transformation.
                4. Return the filtered signal map multiplied by the mask
    
        '''
        from scipy.ndimage.morphology import binary_erosion, binary_dilation, grey_dilation
        
        cmask = npy.ones (amap.fSignal.shape, dtype=npy.bool)
        cmask = npy.where (amap.fSnMap > cutThreshold, cmask, False)
        
        if cmask.sum() == 0.0:
            return None
        

        dil = self.calculateMorphoKernel(amap)
        cmask = binary_erosion (cmask, iterations = iterations)
        cmask = grey_dilation (cmask, structure=dil, mode = 'constant', cval=0.0)
        cmask = cmask/self.intlimit
        deltaMap = amap.fSignal*cmask
        
        if cmask.sum() == 0.0:
            cmask = npy.where(deltaMap >=0.0, cmask, 0.0)
            return None
        
        return cmask
    
    
    def startIterations (self, covCut =70, cutThreshold = 3.0, startIteration=0):
        curIt = startIteration
        myapFile = self.apFile
        
        #Initialization
        initMapPath = None
        create = True
        apFile = apFileCreator(self.apFile)
        path0 = apFile.getCoaddMapPath()
        if curIt == 0:
            #Need to open the coadded map from the original map
            initMapPath = os.path.join(path0,apFile.getCoaddMap())
        else:
            initMapPath = self.outputFile
            create = False
            
        initMap = AztecMap(initMapPath)
        initMap.wcut(covCut)
        curMapPath = initMapPath
        if create:
            initMap.writeToNc(self.outputFile)
        
        while (curIt <= startIteration + self.maxIt):
            curMap = AztecMap(curMapPath)
            curMap.wcut(covCut)
            curMask = self.getMask(curMap,cutThreshold)
            if not curMask is None:
                if curIt != startIteration:
                    initMap.fSignal += curMap.fSignal*curMask
                    initMap.calculateSNMap()
                    initMap.writeToNc(self.outputFile)
                
                subMask = self.getMask(initMap,cutThreshold)
                if subMask is None:
                    break
                curMap.fSignal = initMap.fSignal * subMask
                curMap.calculateSNMap()
            
                subMap = "fruit_input_iter_%d.nc" % curIt
                newApFile = "ap_iter%d.xml" %(curIt +1)
                newCoaddFile = "fruit_output_iter_%d.nc" % (curIt+1)
                
                curMap.writeToNc(os.path.join(path0,subMap))
                apFile.changeSubParams(path0, subMap)
                apFile.changeCoaddMap(newCoaddFile)
                apFile.writeToFile(newApFile)       
                runMacana(newApFile)
                curMapPath = os.path.join (path0, newCoaddFile)
                curIt += 1
            else:
                break
        print "macana(FRUIT). No more pixels to add. Last output iteration is %d" % curIt   
        
        return curIt


class FruitPcaIterator (Fruit):
    def __init__(self, baseApFile, maxIt=10, outputFile = None):
        Fruit.__init__(self, baseApFile, maxIt, outputFile)
    
    def startIterations (self, covCut =70, cutThreshold = 3.0, startEig = 4, endEig = 6):
        resAp = self.apFile
        
        step = 1
        if startEig > endEig:
            step = -1
        
        apFile = apFileCreator(self.apFile)
        apFile.changeParam("cutStd",0.0)
        apFile.changeParam("splineOrder",0)
        
        
        
        startIteration =0
        for i in npy.arange (startEig,endEig+step,step):
            apFileString = resAp.replace (".xml", "_fruit_eig%d.xml" %i)
            apFile.changeParam("neigToCut", i)
            apFile.writeToFile(apFileString)
            self.apFile = apFileString
            startIteration = Fruit.startIterations(self, covCut, cutThreshold, startIteration)
        
    
