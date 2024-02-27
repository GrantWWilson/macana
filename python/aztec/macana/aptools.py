from lxml import etree
import xml.etree.ElementTree as ET
import os
import shutil


class apError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__ (self):
        return "Analysis Parameters Error: " + self.value

class apFileCreator:
    
    """This class allows to modify the content of an Analysis Parameters file (apfile). It is intended to automatize macana
       from python.
    """
    
    def __init__ (self, apTemplate):
        """Creates the apFileCreator
            Input:
                    apTemplate    An xml file with the Analysis Parameters you want to modiyf
        """
        self.template = apTemplate
        self.readTemplate()
        
    def readTemplate(self):
        parser = etree.XMLParser(remove_blank_text=True)
        self.apTree = etree.parse(self.template,parser=parser)
        self.analysisRoot = self.apTree.getroot()
        self.params = self.analysisRoot.find('parameters')
        self.coadd = self.analysisRoot.find('coaddition')
        self.noise = self.analysisRoot.find('noiseRealization')
        self.obs = self.analysisRoot.find('observations')
        self.simulate = self.analysisRoot.find('simulate')
        self.subtract = self.analysisRoot.find('subtract')
        
    def changeParam(self, paramName, value):
        cElement = self.params.find(paramName)
        if cElement is None:
            raise apError('No such parameter on template file')
        cElement.text = str(value)
        
    def changeAttribute (self, paramName, attributeName, value):
        cElement = self.params.find(paramName)
        if cElement is None:
            raise apError('No such parameter on template file')
        try:
            cElement.attrib[attributeName]=value
        except Exception:
            raise apError('No such attribute on template file')
        
    
    def changeCoaddPath(self, newPath):
        path = self.coadd.find('mapPath')
        if not path is None:
            path.text = newPath
        else:
            raise apError ('mapPath element not found in template file')
    
    def getCoaddMap (self):
        return self.coadd.find('mapFile').text
    
    def getCoaddMapPath(self):
        return self.coadd.find('mapPath').text
    
    def changeCoaddMap (self, newMapName):
        path = self.coadd.find('mapFile')
        if not path is None:
            path.text = newMapName
        else:
            raise apError ('mapPath element not found in template file')
        
    def changeSubParams (self, path, newMapName):
        if self.subtract is None: 
            self.subtract = etree.SubElement(self.analysisRoot, 'subtract')
            subPath = etree.SubElement(self.subtract, 'subPath')
            subFile = etree.SubElement (self.subtract, 'subFile')
        else:
            subPath = self.subtract.find('subPath')
            subFile = self.subtract.find('subFile')
        subPath.text = path
        subFile.text = newMapName
        
    def getSubParams(self):
        #return self.subtract.find('subPath').text + "/" + self.subtract.find('subFile').text
        return self.subtract.find('subPath').text + self.subtract.find('subFile').text
        
    def changeSimMap(self, newMapName):
        if not self.simulate is None:
            simMapE = self.simulate.find('simFile')
            simMapE.text = newMapName
        else:
            print "Parameter file has no simulate option, skipping"
    
    def changeSimParam(self, parameter, value):
        if not self.simulate is None:
            par = self.simulate.find (parameter)
            if not par is None:
                par.text = str(value)
            else:
                print "Not such simulation parameter, skipping"
        else:
            print "Parameter file has no simulate option, skipping"

    def changeNoisePath(self, newMapName):
        if not self.noise is None:
            noisePath = self.noise.find('noisePath')
            noisePath.text = newMapName
        else:
            print "Parameter file has no simulate option, skipping"
            
    def getNoisePath(self):
        if not self.noise is None:
            noisePath = self.noise.find('noisePath')
            return noisePath.text 
        else:
            print "Parameter file has no noise Path statement"

    def writeToFile(self, filename):
        f=open (filename, "w")
        f.write(etree.tostring(self.analysisRoot, pretty_print=True))
        f.close()
    
    def createSimulate (self, directory, simMap):
        if not self.simulate is None:
            self.analysisRoot.remove(self.simulate)
        self.simulate = ET.SubElement(self.analysisRoot, "simulate")
        fluxFactor = ET.SubElement(self.simulate, "fluxFactor")
        fluxFactor.text = "1"
        addSignal = ET.SubElement(self.simulate,"addSignal")  #  <addSignal>0</addSignal>
        addSignal.text= "0"
        atmFreq = ET.SubElement(self.simulate, "atmFreq")
        atmFreq.text = "5"
        noiseChunk = ET.SubElement (self.simulate, "noiseChunk")
        noiseChunk.text = "0"
        simPath = ET.SubElement(self.simulate, "simPath")
        simPath.text = directory
        simFile = ET.SubElement(self.simulate,"simFile")
        simFile.text = simMap
    
    def createSubtract(self, directory, subMap):
        if not self.subtract is None:
            self.analysisRoot.remove(self.subtract)
        self.subtract = ET.SubElement(self.analysisRoot, "subtract")
        subPath = ET.SubElement(self.subtract, "subPath")
        subPath.text = directory
        subFile = ET.SubElement(self.subtract,"subFile")  #  <addSignal>0</addSignal>
        subFile.text= subMap
    
