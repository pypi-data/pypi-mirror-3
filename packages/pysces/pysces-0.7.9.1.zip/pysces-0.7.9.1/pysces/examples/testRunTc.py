#!/usr/bin/env python
# Testing the new parallel scanner class

import os
backupdir = os.getcwd()

import numpy as np
import pysces

tbox=pysces.PyscesUtils.TimerBox()
import time

m=pysces.model('isola2a')

print "\n\nParallel execution...scans per run =", 100
par = pysces.ParScanner(m)
par.scans_per_run = 100
t3=time.time()
par.addScanParameter('V4',60,100,11)
par.addScanParameter('V1',100,130,16)
par.addScanParameter('V2',100,130,16,slave=True)
par.addScanParameter('V3',80,90,6)
par.addUserOutput('J_R1', 'A', 'ecR4_X', 'ccJR1_R1')
#par.addUserOutput('J_R1', 'A')
par.Run()
t4=time.time()
print "Duration: %.2f seconds" % (t4-t3)
par.statespersecond = par.Tsteps/(t4-t3)
print "States per second: %.1f" % par.statespersecond


os.chdir(backupdir)