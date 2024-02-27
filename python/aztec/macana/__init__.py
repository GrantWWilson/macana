import os

def makeDirectoryStructure(mdir):
    if not os.path.exists(mdir+'/raw_data/'):
        os.mkdir(mdir+'/raw_data/')
    if not os.path.exists(mdir+'/reduced_maps/'):
        os.mkdir(mdir+'/reduced_maps/')
    if not os.path.exists(mdir+'/noise_maps/'):
        os.mkdir(mdir+'/noise_maps/')

def runMacana(apfile, macanaPath = os.path.expanduser(os.environ['AZTEC_MACANA_PATH'])):
    import subprocess
    curDir = os.getcwd()
    apfile = os.path.abspath(apfile)
    command = macanaPath + "/macana"
    subprocess.check_call([command, apfile])
    os.chdir(curDir)