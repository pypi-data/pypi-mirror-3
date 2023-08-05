"""
PySCeS - Python Simulator for Cellular Systems (http://pysces.sourceforge.net)

Copyright (C) 2004-2012 B.G. Olivier, J.M. Rohwer, J.-H.S Hofmeyr all rights reserved,

Johann Rohwer (jrohwer@users.sourceforge.net)
Triple-J Group for Molecular Cell Physiology
Stellenbosch University, South Africa.

Permission to use, modify, and distribute this software is given under the
terms of the PySceS (BSD style) license. See LICENSE.txt that came with
this distribution for specifics.

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
Johann M. Rohwer
"""

from pysces.version import __version__
__doc__ = """
          PyscesParScan
          -------------

          PySCeS class distributed multi-dimensional parameter scans with IPython
          """

import numpy as np
from pysces.PyscesUtils import TimerBox
from pysces.PyscesScan import Scanner
try:
    from IPython.kernel import client
    from twisted.internet.error import ConnectionRefusedError
except ImportError, ex:
    print '\n',ex
    raise SystemExit, 'PARSCANNER: Requires IPython and twisted.'
import sys, os
flush = sys.stdout.flush
from time import sleep
from pysces.engineCode import Analyze

__psyco_active__ = 0

class ParScanner(Scanner):
    """
    Arbitrary dimension generic distributed scanner.
    Subclassed from pysces.PyscesScan.Scanner.
    This class is initiated with a loaded PySCeS model and then allows
    the user to define scan parameters, see self.addScanParameter()
    and user output, see self.addUserOutput().
    Steady-state results are always stored in self.SteadyStateResults while
    user output can be found in self.UserOutputResults.
    Distributed (parallel) execution is achieved with the clustering capability
    of IPython. See "ipcluster --help". --johann 20101206
    """
    genOn = True
    _MODE_ = 'state'
    HAS_USER_OUTPUT = False
    nan_on_bad_state = True
    MSG_PRINT_INTERVAL = 500
    __AnalysisModes__ = ('state','elasticity','mca','stability')
    invalid_state_list = None
    invalid_state_list_idx = None
    scans_per_run = 100

    def __init__(self, mod):
        try:
            mec=client.MultiEngineClient()
            tc=client.TaskClient()
        except ConnectionRefusedError, ex:
            raise SystemExit, str(ex)+'\nPARSCANNER: Requires a running IPython cluster. See "ipcluster --help".\n'
        self.GenDict = {}
        self.GenOrder = []
        self.ScanSpace = []
        self.mod = mod
        self.SteadyStateResults = []
        self.UserOutputList = []
        self.UserOutputResults = []
        self.scanT = TimerBox()
        self.mec=mec
        self.tc=tc

        # get the python path of current file to add to the ipython engines
        mec.execute('import pysces')
        mec.execute('mod=pysces.model("'+mod.ModelFile+'")')
        mec.execute('from pysces.engineCode import *')
        
    def genScanSpace(self):
        """
        Generates the parameter scan space, partitioned according to self.scans_per_run
        """
        spr=self.scans_per_run
        Tsteps = 1
        for gen in self.GenOrder:
            if self.GenDict[gen][4] == False:      # don't increase Tsteps for slaves
                Tsteps *= self.GenDict[gen][2]
        for step in range(Tsteps):
            pars = self.__nextValue__()
            #if pars not in self.ScanSpace:
            self.ScanSpace.append(pars)
        self.ScanSpace = np.array(self.ScanSpace)
        self.SeqArray = np.arange(1,Tsteps+1)
        if Tsteps % spr == 0:
            numparts = Tsteps/spr
        else:
            numparts = Tsteps/spr + 1
        self.ScanPartition = [self.ScanSpace[n*spr:(n+1)*spr] for n in range(numparts)]
        self.SeqPartition = [self.SeqArray[n*spr:(n+1)*spr] for n in range(numparts)]
        self.Tsteps = Tsteps
        
    def Prepare(self,ReRun=False):
        """
        Internal method to prepare the parameters and generate ScanSpace.
        """
        print "\nPREPARATION\n-----------"
        self.scanT.normal_timer('PREP')
        self._MODE_ = self._MODE_.lower()
        assert self._MODE_ in self.__AnalysisModes__, '\nSCANNER: \"%s\" is not a valid analysis mode!' % self._MODE_
        if ReRun:
            self.ScanSpace = []
            self.UserOutputResults = []
            self.SteadyStateResults = []
        self.invalid_state_list = []
        self.invalid_state_list_idx = []
        if self.nan_on_bad_state:
            self.mod.__settings__["mode_state_nan_on_fail"] = True
            self.mec.execute('mod.__settings__["mode_state_nan_on_fail"] = True')
        # generate the scan space
        self.genScanSpace()
        print "Generated ScanSpace:", self.scanT.PREP.next()
        print 'PARSCANNER: Tsteps', self.Tsteps
        flush()

    def Run(self,ReRun=False):
        """
        Run the parameter scan with a load balancing task client.
        """
        self.Prepare(ReRun)
        # this is where the parallel magic fun starts....
        taskids = []
        for i in range(len(self.ScanPartition)):
            t = client.MapTask(
                Analyze,
                args=(self.GenOrder, self.ScanPartition[i], self.SeqPartition[i], self._MODE_, self.UserOutputList, self.mod)
            )
            taskids.append(self.tc.run(t))
        print "Submitted tasks:", len(taskids)
        print "Preparation completed:", self.scanT.PREP.next()
        print "\nPARALLEL COMPUTATION\n--------------------"
        flush()
        self.scanT.normal_timer('RUN')
        while self.tc.queue_status()['pending'] > 0:
            sleep(2)
            print self.tc.queue_status()
        # block until all tasks are completed
        self.tc.barrier(taskids)
        print "Parallel calculation completed:", self.scanT.RUN.next()
        flush()
        
        ## this is analysis stuff
        self.scanT.normal_timer('GATHER')
        print "\nGATHER RESULT\n-------------"
        flush()
        for tid in taskids:
            result = self.tc.get_task_result(tid)
            #tuple: 0 - state_species
                #   1 - state_flux
                #   2 - user_output_results
                #   3 - invalid_state_list
                #   4 - invalid_state_list_idx
            self.StoreData(result)
        self.GatherScanResult()
            
    def RunScatter(self,ReRun=False):
        """
        Run the parameter scan by using scatter and gather for the ScanSpace.
        Not load balanced, equal number of scan runs per node.
        """
        self.Prepare(ReRun)
        # this is where the parallel magic fun starts....
        # push details into client namespace
        self.mec.push({ 'GenOrder' : self.GenOrder,\
                        'mode' : self._MODE_,\
                        'UserOutputList' : self.UserOutputList })
        # scatter ScanSpace and SeqArray
        self.mec.scatter('partition', self.ScanSpace)
        self.mec.scatter('seqarray', self.SeqArray)
        print "Scattered ScanSpace on number of engines:", len(self.mec)
        print "Preparation completed:", self.scanT.PREP.next()
        print "\nPARALLEL COMPUTATION\n--------------------"
        flush()
        self.scanT.normal_timer('RUN')
        # executes scan on partitioned ScanSpace on every node
        self.mec.execute('y=Analyze(GenOrder,partition,seqarray,mode,UserOutputList,mod)')
        print "Parallel calculation completed:", self.scanT.RUN.next()
        flush()

        ## this is analysis stuff
        self.scanT.normal_timer('GATHER')
        print "\nGATHER RESULT\n-------------"
        flush()
        results = self.mec.gather('y')
        results = [results[i:i+5] for i in range(0,len(results),5)]
        for result in results:
            #tuple: 0 - state_species
                #   1 - state_flux
                #   2 - user_output_results
                #   3 - invalid_state_list
                #   4 - invalid_state_list_idx
            self.StoreData(result)
        self.GatherScanResult()

    def StoreData(self, result):
        """
        Internal function which concatenates and stores single result generated by Analyze.

        - *result* IPython client result object
        """
        self.SteadyStateResults.append(np.hstack((np.array(result[0]),np.array(result[1]))))
        if self.HAS_USER_OUTPUT:
            self.UserOutputResults.append(np.array(result[2]))
        self.invalid_state_list += result[3]
        self.invalid_state_list_idx += result[4]

    def GatherScanResult(self):
        """
        Concatenates and combines output result fragments from the parallel scan.
        """
        # from here on we have the complete results
        self.SteadyStateResults = np.vstack([i for i in self.SteadyStateResults])
        if self.HAS_USER_OUTPUT:
            self.UserOutputResults = np.vstack([i for i in self.UserOutputResults])
        self.resetInputParameters()
        print "Gather completed:", self.scanT.GATHER.next()
        print "\nPARSCANNER: %s states analysed" % len(self.SteadyStateResults)
        print "Total time taken: ", self.scanT.PREP.next()
        self.scanT.PREP.close()     # close timer
        self.scanT.RUN.close()
        self.scanT.GATHER.close()
        if len(self.invalid_state_list) > 0:
            print '\nBad steady states encountered at:\n'
            print "Sequence: ", self.invalid_state_list_idx
            print "Parameters: ", self.invalid_state_list
                
