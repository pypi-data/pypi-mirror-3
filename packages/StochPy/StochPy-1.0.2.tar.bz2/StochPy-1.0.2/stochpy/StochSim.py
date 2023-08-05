 #! /usr/bin/env python
"""
Stochastic Simulation Module
============================

The main module of StochPy

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: November 11, 2011
"""

def usage():  
  print """
Command line options:
--------------------
-h  Print this help message
-f  PySceS input file [default = filename.psc]
-s  Number of time steps [default = 1000 time steps]
-t  End time 
-v  Testsuite

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: November 11, 2011
"""

############################ IMPORTS ################################

from math import ceil
import sys,copy,time,os,getopt,cPickle,string

try: import numpy as np  
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without numpy"
    print "See http://numpy.scipy.org/ for more information about numpy"
    sys.exit()
 
try: import stochpy.modules.Analysis as Analysis			 # installed  
except:
    sys.path.append(os.getcwd()+'/modules/')
    import Analysis

try: from stochpy.PyscesMiniModel import InterpolatedDataObj # installed
except: from PyscesMiniModel import InterpolatedDataObj

############################ END IMPORTS ############################
  
class SSA():
  """
  Input options:
   - *Method* [default = 'Direct']
      Available methods: 'Direct', 'FirstReactionMethod','TauLeaping','Next Reaction Method'
   - *File*:   [default = ImmigrationDeath.psc]
   - *dir*:    [default = /home/user/stochpy/pscmodels/ImmigrationDeath.psc]
   - *Mode*:   [default = 'steps'] simulation for a total number of 'steps' or until a certain end 'time' (string)
   - *End*:    [default = 1000] end of the simulation (number of steps or end time)   (float)   
   - *Trajectories*L [default = 1] (integer)
   - *TrackPropensities*: [default = False] (Boolean)

   Usage (with High-level functions):
   >>> mod = stochpy.SSA()
   >>> help(mod)
   >>> mod.Model(File = 'filename.psc', dir = '/.../')
   >>> mod.Method('Direct')
   >>> mod.Reload()
   >>> mod.Trajectories(5)
   >>> mod.Timesteps(10000)
   >>> mod.TrackPropensities()
   >>> mod.DoStochSim()
   >>> mod.DoStochSim(end=1000,mode='steps',trajectories=5,method='Direct')
   >>> mod.PlotTimeSim()
   >>> mod.PlotPropensities()
   >>> mod.PlotInterpolatedData()
   >>> mod.PlotWaitingtimes()
   >>> mod.PlotDistributions(bin_size = 3)
   >>> mod.ShowMeans()
   >>> mod.ShowStandardDeviations()
   >>> mod.ShowOverview()
   >>> mod.ShowSpecies()
   >>> mod.DoTestsuite()
  """
  def __init__(self,Method='Direct',File=None,dir=None,Mode='steps',End=1000,Trajectories=1,IsTestsuite=False,IsInteractive=True,IsTrackPropensities=False,IsRun=False):
    if os.sys.platform != 'win32':
        output_dir = os.path.join(os.path.expanduser('~'),'Stochpy',)
        temp_dir = os.path.join(os.path.expanduser('~'),'Stochpy','temp',)
        if File == dir == None:
            dir = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
            File = 'ImmigrationDeath.psc'
    else:
        output_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy',)
        temp_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp',)
        if File == dir == None:
            dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
            File = 'ImmigrationDeath.psc'

    self.IsInteractive = IsInteractive
    self.model_file = File
    self.model_dir = dir
    self.output_dir = output_dir
    self.temp_dir = temp_dir
    self.Method(Method)
    self.sim_end = End
    self.sim_mode = Mode
    self.sim_trajectories = Trajectories
    self.IsTrackPropensities = IsTrackPropensities
    self.IsSimulationDone = False
    if self.IsInteractive:
        try: Analysis.plt.ion()      		        # Set on interactive pylab environment
        except: pass 					# Error message is already shown
        
    if IsTestsuite: self.DoTestsuite()
    if IsRun: self.DoStochSim()				# Initial run

  def Method(self,method):
    """
    Input:
     - *method*

    Select one of the following four methods:    
     - *Direct*
     - *FirstReactionMethod*
     - *NextReactionMethod*
     - *TauLeaping*
    Note: input must be a string --> 'Direct'
    """
    self.IsTauLeaping = False
    IsNRM = False
    if method == 'Direct':
        import DirectMethod
        self.sim_method = DirectMethod.DirectMethod
        print "Info: The Direct method is selected to perform the simulations"
        self.sim_method_name = "Direct"
    elif method == 'FirstReactionMethod':
        import FirstReactionMethod as FRM
        self.sim_method = FRM.FirstReactionMethod
        self.sim_method_name = "FirstReactionMethod"
        print "Info: The First Reaction method is selected to perform the simulations"
    elif method == 'TauLeaping':
        import TauLeaping
        self.sim_method = TauLeaping.OTL
        self.sim_method_name = "TauLeaping"
        print "Info: The Optimized Tau-Leaping method is selected to perform the simulations"
        print "Info: the user can change the 'epsilon' parameter with DoStochSim(epsilon = 0.01)"
        self.IsTauLeaping = True
    elif method == 'NextReactionMethod':
        import NextReactionMethod as NRM
        self.sim_method = NRM.NextReactionMethod
        print "Info: The Next Reaction method is selected to perform the simulations"
        IsNRM = True
        self.sim_method_name = "NextReactionMethod"
    else:
        print "Error: The only valid options are: 'Direct', 'FirstReactionMethod', 'TauLeaping'."
        print "Info: By default, the Direct method is executed"
        import DirectMethod
        self.sim_method = DirectMethod.DirectMethod
        self.sim_method_name = "Direct"

    self.SSA = self.sim_method(self.model_file,self.model_dir,self.output_dir,self.temp_dir)
    self.IsSimulationDone = False

  def Timesteps(self,s):
      """
      Set the number of time steps to be generated for each trajectory
      
      Input:
       - *s*: number of time steps (integer)
      """
      try:
          self.sim_end  = int(s)
          self.sim_mode = 'steps'
          print "Info: The number of time steps is:\t",self.sim_end
      except:
          print "Error: The number of time steps must be an integer"

  def Endtime(self,t):
      """
      Set the end time of the exact realization of the Markov jump process
      
      Input:
       - *t*: end time  (float)
      """    
      try:
          self.sim_end  = float(t)
          self.sim_mode = 'time'
          print "Info: the simulation end time is:\t",self.sim_end
      except: print "Error: The end time must be an integer/float"

  def Trajectories(self,traj):
      """
      Set the number of trajectories to be generated
      
      Input:
       - *traj*: number of trajectories (integer)
      """
      try: self.sim_trajectories = int(traj)
      except: print "Error: The number of trajectories must be a integer"

  def Reload(self):
      """ Reload the entire model again. Useful if the model file has changed"""
      self.SSA.Parse(self.model_file,self.model_dir)		# Build model
      self.model_file = self.SSA.ModelFile 
      self.model_dir = self.SSA.ModelDir
      self.IsSimulationDone = False	                        # 15/01/11

  def Model(self,File,dir=None):
      """
      High-level function to determine the model which can be used for stochastic simulations
      
      Input:
       - *File*:'filename.psc' (string)
       - *dir*: [default = None] the directory where File is located (string)
      """    
      if self.IsSimulationDone:
        try: 
            del self.data_stochsim                          # remove old model data
            del self.data_stochsim_interpolated
        except: pass
      self.model_file = File
      if dir != None: 
          self.model_dir = dir
      self.Reload()

  def Mode(self,sim_mode='steps'):
      """
      Run a stochastic simulation for until `end` is reached. This can be either time steps or end time (which could be a *HUGE* number of steps).

      Input:
       - *sim_mode*: [default = 'steps'] 'time' or 'steps'
       - *end*: [default = 1000]   
      """
      self.sim_mode = sim_mode 
      if self.sim_mode not in ['steps','time']:
          print "Mode '%s' not recognised using: 'steps'" % mode
          self.sim_mode = 'steps'

  def GetTrajectoryData(self,n=1):
      """ 
      Switch to another trajectory, by default, the last trajectory is accesible      
      
      Input:
       - *n*: [default = 1] get data from a certain trajectory 
      """
      try: 
          File = open(self.temp_dir+'/'+self.model_file+str(n)+'.dat','r')	# Open dumped output
          self.data_stochsim = cPickle.load(File)
      except:
          print "Error: trajectory",n, "does not exist" 

  def TrackPropensities(self,boolean=True):
      """ 
      Track the propensities through time

      Input:
       - *boolean*: [default = True]
      """   
      try: self.IsTrackPropensities = int(boolean)
      except: print "input must be a boolean: True or False"
  
  def Run(self,end=False,mode=False,method=False,trajectories=False):
      """ Old version """
      self.DoStochSim(end,mode,method,trajectories)

  def DoStochSim(self,end=False,mode=False,method=False,trajectories=False,epsilon = 0.03):
    """
      doStochSim(end=10, mode='steps', method='Direct',trajectories = 1,epsilon = 0.03)

      Run a stochastic simulation for until `end` is reached. This can be either time steps or end time (which could be a *HUGE* number of steps).

      Input:
       - *end* [default=1000] simulation end (steps or time)
       - *mode* [default='steps'] simulation mode, can be one of:
         - *steps* total number of steps to simulate
         - *time* simulate until time is reached
       - *method* [default='Direct'] stochastic algorithm, can be one of:
         - Direct
         - FirstReactionMethod
         - NextReactionMethod
         - TauLeaping
       - *trajectories* [default = 1] number of trajectories
       - *epsilon* [default = 0.03] parameter for Tau-Leaping
    """
    if mode != False:         
        self.Mode(sim_mode = mode)         
    if end != False:    
        if type(end) == int or type(end) == float: self.sim_end = end      
        else:
            print "Error: end should be an integer or float\n 1000 is used by default"
            self.sim_end = 1000   
    try: 
        del self.data_stochsim                          # remove old model data
        del self.data_stochsim_interpolated
    except: pass

    if method != False: self.Method(method)
    if trajectories != False: self.Trajectories(trajectories)

    self.HasWaitingtimes = False
    self.HasMeanWaitingtimes = False
    self.HasDistributions = False
    self.HasInterpol = False
    try: self.DeleteTempfiles()						# Delete '.dat' files
    except: pass
    t1 = time.time()

    if self.sim_method_name == "TauLeaping":
      if self.sim_mode == 'time':
          self.SSA.Execute(self.sim_trajectories,self.sim_end,10**10,self.IsTrackPropensities,epsilon)
      elif self.sim_mode == 'steps':
          self.SSA.Execute(self.sim_trajectories,10**10,self.sim_end,self.IsTrackPropensities,epsilon)
      else:
          print "Error: Simulation mode should be 'time' or 'steps'. Steps is done by default"
          self.SSA.Execute(self.sim_trajectories,10**10,self.sim_end,self.IsTrackPropensities)
    else:
      if self.sim_mode == 'time':
          self.SSA.Execute(self.sim_trajectories,self.sim_end,10**10,self.IsTrackPropensities)
      elif self.sim_mode == 'steps':
          self.SSA.Execute(self.sim_trajectories,10**10,self.sim_end,self.IsTrackPropensities)
      else:
          print "Error: Simulation mode should be 'time' or 'steps'. Steps is done by default"
          self.SSA.Execute(self.sim_trajectories,10**10,self.sim_end,self.IsTrackPropensities)

    t2 = time.time()  
    self.IsSimulationDone = True
    self.HasDistributions = True
    self.data_stochsim = copy.deepcopy(self.SSA.data_stochsim)
    try: self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
    except: self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)
  
  def PlotTimeSim(self,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Time Simulation Plot'):
    """
    Plot time simulation output for each generated trajectory
    Default: PlotTimeSim() plots time simulation for each species

    Input:
     - *species2plot*: [default = True] as a list ['S1','S2'] 
     - *linestyle*: [default = 'None'] dashed, solid, and dash_dot (string)
     - *marker* [default = 'o'] ('v','o','*',',')
     - *title*: [default = '']  (string)
    """
    if not self.IsSimulationDone: self.DoStochSim()
    if species2plot == True: species2plot = self.data_stochsim.species_labels
    if type(species2plot) == str: species2plot = [species2plot]

    IsPlot = True
    for species in species2plot:
        if species not in self.data_stochsim.species_labels:
            print "Error: species",species,"is not in the model"
            IsPlot = False
    if IsPlot:
          try:
              traj = 1
              while traj <= self.SSA.Trajectories:
                  if self.SSA.Trajectories > 1:     
                      File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
                      self.data_stochsim = cPickle.load(File)
                  self.plot.TimeSimulation(self.data_stochsim.getSpecies(),species2plot,traj-1,linestyle,marker,colors,title) # Plot time sim
                  if self.SSA.Trajectories > 1: self.plot.plotnum-=1
                  traj+=1
              if traj > 1: self.plot.plotnum+=1
          except: print "Error: MatPlotlib is not available"
 
  def PrintTimeSim(self):
    """ Print time simulation output for each generated trajectory"""
    if not self.IsSimulationDone: self.DoStochSim()
    traj = 1
    while traj <= self.SSA.Trajectories:
        if self.SSA.Trajectories > 1:
            File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
            self.data_stochsim = cPickle.load(File)

        print 'Time','\t'
        for species in self.data_stochsim.species_labels:
            print species,'\t',
        print ''
        for timepoint in self.data_stochsim.getSpecies():
            for value in timepoint:
                print value,'\t',                                               # Print time sim
            print ''
        traj+=1

  def PlotDistributions(self,species2plot = True, linestyle = 'dotted',colors=None,title = 'StochPy Probability Density Function',bin_size=1):
    """
    Plots the PDF for each generated trajectory
    Default: PlotDistributions() plots PDF for each species

    Input:
     - *species2plot* [default = True] as a list ['S1','S2']
     - *linestyle* [default = 'dotted'] (string)
     - *colors* (list)
     - *title* [default = 'StochPy Probability Density Function'] (string)     
     - *bin_size* [default=1] (integer)
    """
    if not self.IsSimulationDone: self.DoStochSim()
    if species2plot == True: species2plot = self.data_stochsim.species_labels
    if type(species2plot) == str: species2plot = [species2plot]
    IsPlot = True
    for species in species2plot:
        if species not in self.data_stochsim.species_labels:
            print "Error: species",species,"is not in the model"
            IsPlot = False

    if IsPlot:
        try:
            traj = 1
            while traj <= self.SSA.Trajectories:    
                if self.SSA.Trajectories > 1:
                    File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
                    self.data_stochsim = cPickle.load(File)
                self.plot.Distributions(self.data_stochsim.distributions,species2plot,traj-1,linestyle,colors,title,bin_size)	# Plot dist
                if self.SSA.Trajectories > 1: self.plot.plotnum -= 1
                traj+=1      
            if traj > 1: self.plot.plotnum += 1
        except:
            print "Error: The Matplotlib module is not available, so it is impossible to create plots"
            print "Info: See http://matplotlib.sourceforge.net/"

  def PrintDistributions(self):
    """ Print obtained distributions for each generated trajectory """
    if not self.IsSimulationDone: self.DoStochSim()
    traj = 1
    while traj <= self.SSA.Trajectories:    
        if self.SSA.Trajectories > 1:
            File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
            self.data_stochsim = cPickle.load(File)
      
        for species in self.data_stochsim.distributions:
            print "Position\tProbability"            
            for i in range(len(species[0])):
                print species[0][i],"\t",species[1][i]
        traj+=1

  def PlotPropensities(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Plot'):
    """ 
    Plot time simulation output for each generated trajectory

    Default: PlotPropensities() plots propensities for each species

    Input:
     - *rates2plot* [default = True]: species as a list ['S1','S2']
     - *marker* [default = 'o'] ('v','o','*',',')
     - *linestyle* [default = 'None']: dashed, dotted, and solid (string)
     - *colors* [default = None] (list)
     - *title* [default = 'StochPy Propensities Plot'] (string)
    """
    if not self.IsTrackPropensities:
        self.IsTrackPropensities = True
        self.DoStochSim()
    if not self.IsSimulationDone: self.DoStochSim()
    if rates2plot  == True: rates2plot = self.SSA.rate_names
    if type(rates2plot) == str: rates2plot = [rates2plot]

    IsPlot = True
    for r in rates2plot:
        if r not in self.SSA.rate_names:
            print "Error: species",r,"is not in the model"
            IsPlot = False

    if IsPlot:
         try:
            traj = 1
            while traj <= self.SSA.Trajectories:	
                if self.SSA.Trajectories > 1:        
                    File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
                    self.data_stochsim = cPickle.load(File)

                self.plot.Propensities(self.data_stochsim,rates2plot,traj-1,linestyle,marker,colors,title) # Plot props time sim 
                if self.SSA.Trajectories > 1: self.plot.plotnum-=1
                traj+=1
            if traj > 1: self.plot.plotnum+=1
         except:
            print "Error: The Matplotlib module is not available, so it is impossible to create plots"
            print "Info: See http://matplotlib.sourceforge.net/"
            print "Info: Use the print function: PrintPropensities()"

  def PrintPropensities(self):
    """ Print time simulation output for each generated trajectory"""
    if not self.IsTrackPropensities:
        self.IsTrackPropensities = True
        self.DoStochSim()
    if not self.IsSimulationDone: self.DoStochSim()
    traj = 1

    while traj <= self.SSA.Trajectories:	
        if self.SSA.Trajectories > 1:        
            File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
            self.data_stochsim = cPickle.load(File)
        print 'Time\t',
        #for rate in self.data_stochsim.propensities_labels:
        for rate in self.SSA.rate_names: print rate,'\t',
        print ''
        for timepoint in self.data_stochsim.getPropensities():    
            for value in timepoint:
                print value,"\t",    					        # Print time sim
            print ''
        traj+=1

  def GetWaitingtimes(self):
    """ Get for each reaction the waiting times """ 
    if not self.IsSimulationDone: self.DoStochSim()
    if  self.IsTauLeaping:
        print "Error: It is impossible to get information about waiting times if you do simulations with the Tau-Leaping method"
    else:
        traj = 1
        waitingtimes = []
        while traj <= self.SSA.Trajectories:
            if self.SSA.Trajectories > 1:
                File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
                self.data_stochsim = cPickle.load(File)   
            waitingtimes = Analysis.ObtainWaitingtimes(self.data_stochsim,self.SSA.number_of_reactions)
            self.data_stochsim.setWaitingtimes(waitingtimes)
            if self.SSA.Trajectories > 1:
                name = self.SSA.TempDir+'/'+self.SSA.ModelFile+str(traj)+'.dat'
                cPickle.dump(self.data_stochsim,file = open(name,'w'))         # Dump trajectory output            
            traj+=1
        self.HasWaitingtimes = True      
    
  def PlotWaitingtimes(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Waitingtimes Plot'):
    """
    Plot obtained waiting times 
    default: PlotWaitingtimes() plots waiting times for all rates
    
    Input:
     - *rates2plot*: [default = True]  as a list of strings ["R1","R2"]
     - *linestyle*: [default = 'None'] dashed, dotted, dash_dot, and solid (string)
     - *marker* [default = 'o'] ('v','o','*',',')
     - *colors*: [default =  None] (list)
     - *title* [default = 'StochPy Waitingtimes Plot'] (string)
    """    
    IsPlot = True
    if self.IsTauLeaping:
        print "Error: It is impossible to get information about waiting times if you do simulations with the Tau-Leapingmethod"
        IsPlot = False

    if rates2plot  == True: rates2plot = self.SSA.rate_names
    if type(rates2plot) == str: rates2plot = [rates2plot]
    for r in rates2plot:
        if r not in self.SSA.rate_names:
            print "Error: reaction",r,"is not in the model"
            IsPlot = False

    if IsPlot:
       if not self.IsSimulationDone: self.DoStochSim()
       if not self.HasWaitingtimes and not self.IsTauLeaping: self.GetWaitingtimes()	# If not calculated 
       try:
          traj = 1
          while traj <= self.SSA.Trajectories:
              self.plot.Waitingtimes(self.data_stochsim.waiting_times,rates2plot,traj-1,linestyle,marker,colors,title)
              if self.SSA.Trajectories > 1:
                  self.plot.plotnum-=1
              traj+=1
          self.plot.plotnum+=1
       except:
          print "Error: The Matplotlib module is not available, so it is impossible to create plots"
          print "Info: See http://matplotlib.sourceforge.net/"

  def PrintWaitingtimes(self):
      """ Print obtained waiting times """
      IsPlot = True
      if self.IsTauLeaping:
          print "It is impossible to get information about waiting times if you do simulations with the Tau-Leapingmethod"
          IsPlot = False

      if IsPlot:
          if not self.IsSimulationDone: self.DoStochSim()
          if not self.HasWaitingtimes and not self.IsTauLeaping: self.GetWaitingtimes()	# If not calculated
          traj = 1
          while traj <= self.SSA.Trajectories:
              waiting_times = self.data_stochsim.waiting_times
              for r in waiting_times:
                  print "Waiting times\t",self.SSA.rate_names[int(r)-1]
                  waiting_times_r = waiting_times[r]
                  for time in waiting_times_r: print time
              traj+=1

  def GetMeanWaitingtimes(self):
      """ Get the mean waiting times for the selected trajectory """
      if not self.IsSimulationDone: self.DoStochSim()
      IsPlot = True
      if self.IsTauLeaping:
          print "It is impossible to get information about waiting times if you do simulations with the Tau-Leapingmethod"
          IsPlot = False

      if not self.HasWaitingtimes and not self.IsTauLeaping: self.GetWaitingtimes()	# If not calculated      
      
      if IsPlot:
          traj = 1
          while traj <= self.SSA.Trajectories:
              self.data_stochsim.setMeanWaitingtimes(self.data_stochsim.waiting_times)
              traj+=1    
          self.HasMeanWaitingtimes = True						# Calculated

  def PrintMeanWaitingtimes(self):
      """ Print the mean waiting times for the selected trajectory """
      if not self.HasMeanWaitingtimes: self.GetMeanWaitingtimes()
      print "Reaction\tMean Waiting times"    
      i=0
      for rate in self.SSA.rate_names: 
          print rate,"\t",self.data_stochsim.mean_waitingtimes[i]          
          i+=1

  def MeanWaitingtimes(self):
      """ old version (StochPy 0.9) """
      self.GetMeanWaitingtimes()

  def GetInterpolatedData(self):
    """ Perform linear interpolation for each generated trajectory. Linear interpolation is done for all integer time points, between the start time (0) end the endtime. """
    if not self.IsSimulationDone: self.DoStochSim()
    self.data_stochsim_interpolated = InterpolatedDataObj()

    for species in self.data_stochsim.species_labels: self.data_stochsim_interpolated.species.append([])
    if self.sim_mode == 'time': self.data_stochsim_interpolated.points = range(int(self.sim_end)+1) # Points for interpolation    
    traj = 1
    while traj <= self.SSA.Trajectories:
      if self.SSA.Trajectories > 1:
          File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')
          self.data_stochsim = cPickle.load(File)      

      if not self.sim_mode == 'time':                
          endtime = int(ceil(self.data_stochsim.time[-1][0]))
          if traj == 1: self.data_stochsim_interpolated.points = range(endtime+1)
          if endtime < self.data_stochsim_interpolated.points[-1]: self.data_stochsim_interpolated.points = range(endtime+1) 	 # Points for interpolation
         
      i=0
      for species in self.data_stochsim.species_labels:
          xp = self.data_stochsim.time.flatten()
          fp = self.data_stochsim.species[:,i]       
          temp_interpolated_output = []
          n=0
          for value in self.data_stochsim_interpolated.points:
              while n<len(xp):
                if value > xp[n]: n+=1              
                else:
                    if value: temp_interpolated_output.append(fp[n-1])
                    else: temp_interpolated_output.append(fp[0])
                    break

          self.data_stochsim_interpolated.species[i].append(temp_interpolated_output)  
          i+=1    
      traj+=1
    self.data_stochsim_interpolated.means,self.data_stochsim_interpolated.standard_deviations,self.data_stochsim_interpolated.time = Analysis.ObtainInterpolationResults(self.data_stochsim_interpolated.species,self.data_stochsim_interpolated.points)   
    self.HasInterpol = True

  def PrintInterpolatedData(self):    
      """ Analyse the interpolated output for each generated trajectory """
      if not self.IsSimulationDone: self.DoStochSim()
      if not self.HasInterpol: self.GetInterpolatedData()

      print "t",
      for species in self.data_stochsim.species_labels:
          print "\t","Mean "+species[4:], "\t","SD "+species[4:],
      print
      means = np.transpose(self.data_stochsim_interpolated.means)
      sds = np.transpose(self.data_stochsim_interpolated.standard_deviations)
      for t in range(self.data_stochsim_interpolated.time[-1]+1): 
          print t,"\t",
          for i in range(len(self.data_stochsim_interpolated.means)): 
              print means[t][i],"\t",sds[t][i],"\t",
          print

  def PlotInterpolatedData(self,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Interpolated Time Plot (# of trajectories = )'): 
      """
      Plot the averaged interpolation result. For each time point, the mean and standard deviation are plotted 
      Input:
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = ','] ('v','o','*')
       - *colors*: [default =  None] (list)
       - *title* [default = StochPy Interpolated Time (# of trajectories = ... ) ] (string)
      """
      if species2plot == True: species2plot = self.data_stochsim.species_labels
      if type(species2plot) == str: species2plot = [species2plot]

      IsPlot = True
      for species in species2plot:
          if species not in self.data_stochsim.species_labels:
              print "Error: species",species,"is not in the model"
              IsPlot = False      
      if title == 'StochPy Interpolated Time Plot (# of trajectories = )':
          title = title.replace('= ','= '+str(self.SSA.Trajectories)) 
      if not self.IsSimulationDone: self.DoStochSim()
      if not self.HasInterpol: self.GetInterpolatedData()     
      try:
          self.plot.AverageTimeSimulation(self.data_stochsim_interpolated.means,self.data_stochsim_interpolated.standard_deviations,self.data_stochsim_interpolated.time,species2plot,linestyle,marker,colors,title)
      except:
          print "Error: The Matplotlib module is not available, so it is impossible to create plots"
          print "Info: See http://matplotlib.sourceforge.net/"
      self.plot.plotnum+=1

  def GetMeans(self):
      """ Get the means of each species for the selected trajectory """
      if not self.IsSimulationDone: self.DoStochSim()

  def ShowMeans(self):
      """ Print the means of each species for the selected trajectory"""
      self.GetMeans()    
      print "Species\t","Mean"   
      for species in self.data_stochsim.species_labels:         
          print species,"\t",self.data_stochsim.means[species]

  def GetStandardDeviations(self):
      """ Get the standard deviations of each species for the selected trajectory """
      if not self.IsSimulationDone: self.DoStochSim()

  def ShowStandardDeviations(self):
      """ Print the standard deviations of each species for the selected trajectory"""      
      print "Species\t","Standard Deviation"
      for species in self.data_stochsim.species_labels:          
          print species,"\t",self.data_stochsim.standard_deviations[species]

  def Write2File(self,what='TimeSim', directory=None):
    """
    Write output to a file

    Input:
     - *what*: [default = TimeSim] TimeSim, Propensities, Distributions, Waitingtimes, and Interpol (string)
     - *directory*: [default = None] (string)
    """
    if directory == None: directory = self.output_dir + '/' + self.model_file+'_' + what
    if what == 'TimeSim':
        if not self.IsSimulationDone: self.DoStochSim()
        traj = 1
        while traj <= self.SSA.Trajectories:
            if self.SSA.Trajectories > 1:
                File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')
                self.data_stochsim = cPickle.load(File)

            Dir = directory+str(traj)+'.txt'			# Dir/Filename
            f = open(Dir,'w')
            for timepoint in self.data_stochsim.getSpecies():
                line = ''
                for value in timepoint:
                    line += str(value)
                    line += '\t'
                line += '\n'
                f.write(line)
            traj+=1
            f.close()
            print "TimeSim output is successfully saved at:\t",Dir
    elif what == 'Propensities':
        if self.IsTrackPropensities == 0:
            self.IsTrackPropensities = 1
            self.DoStochSim()
        elif not self.IsSimulationDone: self.DoStochSim()
        traj = 1
        while traj <= self.SSA.Trajectories:
            if self.SSA.Trajectories > 1:
                File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')
                self.data_stochsim = cPickle.load(File)

            Dir = directory+str(traj)+'.txt'
            f = open(Dir,'w')        
            for timepoint in self.data_stochsim.getPropensities():
                line = ''
                for value in timepoint:
                    line += str(value)
                    line += '\t'
                line += '\n'
                f.write(line)
            traj+=1
            f.close()
            print "Propensities output is succesfully saved at:\t",Dir
    elif what == 'Distributions':
        if not self.IsSimulationDone: self.DoStochSim()
        traj = 1
        while traj <= self.SSA.Trajectories:    
            if self.SSA.Trajectories > 1:
                File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
                self.data_stochsim = cPickle.load(File)

            Dir = directory+str(traj)+'.txt'
            f = open(Dir,'w')  
            for species in self.data_stochsim.distributions:
                f.write("Position\tProbability\n")
                for i in range(len(species[0])):  
                    line = str(species[0][i])+"\t"+str(species[1][i])+"\n"
                    f.write(line)               
            traj+=1 
            f.close()
            print "Distributions output is successfully saved at:\t",Dir
    elif what == 'Waitingtimes':
        if not self.HasWaitingtimes: self.GetWaitingtimes() # If not calculated
        traj = 1
        while traj <= self.SSA.Trajectories:
            if self.SSA.Trajectories > 1:
                File = open(self.temp_dir+'/'+self.model_file+str(traj)+'.dat','r')	# Open dumped output
                self.data_stochsim = cPickle.load(File)

            Dir = directory+str(traj)+'.txt'
            f = open(Dir,'w')
  
            for r in self.data_stochsim.waiting_times:
                f.write("Waitingtimes\t"+str(self.SSA.rate_names[int(r)-1])+"\n")
                waiting_times_r = self.data_stochsim.waiting_times[r]
                for time in waiting_times_r: f.write(str(time)+"\n")
            traj+=1
            f.close()
            print "Waiting times output is successfully saved at:\t",Dir
    elif what == 'Interpol':
        if not self.IsSimulationDone: self.DoStochSim()
        if not self.HasInterpol: self.GetInterpolatedData()
        self.data_stochsim_interpolated.means,self.data_stochsim_interpolated.standard_deviations,self.data_stochsim_interpolated.time =  Analysis.ObtainInterpolationResults(self.data_stochsim_interpolated.species,self.data_stochsim_interpolated.points)

        Dir = directory + '.txt'
        f = open(Dir,'w')
        f.write("t")
        for species in self.data_stochsim.species_labels: f.write("\tMean "+str(species[4:])+"\tSD "+str(species[4:]))
        f.write("\n")

        means = np.transpose(self.data_stochsim_interpolated.means)
        sds = np.transpose(self.data_stochsim_interpolated.standard_deviations)
        for t in range(self.data_stochsim_interpolated.time[-1]+1):
            f.write(str(t)+"\t")
            for i in range(len(self.data_stochsim_interpolated.means)): f.write(str(means[t][i])+"\t"+str(sds[t][i])+"\t")
            f.write("\n")
        print "Interpolation output is successfully saved at:\t",Dir
    else:
        print "Error: The only valid options are: 'TimeSim', 'Propensities', 'Distributions', 'Waitingtimes', and 'Interpol'"
        print "Info: mod = stochpy.SSA()"
        print "Info: mod.Write2File('Distributions')"

  def ShowSpecies(self):
      """ Print the species of the model """
      print self.data_stochsim.species_labels

  def ShowOverview(self):
      """ Print an overview of the current settings """
      print "Current Model:\t", self.model_file
      if self.sim_mode == "steps": print "Number of time steps:\t\t", self.sim_end
      elif self.sim_mode == "time":print "Simulation end time:\t", self.sim_end
      print "Current Algorithm:\t",self.sim_method
      print "Number of trajectories:\t",self.sim_trajectories
      if self.IsTrackPropensities: print "Propensities are tracked"
      else:print "Propensities are not tracked"

  def DeleteTempfiles(self):
      """ Deletes all .dat files """
      for line in self.SSA.Dump: os.remove(line)

  def DoTestsuite(self,epsilon_ = 0.01):
      """
      Do 10000 simulations until t=50 and print the interpolated result for t = 0,1,2,...,50
      
      Input:
       - *epsilon_* [default = 0.01]: useful for Tau-Leaping simulations (float)
      """
      self.sim_end = 50
      self.sim_mode = "time"
      self.sim_trajectories = 10000
      self.DoStochSim(epsilon = epsilon_ )    
      self.PrintInterpolatedData()    
      self.sim_end = 1000                           # Reset settings to default values
      self.sim_mode = "steps"
      self.sim_trajectories = 1
 
if __name__ == "__main__": 
  modelfile = "ImmigrationDeath.psc" 				# Default model
  try: Dir = '/home/timo/Stochpy/pscmodels/'  
  except: print " Error: make sure that the directory:", Dir, "exists"

  ####################### Command line options ###########################
  try: options,remainder = getopt.getopt(sys.argv[1:],'hf:m:n:s:t:v',  ['filename=','method=','number=','timesteps=','endtime=','interpolate'])
  except:
      print "Error: This is no valid option.\nPlease use the commenad python filename.py -h"
      sys.exit()

  method = 'Direct'
  end = 1000
  mode = 'steps'
  trajectories = 1
  is_run = True
  is_testsuite = False
  for opt,arg in options:
    if opt in ('-h'):
        usage()
        sys.exit()
    elif opt in ('-f','--filename'):
        modelfile = str(arg)
    if opt in ('-m','--method'):
        method = arg  
    elif opt in ('-n','--trajectories'):
        try: trajectories = int(arg)
        except: 
            print "Make sure that the number of trajectories is a integer"
            sys.exit()
    elif opt in ('-s','--timesteps'):
        try: end = int(arg)    
        except:
            print "The number of time steps for the simulation must be a integer" 
            sys.exit()
    elif opt in ('-t','--endtime'):
        try:
            end = float(arg)        
            mode = 'time'
        except:
            print "The endtime must be a integer or float"
            sys.exit()
    elif opt in ('-v'):
        is_testsuite = True
        is_run = False
  
  sim = SSA( Method=method,IsRun=is_run,File=modelfile,dir=Dir,Mode = mode,End=end,Trajectories=trajectories,IsTestsuite = is_testsuite,IsInteractive = 0)
    
  """import cProfile  
  cProfile.run('sim = SSA( Method=method,IsRun=is_run,File=modelfile,dir=Dir,Mode = mode,End=ends,Trajectories=trajectories,IsTestsuite = is_testsuite,IsInteractive = 0)','fooprof')
  import pstats
  p = pstats.Stats('fooprof')
  p.strip_dirs().sort_stats("time").print_stats() """ 
  
  traj = 1
  while traj <= sim.SSA.Trajectories:
      if sim.SSA.Trajectories > 1:
          File = sim.temp_dir+'/'+sim.model_file+str(traj)+'.dat'
          os.remove(File)
      traj+=1
