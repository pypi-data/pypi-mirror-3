"""
Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 15, 2011
"""

import os,sys
from math import ceil
sys.path.append(os.getcwd())
from numpy import mean,std
#os.system("./testsuite.sh > output.txt")
os.system("python StochSim.py -f dsmts-001-01.xml.psc -t 50 -n 1000  > output.txt")

filename = "output.txt"
data = open(filename,'r')
data_list = data.readlines()

results = []
for i in range(0,51):
    results.append([])

IsPrint = 0
for line in data_list:
    data_line = line.split()
    try:
        t = int(data_line[0])
        x = float(data_line[1])
        results[t].append(x)
    except:
        continue

i =0
while i< len(results):
    print i,"\t",mean(results[i]),"\t",std(results[i])
    i+=1


