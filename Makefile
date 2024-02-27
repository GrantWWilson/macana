# determine operating system
HOST_OS   := $(shell uname -s 2>/dev/null | tr "[:upper:]" "[:lower:]")
TARGET_OS ?= $(HOST_OS)
ifeq (,$(filter $(TARGET_OS),linux darwin))
    $(error ERROR - unsupported value $(TARGET_OS) for TARGET_OS!)
endif

# set specific library and include locations here
# internal flags
LDFLAGS     :=
IFLAGS      :=

# build flags
ifeq ($(TARGET_OS),darwin)
    LDFLAGS += -L /opt/local/lib 
    IFLAGS  += -I /opt/include -I /opt/local/include
else 
    LDFLAGS += -L /usr/lib
    IFLAGS  += -I /usr/include
endif

CC=g++
CFLAGS   = -c -g -Wall -DHAVE_INLINE -O2 -fexceptions -fopenmp  
IFLAGS  += -I include/ -I /usr/local/include -I Sky/Novas/  
LDFLAGS += -l netcdf_c++ -l netcdf -lgsl -lgslcblas -l fftw3  -lcxsparse -lm -lcfitsio -l CCfits -fopenmp 


#Common source files
CSOURCES=Clean/Clean2dStripe.cpp Clean/Clean.cpp Clean/CleanPCA.cpp Clean/CleanBspline.cpp Clean/CleanHigh.cpp Clean/CleanSelector.cpp Observatory/Detector.cpp Utilities/tinyxml2.cpp Utilities/vector_utilities.cpp Observatory/Array.cpp Observatory/Telescope.cpp Observatory/TimePlace.cpp Sky/Source.cpp Utilities/GslRandom.cpp Analysis/AnalParams.cpp Sky/astron_utilities.cpp Mapmaking/Map.cpp Mapmaking/Observation.cpp Mapmaking/Coaddition.cpp Mapmaking/PointSource.cpp Mapmaking/CompletenessSim.cpp Mapmaking/NoiseRealizations.cpp Mapmaking/WienerFilter.cpp Utilities/gaussFit.cpp Utilities/BinomialStats.cpp Sky/Novas/novas.c Sky/Novas/novascon.c Sky/Novas/nutation.c Sky/Novas/solsys1.c Sky/Novas/eph_manager.c Sky/Novas/readeph0.c Analysis/SimParams.cpp Simulate/MapNcFile.cpp Simulate/SimulationInserter.cpp Simulate/Subtractor.cpp Utilities/SBSM.cpp  Utilities/convolution.cpp Utilities/mpfit.cpp Utilities/sparseUtilities.cpp Clean/AzElTemplateCalculator.cpp



#Macana executable definitions
SOURCES=macanap.cpp $(CSOURCES)
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=macana
#fitswriter executable definitions
SOURCES_FITS=Utilities/fitswriter.cpp 
OBJECTS_FITS=$(SOURCES_FITS:.cpp=.o)
EXECUTABLE_FITS=fitswriter

all: $(EXECUTABLE)  $(EXECUTABLE_FITS) 

$(EXECUTABLE): $(OBJECTS) 
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)  
	ln -s -f macanap

$(EXECUTABLE_FITS): $(OBJECTS_FITS)
	$(CC) $(OBJECTS_FITS) -o $@ $(LDFLAGS)

%.o: %.cpp
	$(CC) $(CFLAGS) $(IFLAGS) $< -o $@

.PHONY: clean

clean:
	rm -rf *.o *~ core */*.o */*~ *.op */*.op $(EXECUTABLE) $(EXECUTABLE_FITS)
