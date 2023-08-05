import os
import numpy,scipy
scipy.pkgload('io')
import pysces
from pysces.PyscesModelMap import ModelMap
from pylab import figure, close, show, ioff, figtext
from matplotlib.transforms import offset_copy
import cStringIO,string
from colorsys import hsv_to_rgb as htor
from matplotlib.figure import Figure as mplfigure
import warnings

doc = '''
************************************* 
* RateChar add-on module for PySCeS *
*************************************

Does generic supply-demand parameter scans around
internal metabolites species of a model and optionally
plots the results.

Copyright (c) Johann Rohwer, Carl Christensen
and Jannie Hofmeyr, 2007-2011
Triple-J Group for Moleculear Cell Physiology
Stellenbosch University, South Africa

Open Source Software distributed under
the PySCeS (BSD style) licence, see LICENSE.txt.
'''

class RateChar:
    """Main class for doing generic supply-demand rate characteristics"""
    def __init__(self, psc_file, min_concrange_factor=100, max_concrange_factor=100):
        """
        __init__(psc_file)

       ParScan Arguments:
        ==========
        psc_file: pysces input file with which to instantiate class
        """
        
        
        print doc
        # default scan parameter values
        self.min_concrange_factor = min_concrange_factor
        self.max_concrange_factor = max_concrange_factor
        self.min_fluxrange_factor = 2
        self.max_fluxrange_factor = 2
        self.scan_points = 256

        # initialise model
        self._out_base_dir=pysces.PyscesModel.OUTPUT_DIR+'/ratechar_out'
        self._psc_mod = None
        self._psc_out_dir = None
        self._psc_mod_dir = pysces.PyscesModel.MODEL_DIR
        if not '.psc' in psc_file:
            self._psc_file = psc_file + '.psc'
            self._mod = psc_file
        else:
            self._psc_file = psc_file
            self._mod = psc_file[:-4]
        status = self.checkModelStatus()
        if status:
            self.createModelOutputDir()
            print 'Using model directory:  ', self._psc_mod_dir
            print 'Using output directory: ', self._psc_out_dir
            self.loadModel()
        else:
            print 'ERROR - ', self._psc_file, ' IS NOT LOCATED IN PySCeS MODEL DIRECTORY!'


    def checkModelStatus(self):
        """
        checkModelStatus()

        Checks to see if the pysces file is located in the pysces input file directory.

        Arguments:
        ==========
        None
        """
        all_psc = os.listdir(self._psc_mod_dir)
        if self._psc_file in all_psc:
            return True
        else:
            return False

    def createModelOutputDir(self):
        """
        createModelOutputDir()

        Creates a directory based on the model filename in the output base directory
        for all model output. For mulitple simulations with different models
        a directory for each model is created.

        Arguments:
        =========
        None
        """
        out_base_dir_status = os.path.exists(self._out_base_dir)
        if not out_base_dir_status:
            os.mkdir(self._out_base_dir)
        model_output_dir =  self._out_base_dir + '/' + self._mod
        model_output_dir_status = os.path.exists(model_output_dir)
        if not model_output_dir_status:
            os.mkdir(model_output_dir)
        self._psc_out_dir = model_output_dir
        pysces.PyscesModel.output_dir = model_output_dir

    def loadModel(self):
        """
        loadModel()

        Loads a PySCeS model.

        Arguments:
        =========
        None
        """
        self._psc_mod = pysces.model(self._psc_file)
        # self._psc_mod.doLoad()   # no longer necessary as of PySCeS 0.7.0

    def pscFile2str(self, name):
        """
        pscFile2str(name)

        Read psc file and return as string

        Arguments:
        ==========
        name - string containing filename
        """
        if name[-4:] != '.psc':
            name += '.psc'
        F = file(os.path.join(pysces.PyscesModel.MODEL_DIR, name),'r')
        fstr = F.read()
        F.close()
        return fstr

    def pscMod2str(self, mod):
        """
        pscMod2str(name)

        Write PySCeS model out to string

        Arguments:
        ==========
        mod - instantiated PySCeS model
        """
        F = cStringIO.StringIO()
        mod.showModel(filename=F)
        fstr = F.getvalue()
        F.close()
        return fstr

    def stripFixed(self, fstr):
        """
        stripFixed(fstr)

        Take a psc file string and return (Fhead, stripped_fstr)
        where Fhead is the file header containing the "FIX: " line
        and stripped_fstr is remainder of file as string

        Arguments:
        ==========
        fstr - string representation of psc file

        See also:
        =========
        pscFile2str(name)
        """
        Fi = cStringIO.StringIO()
        Fi.write(fstr)
        Fi.seek(0)
        Fo = cStringIO.StringIO()
        Fhead = None
        for line in Fi:
            if line[:4] == "FIX:":
                Fhead = string.strip(line)
                Fo.write('\n')
            else:
                Fo.write(line)
        Fo.seek(0)
        return Fhead, Fo.read()


    def augmentFixString(self, OrigFix, fix):
        """
        augmentFixString(OrigFix, fix)

        Add fix to FixString

        Arguments:
        ==========
        OrigFix - original FixString
        fix     - additional species to add to FixString
        """
        return OrigFix + ' %s' % fix


    def evalBaseMod(self,show=1,file=0):
        """
        evalBaseMod(show=1,file=0)

        Evaluates base model in terms of steady state and MCA.
        Prints steady state values, elasticities and control coefficients
        to screen and optionally writes to file.

        Arguments:
        ==========
        show (bool) - print steady-state results on screen (default=1)
        file (bool) - write steady-state results to file (default=0)
        """
        basemod = self._psc_mod
        basemod.mode_elas_deriv=1
        basemod.doMca()
        if show:
            basemod.showState()
            basemod.showEvar()
            basemod.showCC()
        if file:
            rFile = open(os.path.join(self._psc_out_dir,self._mod+'_stst.txt'),'w')
            basemod.showState(rFile)
            basemod.showEvar(rFile)
            basemod.showCC(rFile)
            rFile.write('\n')
            rFile.close()
            
    def setMaxConcRangeFactor(self, max_concrange_factor):
        """
        Changes the maximum concentration factor
        """
        self.max_concrange_factor = max_concrange_factor
        
    def setMinConcRangeFactor(self, min_concrange_factor):
        """
        Changes the Minimum concentration factor
        """
        self.min_concrange_factor = min_concrange_factor
        
    def setScanPoints(self, scan_points):
        self.scan_points = scan_points
        
    def setDefaults(self):
        self.min_concrange_factor = 100
        self.scan_points = 256
        self.max_concrange_factor = 100
        
    def doRateChar(self, fixed, summary=0, solver=0):
        """
        doRateChar(fixed)

        Does rate characteristic analysis around single species (fixed).
        Stores data in instance of RateCharData class which is attached
        as attribute 'fixed' to current RateChar instance.

        Arguments:
        ==========
        fixed (str)    - species around which to generate rate characteristic
        summary (bool) - write summary to output file (default 0)
        solver (int)   - steady-state solver to use: 0 - hybrd, 1 - fintslv, 2 - NLEQ2
        """
        assert solver in (0,1,2), "\nSolver mode can only be one of (0, 1, 2)!"
        #if summary:
            #assert hasattr(self, 'summaryfile'), "\nSummary mode can only be called from doAllRateChar method."
        # base steady state
        basemod = self._psc_mod
        basemod.doMca()
        assert fixed in basemod.species, "\nInvalid fixed species."
        basemod_fstr = self.pscMod2str(basemod)
        basemod.mode_elas_deriv=1
        mymap = ModelMap(basemod)
        OrigFix, Fstr = self.stripFixed(basemod_fstr)
        print Fstr
        h1 = self.augmentFixString(OrigFix, fixed)
        model1 = self._mod + '_' + fixed
        mod = pysces.model(model1, loader="string", fString=h1+'\n'+Fstr)
        #mod.doLoad()   # no longer needed as of PySCeS 0.7.0
        mod.SetQuiet()
        mod.mode_solver = solver
        mod.doState()
        mod.mode_elas_deriv = 1
        setattr(mod,fixed,getattr(basemod,fixed+'_ss'))
        mod.doMcaRC()
        # get fluxes directly linked to fixed species
        FixSubstrateFor = ['J_' + r for r in getattr(mymap, fixed).isSubstrateOf()]
        FixProductFor = ['J_' + r for r in getattr(mymap, fixed).isProductOf()]
        print 'Fixed species is Substrate for: ', FixSubstrateFor
        print 'Fixed species is Product for:   ', FixProductFor
        # set scan distances
        scan_min = getattr(basemod,fixed+'_ss')/self.min_concrange_factor
        scan_max = getattr(basemod,fixed+'_ss')*self.max_concrange_factor
        # do scan               
        rng = scipy.logspace(scipy.log10(scan_min),scipy.log10(scan_max),self.scan_points)
        sc1 = pysces.Scanner(mod)
        sc1.quietRun = True
        sc1.printcnt = 50
        sc1.addScanParameter(fixed, scan_min, scan_max, self.scan_points,log=True)
        args = [fixed] + FixProductFor + FixSubstrateFor
        print 'Scanner user output: ',args
        sc1.addUserOutput(*args)
        sc1.Run()  
        print sc1.UserOutputResults          
        
        
        if len(sc1.invalid_state_list) != 0:
            newUserOutputResults = [] 
            midpart = 0 
            # the number of results between invalid steady states at the ends
            resultsperdimension = sc1.UserOutputResults.shape[1]
            startpoint = 0
            endpoint = len(sc1.UserOutputResults)
            
            #start checking for invalid states from the start
            #move startpoint forward for each NaN
            #break at first non-NaN result
            loopdone = False
            for resultarray in sc1.UserOutputResults:
                if loopdone: 
                    break
                for result in resultarray:
                    if numpy.isnan(result):
                        startpoint = startpoint + 1
                        loopdone = False
                        
                        break
                    else:
                        loopdone = True
            
            #print endpoint
            #checking for invalid states from the end
            #move endpoint backward for each NaN
            #break at first non-NaN result            
            loopdone = False
            for i in range(len(sc1.UserOutputResults)):
                if loopdone: 
                    break                 
                for result in sc1.UserOutputResults[-i-1]:
                    if numpy.isnan(result):
                        endpoint = endpoint - 1
                        loopdone = False
                        
                        break
                    else:
                        loopdone = True
            #number of results between NaN ends            
            midpart = endpoint - startpoint       
            newUserOutputResults =  sc1.UserOutputResults[startpoint:endpoint]
            newUserOutputResults = scipy.array(newUserOutputResults).reshape(midpart,resultsperdimension) 
            sc1.UserOutputResults = newUserOutputResults
    
               
                    
                
        # capture result by instantiating RateCharData class
        setattr(self, fixed, RateCharData(self, mod, fixed, args, sc1.UserOutputResults, FixProductFor, FixSubstrateFor))
        if summary:
            # test for presence of global summary filename, if present append to it
            # if absent, write new summary file for single species scan
            flag = 0
            if hasattr(self, 'summaryfile'):
                of = self.summaryfile
            else:
                of = open(os.path.join(self._psc_out_dir,self._mod+'_'+fixed+'_values.txt'),'w')
                flag = 1
                of.write('# Base model: '+self._psc_file+'\n')
                of.write('####################################\n\n')
            of.write('# Rate Characteristic scan around species: '+fixed+'\n')
            of.write('#######################################################\n')
            of.write('#### Scan Min/Max ####\n')
            of.write('Scan min: '+ str(scan_min) +'\n')  
            of.write('Scan max: '+ str(scan_max) +'\n')          
            # response coefficients
            of.write('#### Response coefficients ####\n')
            for step in getattr(mymap, fixed).isReagentOf()+getattr(mymap, fixed).isModifierOf():
                of.writelines('\\rc{'+step+'}{'+fixed+'} = '+str(mod.rc.get(step,fixed))+'\n')
            # elasticities
            of.write('#### Elasticities ####\n')
            for step in getattr(mymap, fixed).isReagentOf()+getattr(mymap, fixed).isModifierOf():
                of.writelines('\\ec{'+step+'}{'+fixed+'} = '+str(basemod.ec.get(step,fixed))+'\n')
            # steady-state values
            of.write('#### Steady-state values ####\n')
            for step in getattr(mymap, fixed).isReagentOf():
                of.writelines('\\J{'+step+'} = '+str(getattr(basemod, 'J_'+step)) +'\n')
            of.writelines('['+fixed+'] = '+str(getattr(basemod, fixed+'_ss')) +'\n')
            of.write('\n')
            if flag:
                of.close()
                del of
                flag = 0

    def doAllRateChar(self, summary=1, plot=0, data=0, solver=0):
        """
        doAllRateChar(summary=1, plot=0, data=0, solver=0)

        Does rate characteristic analysis for all variable species of a model
        by calling doRateChar() for each one.

        Arguments:
        ==========
        summary (bool) - write summary to output file (default 1)
        plot (bool)    - save plots of all rate characteristics to PNG files (default 0)
        data (bool)    - save data for all graphs to tab-delimited file (default 0)
        solver (int)   - steady-state solver to use: 0 - hybrd, 1 - fintslv, 2 - NLEQ2
        """
        if summary:
            self.summaryfile = open(os.path.join(self._psc_out_dir,self._mod+'_summary.txt'),'w')
            self.summaryfile.write('# Base model: '+self._psc_file+'\n')
            self.summaryfile.write('####################################\n\n')
        basemod = self._psc_mod
        for fixed in basemod.species:
            self.doRateChar(fixed, summary, solver)
            if plot:
                eval('self.'+fixed+'.plotElasRC(file=1)')
                eval('self.'+fixed+'.plotPartialRC(file=1)')
            if data:
                eval('self.'+fixed+'.writeDataToFile()')
        if summary:
            self.summaryfile.close()
            del self.summaryfile
        
    def getRateCharData(self,spec):
        rcd = getattr(self,spec)
        return rcd


class RateCharData:
    """Class to store rate characteristic output data """
    def __init__(self, parent, mod, fix, useroutput, scandata, FixProductFor, FixSubstrateFor):
        self.parent = parent
        self.modelfilename = self.parent._psc_file
        self.mod = mod
        self.fix = fix
        self.useroutput = useroutput
        self.scandata = scandata
        self.FixProductFor = FixProductFor
        self.FixSubstrateFor = FixSubstrateFor
        self.basemod = self.parent._psc_mod
        self.mymap = ModelMap(self.basemod)
        self.slope_range_factor = 3.0
        self.scan_min = getattr(self.basemod,fix+'_ss')/self.parent.min_concrange_factor
        self.scan_max = getattr(self.basemod,fix+'_ss')*self.parent.max_concrange_factor        
        self.flux_min = abs(self.scandata[:,1:]).min()/self.parent.min_fluxrange_factor
        self.flux_max = self.scandata[:,1:].max()*self.parent.max_fluxrange_factor
        self.scan_points = len(self.scandata)
        self.isReagentOf = getattr(self.mymap, self.fix).isReagentOf()
        self.isModifierOf = getattr(self.mymap, self.fix).isModifierOf()
        self.isProductOf = getattr(self.mymap, self.fix).isProductOf()
        self.isSubstrateOf = getattr(self.mymap, self.fix).isSubstrateOf()
        
    def _wrn(self):
        warnings.warn('This is a legacy function, use RCfigure and it\'s  functions instead',stacklevel = 2)
        
    
    def plotRateChar(self, file = 0):        
        """
        TAKE NOTE:
        This function is only included for legacy purposes. All new scripts 
        should use the figure function to create an interactive RCfigure object 
        and use the functions of that object to draw and manipulate plots.
        
        plotRateChar(file=0)

        Plot the data in the instantiated RateCharData class (fluxes vs.
        the concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """ 
        self._wrn()
        fig = self.figure()
        fig.plotRateChar(file)
        
    def plotRateCharIndiv(self, file=0):
        """
        TAKE NOTE:
        This function is only included for legacy purposes. All new scripts 
        should use the figure function to create an interactive RCfigure object 
        and use the functions of that object to draw and manipulate plots.
        
        plotRateCharIndiv(file=0)        

        Plot the data in the instantiated RateCharData class (fluxes vs.
        the concentration of the fixed species for each supply and demand flux 
        in turn).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        self._wrn()
        fig = self.figure()
        fig.plotRateCharIndiv(file)
            
    def plotElasRC(self, file=0):
        """
        TAKE NOTE:
        This function is only included for legacy purposes. All new scripts 
        should use the figure function to create an interactive RCfigure object 
        and use the functions of that object to draw and manipulate plots.
        
        plotElasRC(file=0)

        Plot the data in the instantiated RateCharData class (rates, 
        elasticities and response coefficients vs. the concentration of the 
        fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        self._wrn()
        fig = self.figure()
        fig.plotElasRC(file)
        
    def plotElasRCIndiv(self, file=0):
        """
        TAKE NOTE:
        This function is only included for legacy purposes. All new scripts 
        should use the figure function to create an interactive RCfigure object 
        and use the functions of that object to draw and manipulate plots.
        
        plotElasIndivRC(file=0)

        Plot the data in the instantiated RateCharData class (rates, 
        elasticities [sans modifier elasticities] and response coefficients vs. 
        the concentration of the fixed species for each supply and demand 
        reaction in turn).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        self._wrn()
        fig = self.figure()
        fig.plotElasRCIndiv(file)
        
    def plotPartialRCSupply(self, file=0):
        """
        TAKE NOTE:
        This function is only included for legacy purposes. All new scripts 
        should use the figure function to create an interactive RCfigure object 
        and use the functions of that object to draw and manipulate plots.
        
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class for supply 
        reactions (fluxes and partial response coefficients vs. the 
        concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """  
        self._wrn()      
        fig = self.figure()
        fig.plotPartialRCSupply(file)
        
    
        
    def plotPartialRCDemand(self, file=0):
        """
        TAKE NOTE:
        This function is only included for legacy purposes. All new scripts 
        should use the figure function to create an interactive RCfigure object 
        and use the functions of that object to draw and manipulate plots.
        
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class for demand 
        reactions (fluxes and partial response coefficients vs. the 
        concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """  
        self._wrn()      
        fig = self.figure()
        fig.plotPartialRCDemand(file)
        
    def plotPartialRCIndiv(self, file=0):
        """
        TAKE NOTE:
        This function is only included for legacy purposes. All new scripts 
        should use the figure function to create an interactive RCfigure object 
        and use the functions of that object to draw and manipulate plots.
        
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class for each reaction
        in turn (fluxes and partial response coefficients vs. the 
        concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """  
        self._wrn()      
        fig = self.figure()
        fig.plotPartialRCIndiv(file)
        
         
    
    def findRegulatory(self, regTolerance = 3):
        
        """
        Returns a list of reactions for which the current fixed metabolite is
        a regulatory metabolite eg. Elasticity = Response Coefficient. This is 
        measured as an angle between the elasticity coefficient and the response
        coefficient 
        
        Arguments:
        ==========
        regTolerance (double) - the tolerance in degrees
        """
        regulatoryFor = []
        for step in getattr(self.mymap, self.fix).isReagentOf():
            ec_slope = self.basemod.ec.get(step,self.fix)
            rc_slope = self.mod.rc.get(step, self.fix)
            
            angleBetween = scipy.Infinity
            a = scipy.rad2deg(scipy.arctan(ec_slope))
            b = scipy.rad2deg(scipy.arctan(rc_slope))
            
            if ec_slope > 0 and rc_slope > 0:
                angleBetween = abs(a-b)
            elif ec_slope < 0 and rc_slope < 0:
                angleBetween = abs(abs(a)-abs(b))
            elif ec_slope < 0 or rc_slope <0:
                angleBetween = abs(a) + abs(b)
            #print angleBetween
            if angleBetween < regTolerance:
                regulatoryFor.append(step)
        return regulatoryFor
    
    '''
    def plotRateChar(self, file=0):
        
        filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+self.fix+'_flux.png')
        ioff()
        fig=figure(num=1,figsize=(12.80,10.24))
        fig.clf()
        ax=fig.add_subplot(111)
        
        # Rate Characteristics
        # supply plots
        for column in range(len(self.FixProductFor)):
            ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2)
                                                    # blue for supply
            
            
        if len(self.FixProductFor)>1:
            res_sup=numpy.zeros(self.scan_points)
            for flux in range(len(self.FixProductFor)):
                res_sup += self.scandata[:,flux+1]
            ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2)

        # demand plots
        for column in range(len(self.FixSubstrateFor)):
            ax.plot(self.scandata[:,0],self.scandata[:,column+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2)
                                                # dark green for demand
        if len(self.FixSubstrateFor)>1:
            res_dem=numpy.zeros(self.scan_points)
            for flux in range(len(self.FixSubstrateFor)):
                res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
            ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2)
            
        fix_ss = getattr(self.basemod,self.fix+'_ss')   
        ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)    
        
        # graph settings
        ax.loglog()
        ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
        ax.set_title('Model: '+self.parent._mod+' - Rate Characteristic')
        ax.set_xlabel('$Fixed: ['+self.fix+']$')
        ax.set_ylabel('$Flux$')
        if file:
            fig.savefig(filename)
        else:
            show()
    
            
    def plotRateCharIndiv(self, file=0):
        """
        plotRateCharIndiv(file=0)

        Plot the data in the instantiated RateCharData class (fluxes vs.
        the concentration of the fixed species for each supply and demand flux pair).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        
        

        # Rate Characteristics
        # supply plots
        for column in range(len(self.FixProductFor)):         
                                                                            
            # demand plots
            for column1 in range(len(self.FixSubstrateFor)):
                
                supplyVSdemand = self.FixProductFor[column] + '_' + self.FixSubstrateFor[column1]
                filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+self.fix+ '_' + supplyVSdemand +'_flux.png')
                                                                #Filename = modelName_FixedSpecies_SupplyReaction_DemandReaction_flux
                ioff()
                fig=figure(num=1,figsize=(12.80,10.24))
                fig.clf()
                ax=fig.add_subplot(111)
                ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2, label= self.FixProductFor[column] )
                                                                # blue for supply
                ax.plot(self.scandata[:,0],self.scandata[:,column1+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2,label=self.FixSubstrateFor[column1])
                                                                # dark green for demand
                if len(self.FixProductFor)>1:
                    res_sup=numpy.zeros(self.scan_points)
                    for flux in range(len(self.FixProductFor)):
                        res_sup += self.scandata[:,flux+1]
                    ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2,label='Combined Supply Flux')

                if len(self.FixSubstrateFor)>1:
                    res_dem=numpy.zeros(self.scan_points)
                    for flux in range(len(self.FixSubstrateFor)):
                        res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
                    ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2,label='Combined Demand Flux')
                fix_ss = getattr(self.basemod,self.fix+'_ss')
                ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)
            # graph settings
                ax.loglog()
                ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
                ax.set_title('Model: '+self.parent._mod+' - Rate Characteristic')
                ax.set_xlabel('$Fixed: ['+self.fix+']$')
                ax.set_ylabel('$Flux$')
                ax.legend(loc=0)
                if file:
                    fig.savefig(filename)
                else:
                    show()
         
    
    
               
                
            
        
            
    


    def plotElasRC(self, file=0):
        """
        plotElasRC(file=0)

        Plot the data in the instantiated RateCharData class (rates, elasticities and
        response coefficients vs. the concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+self.fix+'_ElasRC.png')
        ioff()
        fig=figure(num=1,figsize=(8.0,6.0))
        fig.clf()
        ax=fig.add_subplot(111)
        #lastelement = len(self.scandata[:,0]) - 1

        # Rate Characteristics
        # supply plots
        for column in range(len(self.FixProductFor)):
            ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2)
                                                                # blue for supply
            

        if len(self.FixProductFor)>1:
            res_sup=numpy.zeros(self.scan_points)
            for flux in range(len(self.FixProductFor)):
                res_sup += self.scandata[:,flux+1]
            ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2)

        # demand plots
        for column in range(len(self.FixSubstrateFor)):
            ax.plot(self.scandata[:,0],self.scandata[:,column+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2)
                                                                # dark green for demand
            

        if len(self.FixSubstrateFor)>1:
            res_dem=numpy.zeros(self.scan_points)
            for flux in range(len(self.FixSubstrateFor)):
                res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
            ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2)

        # Elasticities
        for step in getattr(self.mymap, self.fix).isReagentOf()+getattr(self.mymap, self.fix).isModifierOf():
            J_ss = getattr(self.basemod,'J_'+step)
            fix_ss = getattr(self.basemod,self.fix+'_ss')
            ec_slope = self.basemod.ec.get(step,self.fix)
            ec_constant = J_ss/(fix_ss**ec_slope)
            range_min = fix_ss/self.slope_range_factor
            range_max = fix_ss*self.slope_range_factor
            stepsize = fix_ss
            fix_conc = numpy.arange(range_min, range_max, stepsize)
            ec_rate = ec_constant * fix_conc**(ec_slope)
            if step in getattr(self.mymap, self.fix).isProductOf():
                ax.plot(fix_conc, ec_rate, color='#bbbbff', lw=3)
                                                # supply elasticity light blue
            elif step in getattr(self.mymap, self.fix).isSubstrateOf():
                ax.plot(fix_conc, ec_rate, color='#88ff88', lw=3)
                                                # demand elasticity light green
            elif step in getattr(self.mymap, self.fix).isModifierOf():
                ax.plot(fix_conc, ec_rate, color='#ff8000', lw=3)
                                                # modifier elasticity orange

        # Response coefficients
        for step in getattr(self.mymap, self.fix).isReagentOf():
            J_ss = getattr(self.basemod,'J_'+step)
            fix_ss = getattr(self.basemod,self.fix+'_ss')
            rc_slope = self.mod.rc.get(step, self.fix)
            rc_constant = J_ss/(fix_ss**rc_slope)
            range_min = fix_ss/self.slope_range_factor
            range_max = fix_ss*self.slope_range_factor
            stepsize = fix_ss
            fix_conc = numpy.arange(range_min, range_max, stepsize)
            rc_rate = rc_constant * fix_conc**(rc_slope)
            if step in getattr(self.mymap, self.fix).isProductOf():
                ax.plot(fix_conc, rc_rate, '--', color='#000080', lw=2)
                                                        # supply resp coeff dark blue
            elif step in getattr(self.mymap, self.fix).isSubstrateOf():
                ax.plot(fix_conc, rc_rate, '--', color='#006000', lw=2)
                                                        # demand resp coeff very dark green

        # vertical line at steady-state value
        
        ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)        

        # graph settings
        ax.loglog()
        ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
        ax.set_title('Model: '+self.parent._mod+' - Response vs. elasticity coefficients')
        ax.set_xlabel('$Fixed: ['+self.fix+']$')
        ax.set_ylabel('$Flux$')
        if file:
            fig.savefig(filename)
        else:
            show()
            
    
            
    def plotElasRCIndiv(self, file=0):
        """
        plotElasIndivRC(file=0)

        Plot the data in the instantiated RateCharData class (rates, elasticities (sans modifier elasticities) and
        response coefficients vs. the concentration of the fixed species for each supply and demand reaction pair).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
                              
        for column in range(len(self.FixProductFor)):         
                                                                            
            # demand plots
            for column1 in range(len(self.FixSubstrateFor)):
                
                supplyVSdemand = self.FixProductFor[column] + '_' + self.FixSubstrateFor[column1]
                                    
                filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+ self.fix+'_' + supplyVSdemand +'_ElasRCIndiv.png')
                #Filename = modelName_FixedSpecies_SupplyReaction_DemandReaction_ElasRCIndiv
                ioff()
                fig=figure(num=1,figsize=(12.80,10.24))
                fig.clf()
                ax=fig.add_subplot(111)
                ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2, label=self.FixProductFor[column])
                                                                # blue for supply
                ax.plot(self.scandata[:,0],self.scandata[:,column1+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2,label=self.FixSubstrateFor[column1])
                                                                # dark green for demand
                if len(self.FixProductFor)>1:
                    res_sup=numpy.zeros(self.scan_points)
                    for flux in range(len(self.FixProductFor)):
                        res_sup += self.scandata[:,flux+1]
                    ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2,label='Combined Supply Flux')

                if len(self.FixSubstrateFor)>1:
                    res_dem=numpy.zeros(self.scan_points)
                    for flux in range(len(self.FixSubstrateFor)):
                        res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
                    ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2,label='Combined Demand Flux')
                
                # Elasticities
                for step in getattr(self.mymap, self.fix).isReagentOf():
                    J_ss = getattr(self.basemod,'J_'+step)
                    fix_ss = getattr(self.basemod,self.fix+'_ss')
                    ec_slope = self.basemod.ec.get(step,self.fix)
                    ec_constant = J_ss/(fix_ss**ec_slope)
                    range_min = fix_ss/self.slope_range_factor
                    range_max = fix_ss*self.slope_range_factor
                    stepsize = fix_ss
                    fix_conc = numpy.arange(range_min, range_max, stepsize)
                    ec_rate = ec_constant * fix_conc**(ec_slope)
                    if step in getattr(self.mymap, self.fix).isProductOf() and step == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                        ax.plot(fix_conc, ec_rate, color='#bbbbff', lw=3,label = 'Supply Elasticity')
                                                # supply elasticity light blue
                    elif step in getattr(self.mymap, self.fix).isSubstrateOf() and step == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                        ax.plot(fix_conc, ec_rate, color='#88ff88', lw=3, label= 'Demand Elasticity')
                                                # demand elasticity light green
                    
                            
                                                
                    # Response coefficients
                for step in getattr(self.mymap, self.fix).isReagentOf():
                    J_ss = getattr(self.basemod,'J_'+step)
                    fix_ss = getattr(self.basemod,self.fix+'_ss')
                    rc_slope = self.mod.rc.get(step, self.fix)
                    rc_constant = J_ss/(fix_ss**rc_slope)
                    range_min = fix_ss/self.slope_range_factor
                    range_max = fix_ss*self.slope_range_factor
                    stepsize = fix_ss
                    fix_conc = numpy.arange(range_min, range_max, stepsize)
                    rc_rate = rc_constant * fix_conc**(rc_slope)
                    if step in getattr(self.mymap, self.fix).isProductOf() and step  == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                        ax.plot(fix_conc, rc_rate, '--', color='#000080', lw=2, label='Supply Response Coefficient')
                                                                # supply resp coeff dark blue
                    elif step in getattr(self.mymap, self.fix).isSubstrateOf() and step == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                        ax.plot(fix_conc, rc_rate, '--', color='#006000', lw=2, label='Demand Response Coefficient')
                                                                # demand resp coeff very dark green
                
            # vertical line at steady-state value
                
                
                ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)
            # graph settings
            
                ax.loglog()
                ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
                ax.set_title('Model: '+self.parent._mod+' - Response vs. elasticity coefficients')
                ax.set_xlabel('$Fixed: ['+self.fix+']$')
                ax.set_ylabel('$Flux$')
                ax.legend(loc=0)
                if file:
                    fig.savefig(filename)
                else:
                    show()
                    
    
                    
    def plotElasRCModIndiv(self, file=0):
        """
        plotElasRCModIndiv(file=0)

        Plots the total demand and supply fluxes and modifier elasticities
        against the fixed species.

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
                              
             
                                                                            
        for step in getattr(self.mymap, self.fix).isModifierOf():                       
                               
            filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+ self.fix+ '_' + step +'_ElasRCModIndiv.png')
            ioff()
            fig=figure(num=1,figsize=(12.80,10.24))
            fig.clf()
            ax=fig.add_subplot(111)
            
            
            if len(self.FixProductFor)>1:
                res_sup=numpy.zeros(self.scan_points)
                for flux in range(len(self.FixProductFor)):
                    res_sup += self.scandata[:,flux+1]
                ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2,label='Combined Supply Flux')
            else:
                ax.plot(self.scandata[:,0],self.scandata[:,1], '-', color='#0000ff', linewidth=2, label=self.FixProductFor[0])
                                                            # blue for supply    

            if len(self.FixSubstrateFor)>1:
                res_dem=numpy.zeros(self.scan_points)
                for flux in range(len(self.FixSubstrateFor)):
                    res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
                ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2,label='Combined Demand Flux')
            else:
                ax.plot(self.scandata[:,0],self.scandata[:,len(self.FixProductFor)+1], '-', color='#008000', linewidth=2,label=self.FixSubstrateFor[0])
                                                            # dark green for demand
            
            # Elasticities
            
            J_ss = getattr(self.basemod,'J_'+step)
            fix_ss = getattr(self.basemod,self.fix+'_ss')
            ec_slope = self.basemod.ec.get(step,self.fix)
            ec_constant = J_ss/(fix_ss**ec_slope)
            range_min = fix_ss/self.slope_range_factor
            range_max = fix_ss*self.slope_range_factor
            stepsize = fix_ss
            fix_conc = numpy.arange(range_min, range_max, stepsize)
            ec_rate = ec_constant * fix_conc**(ec_slope)                 
            
            ax.plot(fix_conc, ec_rate, color='#ff8000', lw=3,label= 'Modifier elasticity for ' + step)
                                            # modifier elasticity orange
                                            
                
                        
            
        # vertical line at steady-state value                
            J_ss = getattr(self.basemod,'J_'+step)
            fix_ss = getattr(self.basemod,self.fix+'_ss')
            ec_slope = self.basemod.ec.get(step,self.fix)
            ec_constant = J_ss/(fix_ss**ec_slope)
            range_min = fix_ss/self.slope_range_factor
            range_max = fix_ss*self.slope_range_factor
            stepsize = fix_ss
            fix_conc = numpy.arange(range_min, range_max, stepsize)
            ec_rate = ec_constant * fix_conc**(ec_slope)                 
            
            ax.plot(fix_conc, ec_rate, color='#ff8000', lw=3)

            
            
            ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)
        # graph settings
        
            ax.loglog()
            ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
            ax.set_title('Model: '+self.parent._mod+' - Modifier Elasticities')
            ax.set_xlabel('$Fixed: ['+self.fix+']$')
            ax.set_ylabel('$Flux $')
            ax.legend(loc=0)
            if file:
                fig.savefig(filename)
            else:
                show()

    

    def plotPartialRC(self, file=0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class (fluxes and partial
        response coefficients vs. the concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+self.fix+'_partialRC.png')
        ioff()
        fig=figure(num=1,figsize=(12.80,10.24))
        fig.clf()
        ax1=fig.add_subplot(121)        # for supply
        ax2=fig.add_subplot(122)        # for demand

        # Rate Characteristics
        # supply plots
        for column in range(len(self.FixProductFor)):
            ax1.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2)
            ax2.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2)
                                                                # blue for supply
        if len(self.FixProductFor)>1:
            res_sup=numpy.zeros(self.scan_points)
            for flux in range(len(self.FixProductFor)):
                res_sup += self.scandata[:,flux+1]
            ax1.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2)
            ax2.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2)

        # demand plots
        for column in range(len(self.FixSubstrateFor)):
            ax1.plot(self.scandata[:,0],self.scandata[:,column+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2)
            ax2.plot(self.scandata[:,0],self.scandata[:,column+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2)
                                                                # dark green for demand
        if len(self.FixSubstrateFor)>1:
            res_dem=numpy.zeros(self.scan_points)
            for flux in range(len(self.FixSubstrateFor)):
                res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
            ax1.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2)
            ax2.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2)

        # partial response coefficients
        # first loop over supply fluxes
        for sup in getattr(self.mymap, self.fix).isProductOf():
            J_ss = getattr(self.basemod,'J_'+sup)
            fix_ss = getattr(self.basemod,self.fix+'_ss')
            # now get all possible partial RCs on that flux
            for step in getattr(self.mymap, self.fix).isReagentOf()+getattr(self.mymap, self.fix).isModifierOf():
                prc_slope = self.basemod.ec.get(step,self.fix)*self.mod.cc.get(sup,step)
                prc_constant = J_ss/(fix_ss**prc_slope)
                range_min = fix_ss/self.slope_range_factor
                range_max = fix_ss*self.slope_range_factor
                stepsize = fix_ss
                fix_conc = numpy.arange(range_min, range_max, stepsize)
                prc_rate = prc_constant * fix_conc**(prc_slope)
                if abs(prc_slope) > 0.01:    # only plot nonzero partial RCs
                    if step in getattr(self.mymap, self.fix).isProductOf():
                        ax1.plot(fix_conc, prc_rate, color='#bbbbff', lw=3)
                                                        # supply partial RC light blue
                    elif step in getattr(self.mymap, self.fix).isSubstrateOf():
                        ax1.plot(fix_conc, prc_rate, color='#88ff88', lw=3)
                                                        # demand partial RC light green
                    elif step in getattr(self.mymap, self.fix).isModifierOf():
                        ax1.plot(fix_conc, prc_rate, color='#ff8000', lw=3)
                                                        # modifier partial RC orange
        # next loop over demand fluxes
        for dem in getattr(self.mymap, self.fix).isSubstrateOf():
            J_ss = getattr(self.basemod,'J_'+dem)
            fix_ss = getattr(self.basemod,self.fix+'_ss')
            # now get all possible partial RCs on that flux
            for step in getattr(self.mymap, self.fix).isReagentOf()+getattr(self.mymap, self.fix).isModifierOf():
                prc_slope = self.basemod.ec.get(step,self.fix)*self.mod.cc.get(dem,step)
                prc_constant = J_ss/(fix_ss**prc_slope)
                range_min = fix_ss/self.slope_range_factor
                range_max = fix_ss*self.slope_range_factor
                stepsize = fix_ss
                fix_conc = numpy.arange(range_min, range_max, stepsize)
                prc_rate = prc_constant * fix_conc**(prc_slope)
                if abs(prc_slope) > 0.01:    # only plot nonzero partial RCs
                    if step in getattr(self.mymap, self.fix).isProductOf():
                        ax2.plot(fix_conc, prc_rate, color='#bbbbff', lw=3)
                                                        # supply partial RC light blue
                    elif step in getattr(self.mymap, self.fix).isSubstrateOf():
                        ax2.plot(fix_conc, prc_rate, color='#88ff88', lw=3)
                                                        # demand partial RC light green
                    elif step in getattr(self.mymap, self.fix).isModifierOf():
                        ax2.plot(fix_conc, prc_rate, color='#ff8000', lw=3)
                                                        # modifier partial RC orange
        # Complete response coefficients
        for step in getattr(self.mymap, self.fix).isReagentOf():
            J_ss = getattr(self.basemod,'J_'+step)
            fix_ss = getattr(self.basemod,self.fix+'_ss')
            rc_slope = self.mod.rc.get(step, self.fix)
            rc_constant = J_ss/(fix_ss**rc_slope)
            range_min = fix_ss/self.slope_range_factor
            range_max = fix_ss*self.slope_range_factor
            stepsize = fix_ss
            fix_conc = numpy.arange(range_min, range_max, stepsize)
            rc_rate = rc_constant * fix_conc**(rc_slope)
            if step in getattr(self.mymap, self.fix).isProductOf():
                ax1.plot(fix_conc, rc_rate, '--', color='#000080', lw=2)
                                                        # supply resp coeff dark blue
            elif step in getattr(self.mymap, self.fix).isSubstrateOf():
                ax2.plot(fix_conc, rc_rate, '--', color='#006000', lw=2)
                                                        # demand resp coeff very dark green

        # vertical line at steady-state value
        ax1.axvline(x=fix_ss, ls=':', color='0.5', lw=1)
        ax2.axvline(x=fix_ss, ls=':', color='0.5', lw=1)
        
        # graph settings
        ax1.loglog()
        ax1.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
        ax1.set_title('supply', fontsize=12)
        ax1.set_xlabel('$Fixed: ['+self.fix+']$')
        ax1.set_ylabel('$Flux$')
        ax2.loglog()
        ax2.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
        ax2.set_title('demand', fontsize=12)
        ax2.set_xlabel('$Fixed: ['+self.fix+']$')
        ax2.set_yticklabels([])
        figtext(0.5,0.95, 'Model: '+self.parent._mod+' - Partial response coefficients', fontsize=16, horizontalalignment='center')
        if file:
            fig.savefig(filename)
        else:
            show()
     
    def plotPartialRCSupply(self, file=0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class (fluxes and partial
        response coefficients vs. the concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
            
        
        #Supply        
        

        # Rate Characteristics
        # supply plots
        for column in range(len(self.FixProductFor)):
            
                    
            # for supply
            # partial response coefficients
            # first loop over supply fluxes
            
            for sup in getattr(self.mymap, self.fix).isProductOf():
                J_ss = getattr(self.basemod,'J_'+sup)
                fix_ss = getattr(self.basemod,self.fix+'_ss')
                # now get all possible partial RCs on that flux
                for step in getattr(self.mymap, self.fix).isReagentOf()+getattr(self.mymap, self.fix).isModifierOf():
                    filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+ '_'+self.fix+'_'+self.FixProductFor[column][2:len(self.FixProductFor[column])] +'_' + str(step) + '_partialRCSupply.png')
                    ioff()
                    fig=figure(num=1,figsize=(12.80,10.24))
                    fig.clf()
                    ax=fig.add_subplot(111)                    
                    prc_slope = self.basemod.ec.get(step,self.fix)*self.mod.cc.get(sup,step)
                    prc_constant = J_ss/(fix_ss**prc_slope)
                    range_min = fix_ss/self.slope_range_factor
                    range_max = fix_ss*self.slope_range_factor
                    stepsize = fix_ss
                    fix_conc = numpy.arange(range_min, range_max, stepsize)
                    prc_rate = prc_constant * fix_conc**(prc_slope)                    
                    outputFile = False
                    if abs(prc_slope) > 0.01:    # only plot nonzero partial RCs
                        if step in getattr(self.mymap, self.fix).isProductOf() and sup == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                            ax.plot(fix_conc, prc_rate, color='#bbbbff', lw=3 , label = 'Partial response coefficient for ' + step)
                            outputFile = True
                                                            # supply partial RC light blue
                        elif step in getattr(self.mymap, self.fix).isSubstrateOf() and sup == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                            ax.plot(fix_conc, prc_rate, color='#88ff88', lw=3 , label = 'Partial response coefficient for ' + step)
                            outputFile = True
                                                            # demand partial RC light green
                        elif step in getattr(self.mymap, self.fix).isModifierOf() and sup == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                            ax.plot(fix_conc, prc_rate, color='#ff8000', lw=3 , label = 'Partial response coefficient for ' + step)
                            outputFile = True
                            
                                                            # modifier partial RC orange
                    if outputFile == True:                                        
                        ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2 , label = self.FixProductFor[column])            
                                                                            # blue for supply
                        if len(self.FixProductFor)>1:
                            res_sup=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixProductFor)):
                                res_sup += self.scandata[:,flux+1]
                            ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2 , label = 'Combined Supply Flux')
                            
                
                        # demand plots
                        for column1 in range(len(self.FixSubstrateFor)):
                            ax.plot(self.scandata[:,0],self.scandata[:,column1+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2 , label = self.FixSubstrateFor[column1])
                            
                        if len(self.FixSubstrateFor)>1:
                            res_dem=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixSubstrateFor)):
                                res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
                            ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2 , label = 'Combined Demand Flux')
                           
                                    
                        # Complete response coefficients
                        for step1 in getattr(self.mymap, self.fix).isReagentOf():
                            J_ss1 = getattr(self.basemod,'J_'+step1)
                            fix_ss1 = getattr(self.basemod,self.fix+'_ss')
                            rc_slope = self.mod.rc.get(step1, self.fix)
                            rc_constant = J_ss1/(fix_ss1**rc_slope)
                            range_min = fix_ss1/self.slope_range_factor
                            range_max = fix_ss1*self.slope_range_factor
                            stepsize = fix_ss1
                            fix_conc = numpy.arange(range_min, range_max, stepsize)
                            rc_rate = rc_constant * fix_conc**(rc_slope)
                            if step1 in getattr(self.mymap, self.fix).isProductOf() and step1 == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                                ax.plot(fix_conc, rc_rate, '--', color='#000080', lw=2 , label = 'Complete Supply Response Coefficient')
                                                                        # supply resp coeff dark blue
                            
                
                        # vertical line at steady-state value
                        ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1 )
                        
                        
                        # graph settings
                        ax.loglog()
                        ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
                        ax.set_title('supply', fontsize=12)
                        ax.set_xlabel('$Fixed: ['+self.fix+']$')
                        ax.set_ylabel('$Flux$')   
                        ax.legend(loc=0)     
                        figtext(0.5,0.95, 'Model: '+self.parent._mod+' - Partial response coefficients - Supply', fontsize=16, horizontalalignment='center')
                        outputFile = False
                        if file:
                            fig.savefig(filename)
                        else:
                            show()
                            
    def plotPartialRCDemand(self, file=0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class (fluxes and partial
        response coefficients vs. the concentration of the fixed species for each 
        supply and demand reaction pair).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        
        
        for column1 in range(len(self.FixSubstrateFor)):
            # next loop over demand fluxes
            for dem in getattr(self.mymap, self.fix).isSubstrateOf():
                J_ss = getattr(self.basemod,'J_'+dem)
                fix_ss = getattr(self.basemod,self.fix+'_ss')
                # now get all possible partial RCs on that flux
                for step in getattr(self.mymap, self.fix).isReagentOf()+getattr(self.mymap, self.fix).isModifierOf():
                    filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+self.fix+ '_' + self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])] + '_' +  str(step) +'_partialRCDemand.png')
                    ioff()
                    fig=figure(num=1,figsize=(12.80,10.24))
                    fig.clf()            
                    ax=fig.add_subplot(111)        # for demand
                    prc_slope = self.basemod.ec.get(step,self.fix)*self.mod.cc.get(dem,step)
                    prc_constant = J_ss/(fix_ss**prc_slope)
                    range_min = fix_ss/self.slope_range_factor
                    range_max = fix_ss*self.slope_range_factor
                    stepsize = fix_ss
                    fix_conc = numpy.arange(range_min, range_max, stepsize)
                    prc_rate = prc_constant * fix_conc**(prc_slope)
                    outputFile = False
                    if abs(prc_slope) > 0.01:    # only plot nonzero partial RCs
                        if step in getattr(self.mymap, self.fix).isProductOf() and dem == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                            ax.plot(fix_conc, prc_rate, color='#bbbbff', lw=3, label = 'Partial response coefficient for ' + step)
                            outputFile = True
                                                            # supply partial RC light blue
                        elif step in getattr(self.mymap, self.fix).isSubstrateOf() and dem == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                            ax.plot(fix_conc, prc_rate, color='#88ff88', lw=3, label = 'Partial response coefficient for ' + step)
                            outputFile = True
                                                            # demand partial RC light green
                        elif step in getattr(self.mymap, self.fix).isModifierOf() and dem == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                            ax.plot(fix_conc, prc_rate, color='#ff8000', lw=3, label = 'Partial response coefficient for ' + step)
                            outputFile = True
                                                            # modifier partial RC orange
            
                    if outputFile == True:
                        # Rate Characteristics
                        # supply plots
                        for column in range(len(self.FixProductFor)):                            
                            ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2,label = self.FixProductFor[column])
                                                                                # blue for supply
                        
                        if len(self.FixProductFor)>1:
                            res_sup=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixProductFor)):
                                res_sup += self.scandata[:,flux+1]
                            ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2, label = 'Combined Supply Flux')
                
                        # demand plots
                        
                            
                        ax.plot(self.scandata[:,0],self.scandata[:,column1+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2, label = self.FixSubstrateFor[column1])
                                                                                # dark green for demand
                        if len(self.FixSubstrateFor)>1:
                            res_dem=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixSubstrateFor)):
                                res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]                           
                            ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2, label = 'Combined Demand Flux')
                
                        # partial response coefficients
                        # first loop over supply fluxes
                        
                        
                        # Complete response coefficients
                        for step1 in getattr(self.mymap, self.fix).isReagentOf():
                            J_ss1 = getattr(self.basemod,'J_'+step1)
                            fix_ss1 = getattr(self.basemod,self.fix+'_ss')
                            rc_slope = self.mod.rc.get(step1, self.fix)
                            rc_constant = J_ss1/(fix_ss1**rc_slope)
                            range_min = fix_ss1/self.slope_range_factor
                            range_max = fix_ss1*self.slope_range_factor
                            stepsize = fix_ss1
                            fix_conc = numpy.arange(range_min, range_max, stepsize)
                            rc_rate = rc_constant * fix_conc**(rc_slope)                            
                            if step1 in getattr(self.mymap, self.fix).isSubstrateOf() and step1 == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                                ax.plot(fix_conc, rc_rate, '--', color='#006000', lw=2, label = 'Complete Response Coefficient')
                                                                        # demand resp coeff very dark green
                
                        # vertical line at steady-state value
                        
                        ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)
                        
                        # graph settings
                        
                        ax.set_ylabel('$Flux$')
                        ax.loglog()
                        ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
                        ax.set_title('demand', fontsize=12)
                        ax.set_xlabel('$Fixed: ['+self.fix+']$')
                        ax.legend(loc=0)     
                        figtext(0.5,0.95, 'Model: '+self.parent._mod+' - Partial response coefficients - Demand', fontsize=16, horizontalalignment='center')
                        outputFile = False
                        if file:
                            fig.savefig(filename)
                        else:
                            show()    
                            
    def plotPartialRCSupplyAll(self, file=0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class (fluxes and partial
        response coefficients vs. the concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
            
        
        #Supply        
        

        # Rate Characteristics
        # supply plots
        for column in range(len(self.FixProductFor)):
            
                    
            # for supply
            # partial response coefficients
            # first loop over supply fluxes
            
            for sup in getattr(self.mymap, self.fix).isProductOf():
                J_ss = getattr(self.basemod,'J_'+sup)
                fix_ss = getattr(self.basemod,self.fix+'_ss')
                # now get all possible partial RCs on that flux
                for step in getattr(self.mymap, self.fix).isReagentOf()+getattr(self.mymap, self.fix).isModifierOf():
                    filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+ '_'+self.fix+'_'+self.FixProductFor[column][2:len(self.FixProductFor[column])] +'_' + str(step) + '_partialRCSupplyAll.png')
                    ioff()
                    fig=figure(num=1,figsize=(12.80,10.24))
                    fig.clf()
                    ax=fig.add_subplot(111)                    
                    prc_slope = self.basemod.ec.get(step,self.fix)*self.mod.cc.get(sup,step)
                    prc_constant = J_ss/(fix_ss**prc_slope)
                    range_min = fix_ss/self.slope_range_factor
                    range_max = fix_ss*self.slope_range_factor
                    stepsize = fix_ss
                    fix_conc = numpy.arange(range_min, range_max, stepsize)
                    prc_rate = prc_constant * fix_conc**(prc_slope)                    
                    outputFile = False
                    
                    if step in getattr(self.mymap, self.fix).isProductOf() and sup == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                        ax.plot(fix_conc, prc_rate, color='#bbbbff', lw=3 , label = 'Partial response coefficient for ' + step)
                        outputFile = True
                                                        # supply partial RC light blue
                    elif step in getattr(self.mymap, self.fix).isSubstrateOf() and sup == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                        ax.plot(fix_conc, prc_rate, color='#88ff88', lw=3 , label = 'Partial response coefficient for ' + step)
                        outputFile = True
                                                        # demand partial RC light green
                    elif step in getattr(self.mymap, self.fix).isModifierOf() and sup == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                        ax.plot(fix_conc, prc_rate, color='#ff8000', lw=3 , label = 'Partial response coefficient for ' + step)
                        outputFile = True
                            
                                                            # modifier partial RC orange
                    if outputFile == True:                                        
                        ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2 , label = self.FixProductFor[column])            
                                                                            # blue for supply
                        if len(self.FixProductFor)>1:
                            res_sup=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixProductFor)):
                                res_sup += self.scandata[:,flux+1]
                            ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2 , label = 'Combined Supply Flux')
                            
                
                        # demand plots
                        for column1 in range(len(self.FixSubstrateFor)):
                            ax.plot(self.scandata[:,0],self.scandata[:,column1+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2 , label = self.FixSubstrateFor[column1])
                            
                        if len(self.FixSubstrateFor)>1:
                            res_dem=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixSubstrateFor)):
                                res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]
                            ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2 , label = 'Combined Demand Flux')
                           
                                    
                        # Complete response coefficients
                        for step1 in getattr(self.mymap, self.fix).isReagentOf():
                            J_ss1 = getattr(self.basemod,'J_'+step1)
                            fix_ss1 = getattr(self.basemod,self.fix+'_ss')
                            rc_slope = self.mod.rc.get(step1, self.fix)
                            rc_constant = J_ss1/(fix_ss1**rc_slope)
                            range_min = fix_ss1/self.slope_range_factor
                            range_max = fix_ss1*self.slope_range_factor
                            stepsize = fix_ss1
                            fix_conc = numpy.arange(range_min, range_max, stepsize)
                            rc_rate = rc_constant * fix_conc**(rc_slope)
                            if step1 in getattr(self.mymap, self.fix).isProductOf() and step1 == self.FixProductFor[column][2:len(self.FixProductFor[column])]:
                                ax.plot(fix_conc, rc_rate, '--', color='#000080', lw=2 , label = 'Complete Supply Response Coefficient')
                                                                        # supply resp coeff dark blue
                            
                
                        # vertical line at steady-state value
                        ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1 )
                        
                        
                        # graph settings
                        ax.loglog()
                        ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
                        ax.set_title('supply', fontsize=12)
                        ax.set_xlabel('$Fixed: ['+self.fix+']$')
                        ax.set_ylabel('$Flux$')   
                        ax.legend(loc=0)     
                        figtext(0.5,0.95, 'Model: '+self.parent._mod+' - Partial response coefficients - Supply', fontsize=16, horizontalalignment='center')
                        outputFile = False
                        if file:
                            fig.savefig(filename)
                        else:
                            show()
                            
    def plotPartialRCDemandAll(self, file=0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class (fluxes and partial
        response coefficients vs. the concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        
        
        for column1 in range(len(self.FixSubstrateFor)):
            # next loop over demand fluxes
            for dem in getattr(self.mymap, self.fix).isSubstrateOf():
                J_ss = getattr(self.basemod,'J_'+dem)
                fix_ss = getattr(self.basemod,self.fix+'_ss')
                # now get all possible partial RCs on that flux
                for step in getattr(self.mymap, self.fix).isReagentOf()+getattr(self.mymap, self.fix).isModifierOf():
                    filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+self.fix+ '_' + self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])] + '_' +  str(step) +'_partialRCDemandAll.png')
                    ioff()
                    fig=figure(num=1,figsize=(12.80,10.24))
                    fig.clf()            
                    ax=fig.add_subplot(111)        # for demand
                    prc_slope = self.basemod.ec.get(step,self.fix)*self.mod.cc.get(dem,step)
                    prc_constant = J_ss/(fix_ss**prc_slope)
                    range_min = fix_ss/self.slope_range_factor
                    range_max = fix_ss*self.slope_range_factor
                    stepsize = fix_ss
                    fix_conc = numpy.arange(range_min, range_max, stepsize)
                    prc_rate = prc_constant * fix_conc**(prc_slope)
                    outputFile = False
                    
                    if step in getattr(self.mymap, self.fix).isProductOf() and dem == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                        ax.plot(fix_conc, prc_rate, color='#bbbbff', lw=3, label = 'Partial response coefficient for ' + step)
                        outputFile = True
                                                        # supply partial RC light blue
                    elif step in getattr(self.mymap, self.fix).isSubstrateOf() and dem == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                        ax.plot(fix_conc, prc_rate, color='#88ff88', lw=3, label = 'Partial response coefficient for ' + step)
                        outputFile = True
                                                        # demand partial RC light green
                    elif step in getattr(self.mymap, self.fix).isModifierOf() and dem == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                        ax.plot(fix_conc, prc_rate, color='#ff8000', lw=3, label = 'Partial response coefficient for ' + step)
                        outputFile = True
                                                            # modifier partial RC orange
            
                    if outputFile == True:
                        # Rate Characteristics
                        # supply plots
                        for column in range(len(self.FixProductFor)):                            
                            ax.plot(self.scandata[:,0],self.scandata[:,column+1], '-', color='#0000ff', linewidth=2,label = self.FixProductFor[column])
                                                                                # blue for supply
                        
                        if len(self.FixProductFor)>1:
                            res_sup=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixProductFor)):
                                res_sup += self.scandata[:,flux+1]
                            ax.plot(self.scandata[:,0], res_sup, '--', color='#00c0c0', linewidth=2, label = 'Combined Supply Flux')
                
                        # demand plots
                        
                            
                        ax.plot(self.scandata[:,0],self.scandata[:,column1+len(self.FixProductFor)+1], '-', color='#008000', linewidth=2, label = self.FixSubstrateFor[column1])
                                                                                # dark green for demand
                        if len(self.FixSubstrateFor)>1:
                            res_dem=numpy.zeros(self.scan_points)
                            for flux in range(len(self.FixSubstrateFor)):
                                res_dem += self.scandata[:,flux+len(self.FixProductFor)+1]                           
                            ax.plot(self.scandata[:,0], res_dem, '--', color='#00c000', linewidth=2, label = 'Combined Demand Flux')
                
                        # partial response coefficients
                        # first loop over supply fluxes
                        
                        
                        # Complete response coefficients
                        for step1 in getattr(self.mymap, self.fix).isReagentOf():
                            J_ss1 = getattr(self.basemod,'J_'+step1)
                            fix_ss1 = getattr(self.basemod,self.fix+'_ss')
                            rc_slope = self.mod.rc.get(step1, self.fix)
                            rc_constant = J_ss1/(fix_ss1**rc_slope)
                            range_min = fix_ss1/self.slope_range_factor
                            range_max = fix_ss1*self.slope_range_factor
                            stepsize = fix_ss1
                            fix_conc = numpy.arange(range_min, range_max, stepsize)
                            rc_rate = rc_constant * fix_conc**(rc_slope)                            
                            if step1 in getattr(self.mymap, self.fix).isSubstrateOf() and step1 == self.FixSubstrateFor[column1][2:len(self.FixSubstrateFor[column1])]:
                                ax.plot(fix_conc, rc_rate, '--', color='#006000', lw=2, label = 'Complete Response Coefficient')
                                                                        # demand resp coeff very dark green
                
                        # vertical line at steady-state value
                        
                        ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)
                        
                        # graph settings
                        
                        ax.set_ylabel('$Flux$')
                        ax.loglog()
                        ax.axis([self.scan_min, self.scan_max, self.flux_min, self.flux_max])
                        ax.set_title('demand', fontsize=12)
                        ax.set_xlabel('$Fixed: ['+self.fix+']$')
                        ax.legend(loc=0)     
                        figtext(0.5,0.95, 'Model: '+self.parent._mod+' - Partial response coefficients - Demand', fontsize=16, horizontalalignment='center')
                        outputFile = False
                        if file:
                            fig.savefig(filename)
                        else:
                            show()
                            
        '''
                        
    def writeDataToFile(self):

        """
        writeDataToFile()

        Write the data in the instantiated RateCharData class (concentration of fixed
        species and fluxes of all adjoining reactions) to a tab-delimited CSV file.

        Arguments:
        ==========
        None
        """
        filename = os.path.join(self.parent._psc_out_dir, self.modelfilename[:-4]+'_'+self.fix+'_data.txt')
        of = open(filename, 'w')
        of.write('# Base model: '+self.modelfilename+'\n')
        of.write('# Rate Characteristic scan around species: '+self.fix+'\n')
        of.write('##########################################\n#')
        for i in self.useroutput:
            of.write(i+'\t')
        of.write('\n')
	numpy.savetxt(of,self.scandata,fmt='%05.2f',delimiter = '\t')
        #scipy.io.write_array(of, self.scandata, separator='\t', keep_open=0)
      
    def figure(self):
        """
        Returns an object of the RcFigure class with the current object as it's
        parent. This object has a variety of functions to plot the rate
        characteristic data interactively.
    
        """
        
        return RcFigure(self)
        
        
class RcFigure:
    def __init__(self,parent):
        ioff()
        self.parent = parent
        self.figure = figure(num=1,figsize=(12.80,10.24))
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)
        
        self.huelist = [0.0000000,
                        0.3333333,
                        0.6666666,
                        0.1666666,
                        0.4999999,
                        0.8333333,
                        0.0833333,
                        0.4166666,
                        0.7499999,        
                        0.2499999,
                        0.5833333,
                        0.9166666]
        self.huedict = self._assign_hue()        
        self.reactions = self._reactions()
        self.supply_flux, self.demand_flux = self._plot_flux()        
        self.reaction_flux = dict(self.supply_flux.items() + 
                                self.demand_flux.items()) 
        
        self.supply_partial_rc, self.demand_partial_rc = self._plot_partial_rc()
        self.reaction_partial_rc = dict(self.supply_partial_rc.items()+
                                        self.demand_partial_rc.items())
        
        self.supply_rc, self.demand_rc = self._plot_rc()         
        self.reaction_rc = dict(self.supply_rc.items() + 
                                self.demand_rc.items())
        
        self.supply_elas, self.demand_elas, self.mod_elas = self._plot_elas()
        self.reaction_elas = dict(self.supply_elas.items() +
                                  self.demand_elas.items() +
                                  self.mod_elas.items())
        
        self.supply_total, self.demand_total = self._plot_totals()
        
        
        fix_ss = getattr(self.parent.basemod,self.parent.fix+'_ss')    
        self.ss_line = self.ax.axvline(x=fix_ss, ls=':', color='0.5', lw=1)     
        self.ax.loglog()
        self.legend = self.ax.legend()
        self.title_label = 'Model: '+self.parent.parent._mod+' - Rate Characteristic'
        self.title = self.ax.set_title(self.title_label)
        self.ax.axis([self.parent.scan_min, self.parent.scan_max, self.parent.flux_min, self.parent.flux_max])
        self.ax.set_xlabel('$Fixed: ['+self.parent.fix+']$')
        self.ax.set_ylabel('$Flux$')
        
        self.legend_status = True
        self.title_status = True
        self._clear()
        self._make_species_dir()
        
    def _make_species_dir(self):
        """
        _make_species_dir()

        Creates a directory for the specific species used in the figure.

        Arguments:
        =========
        None
        """
        
       
        out_base_dir_status = os.path.exists(os.path.join(self.parent.parent._psc_out_dir, 
                                                          self.parent.fix))
        if not out_base_dir_status:
            os.mkdir(os.path.join(self.parent.parent._psc_out_dir, 
                                                          self.parent.fix))
        
        
    
    def _reactions(self):
        reactions = {}
        for r in self.parent.isSubstrateOf:
            reactions['J_' + r] = 'Demand Reaction'
        for r in self.parent.isProductOf:
            reactions['J_' + r] = 'Supply Reaction'
        for r in self.parent.isModifierOf:
            reactions['J_' + r] = 'Modified Reaction'
        return reactions
        
    
                    
       
    def _assign_hue(self):        
        allreactions = self.parent.isReagentOf + self.parent.isModifierOf
        h_num = 0
        while len(allreactions) > len(self.huelist):
                self.huelist.append(self.huelist[h_num])
                h_num = h_num+1
        huedict = {}
        for r_num,reaction in enumerate(allreactions):
            huedict['J_' + reaction] = self.huelist[r_num]    
        return huedict
    
    
    def _plot_totals(self):  
        
        supply_total = None
        demand_total = None      
            
        if len(self.parent.FixProductFor)>1:
            res_sup=numpy.zeros(self.parent.scan_points)
            for flux in range(len(self.parent.FixProductFor)):
                res_sup += self.parent.scandata[:,flux+1]
            supply_total = self.ax.plot(self.parent.scandata[:,0], 
                                        res_sup, '--', 
                                        color ='#0000C0',
                                        label = 'Total Supply Flux', 
                                        linewidth = 2)
            
            
        if len(self.parent.FixSubstrateFor)>1:
            res_dem=numpy.zeros(self.parent.scan_points)
            for flux in range(len(self.parent.FixSubstrateFor)):
                res_dem += self.parent.scandata[:,flux+len(self.parent.FixProductFor)+1]
            demand_total = self.ax.plot(self.parent.scandata[:,0], 
                                        res_dem, '--', 
                                        color = '#00c000', 
                                        label = 'Total Demand Flux', 
                                        linewidth=2)
        return supply_total, demand_total
        
        
    def _plot_flux(self):
        supply_flux = {}
        demand_flux = {}
        
        # supply plots
        for column, reaction in enumerate(self.parent.FixProductFor):
            colr = htor(self.huedict[reaction], 1.0 , 1.0)
            lbl = '$J_{'+reaction[2:]+'}$'          
            supply_flux[reaction] = self.ax.plot(self.parent.scandata[:,0], 
                                               self.parent.scandata[:,column+1],
                                               '-', 
                                               linewidth=2, 
                                               label = lbl, 
                                               color = colr)
            supply_flux[reaction][0]._permalabel = lbl
        #demand plots                                     
        for column, reaction in enumerate(self.parent.FixSubstrateFor):
            colr = htor(self.huedict[reaction], 1.0 , 1.0)     
            lbl = '$J_{'+reaction[2:]+'}$'       
            demand_flux[reaction] = self.ax.plot(self.parent.scandata[:,0],
                                               self.parent.scandata[:,column+len(self.parent.FixProductFor)+1],
                                               '-',
                                               linewidth=2, 
                                               label = lbl, 
                                               color = colr)
            demand_flux[reaction][0]._permalabel = lbl
            
        return supply_flux, demand_flux
    
    def _plot_elas(self):
        supply_elas = {}
        demand_elas = {}
        mod_elas = {}
        
        allreactions = self.parent.isReagentOf + self.parent.isModifierOf
        
        for step in allreactions:
            J_ss = getattr(self.parent.basemod,'J_'+step)
            fix_ss = getattr(self.parent.basemod,self.parent.fix+'_ss')
            ec_slope = self.parent.basemod.ec.get(step,self.parent.fix)
            ec_constant = J_ss/(fix_ss**ec_slope)
            range_min = fix_ss/self.parent.slope_range_factor
            range_max = fix_ss*self.parent.slope_range_factor
            stepsize = fix_ss
            fix_conc = numpy.arange(range_min, range_max, stepsize)
            ec_rate = ec_constant * fix_conc**(ec_slope)
            
            colr = htor(self.huedict['J_' + step], 0.5 , 1.0)
            if step in self.parent.isProductOf: the_dict = supply_elas
            elif step in self.parent.isSubstrateOf: the_dict = demand_elas
            elif step in self.parent.isModifierOf: the_dict = mod_elas
            
            lbl = '$\epsilon^{'+step+'}_{'+self.parent.fix+'}$'
            the_dict['J_' + step] = self.ax.plot(fix_conc, 
                                          ec_rate, 
                                          color = colr,
                                          label = lbl)
            the_dict['J_' + step][0]._permalabel = lbl
                                         
            
            
                                                
        return supply_elas, demand_elas, mod_elas
    
    def _plot_rc(self):
        supply_rc = {}
        demand_rc = {}    
    
        for step in self.parent.isReagentOf:
            J_ss = getattr(self.parent.basemod,'J_'+step)
            fix_ss = getattr(self.parent.basemod,self.parent.fix+'_ss')
            rc_slope = self.parent.mod.rc.get(step, self.parent.fix)
            rc_constant = J_ss/(fix_ss**rc_slope)
            range_min = fix_ss/self.parent.slope_range_factor
            range_max = fix_ss*self.parent.slope_range_factor
            stepsize = fix_ss
            fix_conc = numpy.arange(range_min, range_max, stepsize)
            rc_rate = rc_constant * fix_conc**(rc_slope)
            
            colr = htor(self.huedict['J_' + step], 1.0,0.6)
            
            if step in self.parent.isProductOf: the_dict = supply_rc
            elif step in self.parent.isSubstrateOf: the_dict = demand_rc 
            lbl = '$R^{J_{'+step+'}}_{'+self.parent.fix+'}$'      
            the_dict['J_' + step] = self.ax.plot(fix_conc,
                                                 rc_rate, 
                                                 '--',  
                                                 lw=2, 
                                                 color = colr, 
                                                 label = lbl)
            the_dict['J_' + step][0]._permalabel = lbl
                                                        
        return supply_rc, demand_rc
        
    def _plot_partial_rc(self):
        
        supply_partial_rc = {}
        demand_partial_rc = {}
        allreactions = self.parent.isReagentOf + self.parent.isModifierOf
        
        
        for reaction in self.parent.isReagentOf:
            J_ss = getattr(self.parent.basemod,'J_'+reaction)
            fix_ss = getattr(self.parent.basemod,self.parent.fix+'_ss')            
            step_dict = {}            
            for step in allreactions:
                prc_slope = self.parent.basemod.ec.get(step,self.parent.fix)*self.parent.mod.cc.get(reaction,step)
                prc_constant = J_ss/(fix_ss**prc_slope)
                range_min = fix_ss/self.parent.slope_range_factor
                range_max = fix_ss*self.parent.slope_range_factor
                stepsize = fix_ss
                fix_conc = numpy.arange(range_min, range_max, stepsize)
                prc_rate = prc_constant * fix_conc**(prc_slope)
                #if abs(prc_slope) > 0.01:    # only plot nonzero partial RCs                    
                colr = htor(self.huedict['J_'+step],0.5,1.0)
                lbl = '$^{'+step+'}R^{J_{'+reaction+'}}_{'+self.parent.fix+'}$'
                step_dict['J_'+step] = self.ax.plot(fix_conc,
                                                    prc_rate, 
                                                    color = colr,
                                                    lw=3, 
                                                    label = lbl)
                step_dict['J_'+step][0]._permalabel = lbl
                if abs(prc_slope) > 0.01: 
                    step_dict['J_'+step][0]._nonzero = True
                else:
                    step_dict['J_'+step][0]._nonzero = False
                if reaction in self.parent.isProductOf: the_dict = supply_partial_rc
                elif reaction in self.parent.isSubstrateOf: the_dict = demand_partial_rc
                the_dict['J_' + reaction] = step_dict
            
        return supply_partial_rc, demand_partial_rc
                
        
    def show(self):
        """
        Shows the plot and updates the legend and title. Calls the methods
        update_title and update_legend        
        """
        self.update_title()
        self.update_legend()
        self.figure.show()        
    
    def update_legend(self):
        """
        Updates the title using the value of legend_status (boolean) for
        visibility.
        
        This function is called automatically by save() and show().        
        """
        
        del(self.legend)
        self.legend = self.ax.legend()
        self.legend.set_visible(self.legend_status)
        
    def update_title(self):  
        """
        Updates the title using the value of title_label for the title label and
        title_status (boolean) for visibility.
        
        This function is called automatically by save() and show().        
        """
        
        
        del(self.title)
        self.title = self.ax.set_title(self.title_label)
        self.title.set_visible(self.title_status)
        
    def save(self,filename):
        """
        Saves the figure with the given file name (in the current directory when
        no location is specified)
        
        Arguments:
        ==========
        filename    -    The name and location of the file
        """
        self.update_title()
        self.update_legend()
        self.figure.savefig(filename)
        
    
    def _line_label_vis(self, line, visibility):
        if visibility is True: line._label = line._permalabel
        else: line._label = ''
        
    def set_visible(self, name, affzero = 0, **kwds):
        """
        This function sets the visibility of the lines associated with a certain
        reaction. Use the show() method to show the updated figure after this 
        method.
        
        Arguments:
        ==========
        name     -    The name of the reaction. This value is in the format
                      "J_reactionname", where reactionname is the name of the
                      reaction as it appears in the psc file.
        affzero  -    If true, partial response coefficient lines with zero
                      value slopes will also be affected (default = 0)
        
        Keywords:
        ==========
        Valid keywords are:
        p        -    partial response coefficient
        f        -    flux
        e        -    elasticity
        r        -    response coefficient
        
        For reactions where the fixed metabolite is only a modifier, the only
        valid keyword is "e". 
        
        Usage example:
        fig.set_visible('J_reaction1', l= True, r = False)
        
        This will set the flux line for "reaction1" visible while turning off the 
        response coefficient line. Elasticity and partial response coefficient 
        lines are left as they were.
        
        or
        
        fig.set_visible('J_reaction1', l= True, r = False, p = True, showzero = True)
        
        Same as above, but with partial response coefficients also visible, including
        those with slopes equal to zero
        
        
                    
        """        
        kwrs = {'e':self.reaction_elas,
                  'r':self.reaction_rc,
                  'f':self.reaction_flux}
        for key in kwrs.iterkeys():
            if kwds.has_key(key):
                line = kwrs[key][name][0]
                line.set_visible(kwds[key])
                self._line_label_vis(line, kwds[key])
        if kwds.has_key('p') and name in self.reaction_partial_rc.keys():
            for key in self.reaction_partial_rc[name].iterkeys():
                line = self.reaction_partial_rc[name][key][0]
                if affzero:                
                    line.set_visible(kwds['p'])
                    self._line_label_vis(line, kwds['p'])
                elif line._nonzero:
                    line.set_visible(kwds['p'])
                    self._line_label_vis(line, kwds['p'])
                
    def set_type_visible(self,line_set_name, visibility, affzero=0):
        """
        Sets the visibility of a set of lines. Use the show() method to show the
        updated figure after this method.
        
        Arguments:
        ==========
        line_set_name - The name of the set of lines to enable or disable
                        Valid values are:
                            supply_rc
                            demand_rc
                            supply_elas
                            demand_elas
                            mod_elas
                            supply_flux
                            demand_flux
                            supply_partial_rc
                            demand_partial_rc
        visibility    - True or False
        affzero       - Boolean (default = 0) if set to True, zero slope
                        partial response coefficients will also be 
                        affected
        """
        values = {'supply_rc': self.supply_rc,
                  'demand_rc': self.demand_rc,
                  'supply_elas': self.supply_elas,
                  'demand_elas': self.demand_elas,
                  'mod_elas': self.mod_elas,
                  'supply_flux': self.supply_flux,
                  'demand_flux': self.demand_flux,
                  'supply_partial_rc': self.supply_partial_rc,
                  'demand_partial_rc': self.demand_partial_rc
                  }
        if 'partial' in line_set_name:
            for dic in values[line_set_name].iterkeys():
                for key in values[line_set_name][dic].iterkeys():
                    line = values[line_set_name][dic][key][0]
                    if affzero:
                        line.set_visible(visibility)
                        self._line_label_vis(line,visibility)
                    elif line._nonzero:
                        line.set_visible(visibility)
                        self._line_label_vis(line,visibility)
                    
            
        else:
            for key in values[line_set_name].iterkeys():                
                line = values[line_set_name][key][0]                
                line.set_visible(visibility)
                self._line_label_vis(line,visibility)
                
    
    
    def plotRateChar(self,file = 0):
        """
        plotRateChar(file=0)

        Plot the data in the instantiated RateCharData class (fluxes vs.
        the concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """ 
        
        filename = os.path.join(self.parent.parent._psc_out_dir, 
                                self.parent.fix,
                                self.parent.modelfilename[:-4]+'_'+self.parent.fix+'_flux.png')             
        
        self.title_label = 'Model: '+self.parent.parent._mod+' - Rate Characteristic'
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        self.set_type_visible('supply_flux', True)
        self.set_type_visible('demand_flux', True)
        self.set_type_visible('supply_elas', False)
        self.set_type_visible('demand_elas', False)
        self.set_type_visible('mod_elas', False)
        self.set_type_visible('supply_rc', False)
        self.set_type_visible('demand_rc', False)
        self.set_type_visible('supply_partial_rc', False, affzero = True)
        self.set_type_visible('demand_partial_rc', False, affzero = True)
        
        if file:
            self.save(filename)
        else:
            self.show()
            
    def _clear(self):
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        
        self.set_type_visible('supply_flux', False)
        self.set_type_visible('demand_flux', False)
        self.set_type_visible('supply_elas', False)
        self.set_type_visible('demand_elas', False)
        self.set_type_visible('mod_elas', False)
        self.set_type_visible('supply_rc', False)
        self.set_type_visible('demand_rc', False)
        self.set_type_visible('supply_partial_rc', False, affzero = True)
        self.set_type_visible('demand_partial_rc', False, affzero = True)
        
        
    def plotElasRC(self,file = 0):
        """
        plotElasRC(file=0)

        Plot the data in the instantiated RateCharData class (rates, 
        elasticities and response coefficients vs. the concentration of the 
        fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        
        filename = os.path.join(self.parent.parent._psc_out_dir, 
                                self.parent.fix,
                                self.parent.modelfilename[:-4]+'_'+self.parent.fix+'_ElasRC.png')             
        
        self.title_label = 'Model: '+self.parent.parent._mod+' - Response vs. elasticity coefficients'
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        self.set_type_visible('supply_flux', True)
        self.set_type_visible('demand_flux', True)
        self.set_type_visible('supply_elas', True)
        self.set_type_visible('demand_elas', True)
        self.set_type_visible('mod_elas', True)
        self.set_type_visible('supply_rc', True)
        self.set_type_visible('demand_rc', True)
        self.set_type_visible('supply_partial_rc', False, affzero = True)
        self.set_type_visible('demand_partial_rc', False, affzero = True)
        
        if file:
            self.save(filename)
        else:
            self.show()
            
    def plotPartialRCSupply(self,file = 0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class for supply 
        reactions (fluxes and partial response coefficients vs. the 
        concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """  
        
        filename = os.path.join(self.parent.parent._psc_out_dir, 
                                self.parent.fix,
                                self.parent.modelfilename[:-4]+'_'+self.parent.fix+'_partialRCSupply.png')             
        
        self.title_label = 'Model: '+self.parent.parent._mod+' - Partial response coefficients for Supply'
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        self.set_type_visible('supply_flux', True)
        self.set_type_visible('demand_flux', False)
        self.set_type_visible('supply_elas', False)
        self.set_type_visible('demand_elas', False)
        self.set_type_visible('mod_elas', False)
        self.set_type_visible('supply_rc', True)
        self.set_type_visible('demand_rc', False)
        self.set_type_visible('supply_partial_rc', True)
        self.set_type_visible('demand_partial_rc', False, affzero = True)
        
        if file:
            self.save(filename)
        else:
            self.show()
            
    def plotPartialRCDemand(self,file = 0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class for demand 
        reactions (fluxes and partial response coefficients vs. the 
        concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """  
        
        filename = os.path.join(self.parent.parent._psc_out_dir, 
                                self.parent.fix,
                                self.parent.modelfilename[:-4]+'_'+self.parent.fix+'_partialRCDemand.png')             
        
        self.title_label = 'Model: '+self.parent.parent._mod+' - Partial response coefficients for Demand'
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        self.set_type_visible('supply_flux', False)
        self.set_type_visible('demand_flux', True)
        self.set_type_visible('supply_elas', False)
        self.set_type_visible('demand_elas', False)
        self.set_type_visible('mod_elas', False)
        self.set_type_visible('supply_rc', False)
        self.set_type_visible('demand_rc', True)
        self.set_type_visible('supply_partial_rc', False, affzero = True)
        self.set_type_visible('demand_partial_rc', True)
        
        if file:
            self.save(filename)
        else:
            self.show()
    
    def plotRateCharIndiv(self, file=0):
        """
        plotRateCharIndiv(file=0)        

        Plot the data in the instantiated RateCharData class (fluxes vs.
        the concentration of the fixed species for each supply and demand flux 
        in turn).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        self.set_type_visible('supply_flux', False)
        self.set_type_visible('demand_flux', False)
        self.set_type_visible('supply_elas', False)
        self.set_type_visible('demand_elas', False)
        self.set_type_visible('mod_elas', False)
        self.set_type_visible('supply_rc', False)
        self.set_type_visible('demand_rc', False)
        self.set_type_visible('supply_partial_rc', False, affzero = True)
        self.set_type_visible('demand_partial_rc', False, affzero = True)
        
        
        for line in self.huedict.iterkeys():
            if self.mod_elas.has_key(line): continue
            if line not in self.reaction_partial_rc.keys(): continue
            if len(self.supply_flux) == 1: self.set_visible(self.supply_flux.keys()[0],l=True)
            if len(self.demand_flux) == 1: self.set_visible(self.demand_flux.keys()[0],l=True)
        
            filename = os.path.join(self.parent.parent._psc_out_dir, 
                                    self.parent.fix,
                                    self.parent.modelfilename[:-4]+'_'+self.parent.fix+'_flux_'+ line +'_.png')             
            
            self.title_label = 'Model: '+self.parent.parent._mod+' - Rate Characteristic - '+ line
            self.set_visible(line,f=True)
            if file:
                self.save(filename)
            else:
                self.show()
                raw_input("Press Enter to continue...")
            self.set_visible(line,f=False)
            
            
    def plotElasRCIndiv(self, file=0):
        """
        plotElasIndivRC(file=0)

        Plot the data in the instantiated RateCharData class (rates, 
        elasticities [sans modifier elasticities] and response coefficients vs. 
        the concentration of the fixed species for each supply and demand 
        reaction in turn).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """
        
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        self.set_type_visible('supply_flux', False)
        self.set_type_visible('demand_flux', False)
        self.set_type_visible('supply_elas', False)
        self.set_type_visible('demand_elas', False)
        self.set_type_visible('mod_elas', False)
        self.set_type_visible('supply_rc', False)
        self.set_type_visible('demand_rc', False)
        self.set_type_visible('supply_partial_rc', False, affzero = True)
        self.set_type_visible('demand_partial_rc', False, affzero = True)
        
        
        for line in self.huedict.iterkeys():
            if self.mod_elas.has_key(line): continue
            if len(self.supply_flux) == 1: self.set_visible(self.supply_flux.keys()[0],l=True)
            if len(self.demand_flux) == 1: self.set_visible(self.demand_flux.keys()[0],l=True)
        
            filename = os.path.join(self.parent.parent._psc_out_dir, 
                                    self.parent.fix,
                                    self.parent.modelfilename[:-4]+'_'+self.parent.fix+'_ElasRC_'+ line +'_.png')             
            
            self.title_label = 'Model: '+self.parent.parent._mod+' -Response vs. elasticity coefficients - '+ line
            self.set_visible(line,f=True,e=True,r=True)
            if file:
                self.save(filename)
            else:
                self.show()
                raw_input("Press Enter to continue...")
            self.set_visible(line,f=False,e=False,r=False)
            
            
    def plotPartialRCIndiv(self, file=0):
        """
        plotPartialRC(file=0)

        Plot the data in the instantiated RateCharData class for each reaction
        in turn (fluxes and partial response coefficients vs. the 
        concentration of the fixed species).

        Arguments:
        ==========
        file (bool) - save plot as PNG file (default=0, plots to screen)
        """  
        
        if self.supply_total: self.supply_total[0].set_visible(True)
        if self.demand_total: self.demand_total[0].set_visible(True)
        self.set_type_visible('supply_flux', False)
        self.set_type_visible('demand_flux', False)
        self.set_type_visible('supply_elas', False)
        self.set_type_visible('demand_elas', False)
        self.set_type_visible('mod_elas', False)
        self.set_type_visible('supply_rc', False)
        self.set_type_visible('demand_rc', False)
        self.set_type_visible('supply_partial_rc', False, affzero = True)
        self.set_type_visible('demand_partial_rc', False, affzero = True)
        
        
        for line in self.huedict.iterkeys():
            if self.mod_elas.has_key(line): continue
            if line not in self.reaction_partial_rc.keys(): continue
            if len(self.supply_flux) == 1: self.set_visible(self.supply_flux.keys()[0],l=True)
            if len(self.demand_flux) == 1: self.set_visible(self.demand_flux.keys()[0],l=True)
            
        
            filename = os.path.join(self.parent.parent._psc_out_dir, 
                                    self.parent.fix,
                                    self.parent.modelfilename[:-4]+'_'+self.parent.fix+'_PartialRC_'+ line +'_.png')             
            
            self.title_label = 'Model: '+self.parent.parent._mod+' - Partial response coefficients - '+ line
            self.set_visible(line,f=True,p=True,r=True)
            if file:
                self.save(filename)
            else:
                self.show()
                raw_input("Press Enter to continue...")
            self.set_visible(line,f=False,p=False,r=False)
        
        
        
