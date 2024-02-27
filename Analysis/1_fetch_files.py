#script to grab the new pointing and science files
import os
import subprocess

#specify new pointing files here
newpoint = ['31756','31771']
destpoint = 'pointing/raw_data'

#specify new science files here
obs = [31766,31768,31769,31770]
newscience=[]
for i in range(len(obs)):
    newscience.append(str(obs[i]))
destscience = 'raw_data'

#specify source of files (the data repository) here
source = 'mnc:'
source = ''

#rsync or ssh
cmd = 'rsync -avz --progress --update '

#Pointing Files
for i in range(len(newpoint)):
    ptcmd = cmd+source+'/data_lmt/aztec/*'+newpoint[i]+'*.nc '+destpoint+'/.'
    res = subprocess.call(ptcmd,shell=True)

#Science Files
for i in range(len(newscience)):
    sccmd = cmd+source+'/data_lmt/aztec/*'+newscience[i]+'*.nc '+destscience+'/.'
    res = subprocess.call(sccmd,shell=True)

