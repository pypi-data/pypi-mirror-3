#! /usr/bin/env python
import random,re
"""
Direct Method
=============
This module performs the Direct Stochastic Simulation Algorithm from Gillespie (1977) [1].

This algorithm is used to generate exact realizations of the Markov jump process. Of course, the algorithm is stochastic, so these realizations are different for each run.

Only molecule populations are specified. Positions and velocities, such as in Molecular Dynamics (MD) are ignored. This makes the algorithm much faster, because non-reactive molecular collisions can be ignored.different
Still, this exact SSA is quite slow, because it insists on simulating every individual reaction event, which takes a lot of time if the reactant population is large. Furthermore, even larger problems arise if the model contains distinct processes operating on different time scales [2].

[1] Gillespie D.T (1977), "Exact stochastic simulation of coupled chemical reactions", J.Phys. Chem. 81:2340-2361
[2] Wilkinson D.J (2009), "Stochastic Modelling for quantitative description of heterogeneous biological systems", Nat Rev Genet; 0(2):122-133 

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: 23 October, 2011
"""

__doc__ = """
          Direct Method
          =============
          This program performs the direct Stochastic Simulation Algorithm from Gillespie (1977) [1].This algorithm is used to generate exact realizations of the Markov jump process. Of course, the algorithm is stochastic, so these realizations are different for each run.
          Only molecule populations are specified. Positions and velocities, such as in Molecular Dynamics (MD) are ignored. This makes the algorithm much faster, because non-reactive molecular collisions can be ignored.
          Still, this exact SSA is quite slow, because it insists on simulating every individual reaction event, which takes a lot of time if the reactant population is large. Furthermore, even larger problems arise if the model contains distinct processes operating on different time-scales [2].
          
          [1] Gillespie D.T (1977), "Exact stochastic simulation of coupled chemical reactions", J.Phys. Chem. 81:2340-2361
          [2] Wilkinson D.J (2009), "Stochastic Modelling for quantitative description of heterogeneous biological systems", Nat Rev Genet; 0(2):122-133
          """
############################# IMPORTS ####################################

import sys,copy,time,cPickle
from stochpy import model_dir

try: 
    import numpy as np
    np.seterr(divide = 'ignore') # catch the divide by zero error if species start at zero
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

try: from PyscesMiniModel import PySCeS_Connector
except: from stochpy.PyscesMiniModel import PySCeS_Connector	# installed

try: from PyscesMiniModel import IntegrationStochasticDataObj
except: from stochpy.PyscesMiniModel import IntegrationStochasticDataObj	# installed

########################### END IMPORTS ##################################
  
############################# Classes ####################################

class Species():
  def __init__(self):
    """ Object that is created to store the species amounts """
    pass
    
__species__ = Species()

class DirectMethod(PySCeS_Connector):
  """ 
  Direct Stochastic Simulation Algorithm from Gillespie (1977) [1].

  This algorithm is used to generate exact realizations of the Markov jump process. Of course, the algorithm is stochastic, so these realizations are different for each run.

  [1] Gillespie D.T (1977), "Exact stochastic simulation of coupled chemical reactions", J.Phys. Chem. 81:2340-2361

  Input:  
   - *File*: filename.psc
   - *dir*: /home/user/Stochpy/pscmodels/filename.psc
   - *OutputDir*: /home/user/Stochpy/ 
   - *TempDir*
  """
  def __init__(self,File,dir,OutputDir,TempDir):
      self.OutputDir = OutputDir
      self.TempDir = TempDir                                        # 15 January 2011
      self.IsExit = False
      self.Parse(File,dir)
      #if self.IsExit: 
      #   sys.exit()

  def Parse(self,File,dir):
      """
      Parses the PySCeS MDL input file, where the model is desribed
 
      Input:
       - *File*: filename.psc
       - *dir*:  /home/user/Stochpy/pscmodels/filename.psc
      """
      self.ModelFile = File
      self.ModelDir = dir           
      try:
          self.parse = PySCeS_Connector(self.ModelFile,self.ModelDir)	# Parse model  
          if self.parse.IsConverted:
              self.ModelFile += '.psc'
              self.ModelDir = model_dir
          self.N_matrix = copy.deepcopy(self.parse.Mod.N.transpose())   # 22 January 2011
          self.X_matrixinit = copy.deepcopy(self.parse.X_matrix.transpose()[0])
          self.species_stochmatrix = copy.deepcopy(self.parse.species)
          self.reagents = copy.deepcopy(self.parse.reagents)
          self.rate_names = copy.deepcopy(self.parse.reactions)
          self.propensities = copy.deepcopy(self.parse.propensities)
          self.fixed_species = copy.deepcopy(self.parse.fixed_species)
          self.fixed_species_amount = copy.deepcopy(self.parse.fixed_species_amount)
          self.aDict = copy.deepcopy(self.parse.Mod.__aDict__)
          self.eDict = copy.deepcopy(self.parse.Events)
          self.species = copy.deepcopy(self.species_stochmatrix)
          for species in sorted(self.aDict):
              self.species.append(species)

          self.species_pos = {}
          i=0
          for species in self.species:
              self.species_pos[species] = i                              # Determine once for each species
              i+=1 
          self.sim_dump = []
          self.number_of_reactions = len(self.propensities)              # Number of reactions
      except:
          self.IsExit = True
          print "Error: It is impossible to parse the input file:", self.ModelFile, "from directory" , self.ModelDir    

  def Execute(self,Trajectories,Endtime,Timesteps,TrackPropensities):       
    """
    Generates T trajectories of the Markov jump process.

    Input:
     - *Trajectories*: (integer)
     - *Endtime* (float)
     - *Timesteps* (integer)
     - *TrackPropensities*: (boolean)

    Endtime or Timesteps is infinite
    """
    t1 = time.time()
    self.sim_a_mu = np.zeros(self.number_of_reactions)
    self.X_matrix = self.X_matrixinit.copy()
    self.Trajectories = Trajectories
    self.Endtime = Endtime
    self.Timesteps = Timesteps
    self.IsTrackPropensities = TrackPropensities
    traj = 1
    if self.Trajectories == 1: print "Info: 1 trajectory is generated"   # 15 January 2011
    else:
        file = open(self.OutputDir +'/ssa_sim.log','w')
        file.write("Trajectory\tNumber of time steps\tEnd time\n")
        print "Info:",self.Trajectories, "trajectories are generated\n"     
        print "Info: Time simulation output of the trajectories is stored at ",self.ModelFile[:-4]+'(traj_number).dat in directory: ',self.TempDir
        print "Info: output is written to:", self.OutputDir +'/ssa_sim.log'
    while traj<=self.Trajectories:
      self.sim_t = 0
      self.GetEventAtTime()
      self.GetEventAtAmount()
      self.Propensities()
      self.Initial_Conditions()
      timestep = 0
      #####################
      if self.aDict != {}: # TODO
            self.AssignmentRules(timestep)
            i=0
            for value in self.aDict_species:
                self.sim_output[timestep][self.aDict_indices[i]] = value
                i+=1
      #####################
      while self.sim_t < self.Endtime and timestep < self.Timesteps:
          self.sim_a_0 = self.sim_a_mu.sum()
          if self.sim_a_0 <= 0: break                                    # All reactants got exhausted
          self.Run()                                                     # Run direct SSA
             
          if self.sim_t > self.event_time and self.event_time != None:   # Time Event
              self.DoEvent()
              self.sim_t = copy.copy(self.event_time)
              self.event_time = None
          
          if self.event_amount != None:                                  # Amount Event
              if self.X_matrix[self.event_amount_index] > self.event_amount: self.DoEvent()          
          
          try:                                                           # Add 'dt' to a species amount
              for i in range(len(self.X_matrix)):
                self.distributions[i][self.sim_output[timestep][i+1]] += self.sim_t - self.sim_output[timestep][0]
          except:
              for i in range(len(self.X_matrix)):
                self.distributions[i][self.sim_output[timestep][i+1]] = self.sim_t - self.sim_output[timestep][0]
          
          ### Start output Generation ### TODO
          temp = list(self.X_matrix)
          for amount in self.fixed_species_amount: temp.append(amount)
          if self.aDict != {}:
              self.AssignmentRules(timestep)
              for value in self.aDict_species: temp.append(value)
          temp.append(self.reaction_index+1)
          temp.insert(0,self.sim_t)
          self.sim_output.append(temp)
          ###  End output Generation  ###
	
          timestep += 1
          self.to_update = self.reagents[self.reaction_index]            # Determine vars to update           
          self.Propensities()                                            # Update Propensities
          if self.IsTrackPropensities:
              a_ravel = list(self.sim_a_mu.ravel())
              a_ravel.insert(0,self.sim_t)
              self.propensities_output.append(a_ravel)
                
      self.X_matrix = self.X_matrixinit.copy()                           # Reset X for next trajectory calc.
      #######################################   TODO      
      self.FillDataStochsim()
      self.data_stochsim.setSimulationInfo(timestep,self.sim_t,traj)
      ######################################
      if self.Trajectories == 1: print "Number of time steps",timestep," End time ",self.sim_t
      elif self.Trajectories > 1:
          file.write(str(traj)+"\t"+ str(timestep) +"\t" + str(self.sim_t)+"\n")
          name = self.TempDir+'/'+self.ModelFile+str(traj)+'.dat'
          cPickle.dump(self.data_stochsim,file = open(name,'w'))         # Dump trajectory output
          self.sim_dump.append(name)
      traj+=1

    t2 = time.time()
    if self.Trajectories > 1: file.close()
    print "Simulation time",t2-t1

  def Initial_Conditions(self):              
      """ This function initiates the output format with the initial concentrations """
      self.sim_output = []
      if self.IsTrackPropensities:
         self.propensities_output = []
         a_ravel = list(self.sim_a_mu.ravel())
         a_ravel.insert(0,self.sim_t)
         self.propensities_output.append(a_ravel)

      output_init = [self.sim_t]
      for init in self.X_matrix:                                         # Output at t = 0 
          if init < 0:
              print "Error: There are initial negative concentrations!"
              sys.exit()
          output_init.append(int(init))

      for amount in self.fixed_species_amount: output_init.append(amount)
      self.aDict_indices = []
      if self.aDict != {}:
           for species in sorted(self.aDict):
               output_init.append(self.parse.Mod.__pDict__[species]['initial'])
               self.aDict_indices.append(len(output_init)-1)
      output_init.append(np.NAN)
      self.sim_output.append(output_init)
      
      self.distributions = []
      for i in range(len(self.X_matrix)):
          self.distributions.append({})      

  def GetEventAtTime(self):
      """ Get times where events happen"""
      self.event_time = None
      if 'reset' in sorted(self.eDict):
          if 'TIME' in self.eDict['reset']['trigger']:
              m = re.search(', *\d+',self.eDict['reset']['trigger'])
              self.event_time = float(m.group(0)[1:])

  def GetEventAtAmount(self):
      """ Get amount where events happen """
      self.event_amount = None
      if 'reset' in sorted(self.eDict):
          i=0
          for species in self.species_stochmatrix:
              if re.search('\( *'+species+' *,',self.eDict['reset']['trigger']):
                  m = re.search(', *\d+',self.eDict['reset']['trigger'])
                  self.event_amount = float(m.group(0)[1:])
                  self.event_amount_index = i
                  break
              i+=1

  def DoEvent(self): 
      """ Do the event of the model """
      i=0
      for species in self.species_stochmatrix:
          if species in self.eDict['reset']['assignments']:
              self.X_matrix[i] = float(self.eDict['reset']['assignments'][species])                     
              if i not in self.to_update: self.to_update.append(i)      # Update species value for propensities for next reaction fire
          i+=1 

  def AssignmentRules(self,timestep):
       """
       Builds the assignment rules
       
       Input:
        -*timestep*: (integer)
       """ 
       code_string = """"""
       if self.sim_t == 0:
           self.aDict_species_labels = []
           for species in self.species_stochmatrix:
               for aDict_species in sorted(self.aDict):
                   if species in self.aDict[aDict_species]['formula']: self.aDict_species_labels.append(species)

       for i in range(len(self.aDict_species_labels)):
           species_value = self.X_matrix[i]
           code_string += str(self.species_stochmatrix[i]) + '=' + str(species_value) + '\n'        
       self.aDict_species = np.zeros(len(self.aDict))
       i=0
       for species in sorted(self.aDict):
           code_string += 'self.aDict_species[' + str(i)+']=' + str(self.aDict[species]['formula']) + '\n'
           i+=1
       self.rateFunc(code_string,self.aDict_species)

  def rateFunc(self,rate_eval_code,r_vec):
      """
      Calculate propensities from the compiled rate equations
     
      Input:
       - *rate_eval_code*: compiled rate equations
       - *r_vec*: output for the calculated propensities
      """
      try: exec(rate_eval_code)     
      except:
          print "Error: It is impossible to determine the propensities. Check if all variable concentrations are initialized"
          sys.exit()

  def Propensities(self):
      """ Determines the propensities to fire for each reaction at the current time point. At t=0, all the rate equations are compiled. """   
      if self.sim_t == 0:                                                   # Compile rate-eqs
          code_str = """"""          
          self.sim_a_mu = np.zeros([self.number_of_reactions])              # Initialize a(mu)
          for i in range(self.number_of_reactions): code_str+='r_vec['+str(i)+']='+self.propensities[i]+'\n'
          self.req_eval_code = compile(code_str,"RateEqEvaluationCode","exec")
          for s in range(len(self.species_stochmatrix)):                    # Set species quantities              
              setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s])              
      else:
          for s in self.to_update:                                          # Species to update 
              setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s])      
      self.rateFunc(self.req_eval_code,self.sim_a_mu)                       # Calc. Propensities 
      if self.sim_a_mu.min() < 0:
          print "Error: Negative propensities are found"
      else: self.sim_a_mu = abs(self.sim_a_mu)
        
  def Run(self):
      """ Calculates a time step of the Direct Method """ 
      #np.random.seed(5)   
      if self.sim_t== 0:
          randoms = np.random.random(1000) 
          self.randoms_log = np.log(randoms)*-1
          self.randoms = np.random.random(1000)
          self.count = 0
       
      elif self.count == 1000:
          randoms = np.random.random(1000) 
          self.randoms_log = np.log(randoms)*-1
          self.randoms = np.random.random(1000)    
          self.count = 0     
    
      self.MonteCarlo()      
      self.ReactionSelection()
      self.ReactionExecution()    
  
  def MonteCarlo(self):
      """ Monte Carlo step to determine tau """    
      self.sim_r2  = self.randoms[self.count]                               # Draw random number 2 [0-1]
      self.sim_tau = self.randoms_log[self.count]/float(self.sim_a_0)       # reaction time generation    
      self.sim_t += self.sim_tau                                            # Time update
      self.count +=1

  def ReactionSelection(self):
      """ Function which selects a reaction that will fire once """
      self.reaction_index = 0
      sum_of_as = self.sim_a_mu[self.reaction_index]
      criteria =  self.sim_r2*self.sim_a_0
      while sum_of_as < criteria:                                           # Use r2 to determine which reaction will occur
          self.reaction_index += 1	                                        # Index
          sum_of_as += self.sim_a_mu[self.reaction_index]    

  def ReactionExecution(self):
      """ Function that executes the selected reaction that will fire once """
      try: self.X_matrix += self.N_matrix[self.reaction_index]
      except MemoryError: sys.exit() 
      
  def GetDistributions(self):
      """ Get means, standard deviations and the probability at each species amount value""" 
      dist = []
      means = {}
      sds = {}
      for i in range(len(self.X_matrix)):
          x_i = np.array(sorted(self.distributions[i]),dtype=int)
          y_i = np.array(self.distributions[i].values())/self.sim_t           # probability = dt/T
          mean = sum(x_i*y_i)
          mean_sqrt = sum(x_i*x_i*y_i)
          var = mean_sqrt - mean*mean
          sd = var**0.5          
          dist.append([x_i,y_i])
          means[self.species[i]] = mean
          sds[self.species[i]] = sd
      return dist,means,sds

  def FillDataStochsim(self):
      """ Put all simulation data in the data object data_stochsim"""
      (dist, means, sds) = self.GetDistributions()
      sim_dat = np.array(self.sim_output,'d')
      self.data_stochsim = IntegrationStochasticDataObj()
      self.data_stochsim.setTime(sim_dat[:,0])
      self.data_stochsim.setDist(dist,means,sds)
      all_species = copy.copy(self.species)
      for species in self.fixed_species: all_species.append(species)     # 17 September 2011
      self.data_stochsim.setSpecies(sim_dat[:,1:-1],all_species)
      self.data_stochsim.setFiredReactions(sim_dat[:,-1][1:])
      if self.IsTrackPropensities: 
          self.data_stochsim.setPropensitiesLabels(self.rate_names)
          self.data_stochsim.setPropensities(self.propensities_output)
