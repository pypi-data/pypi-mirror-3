"""
Next Reaction Method
====================
This module performs the Next Reaction Method from Gibson and Bruck [1]. Therefore, it is also called the Gibson and Bruck algorithm.

[1] M.A. Gibson and J. "Bruck Efficient Exact Stochastic Simulation of Chemical Systems with Many Species and Many
Channels", J. Phys. Chem., 2000,104,1876-1889

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 15, 2011
"""

from stochpy import model_dir
import sys,copy,time,heapq,cPickle,os
try: import numpy as np
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

try:from PyscesMiniModel import PySCeS_Connector  
except: from stochpy.PyscesMiniModel import PySCeS_Connector	# installed

try:
    sys.path.append(os.getcwd()+'/modules/')
    from Heap import *  
except:from stochpy.modules.Heap import * # installed  

try: from PyscesMiniModel import IntegrationStochasticDataObj
except: from stochpy.PyscesMiniModel import IntegrationStochasticDataObj	# installed

#############################################################
class NextReactionMethod(PySCeS_Connector):
  """ 
  Next Reaction Methfod from Gibson and Bruck [1].  

  Input:  
   - *File*: filename.psc
   - *dir*: /home/user/Stochpy/pscmodels/filename.psc
   - *OutputDir*: /home/user/Stochpy/
   - *TempDir*

  [1] M.A. Gibson and J. "Bruck Efficient Exact Stochastic Simulation of Chemical Systems with Many Species and Many
Channels", J. Phys. Chem., 2000,104,1876-1889
  """
  def __init__(self,File,dir,OutputDir,TempDir):
      self.OutputDir = OutputDir
      self.TempDir = TempDir
      self.IsExit = 0
      self.Parse(File,dir)
      if self.IsExit: sys.exit()  

  def Parse(self,File,dir):
      """
      Parses the PySCeS MDL input file, where the model is desribed

      Input:
       - *File*: filename.psc
       - *dir*:  /home/.../Stochpy/pscmodels/filename.psc
      """
      self.ModelFile = File
      self.ModelDir = dir
      try:
          parse = PySCeS_Connector(self.ModelFile,self.ModelDir,IsNRM = 1)	# parse model
          if parse.IsConverted:
              self.ModelFile += '.psc'
              self.ModelDir = model_dir

          self.N 		= parse.Mod.N.transpose()		# 22/01/11
          self.Xinit 	= parse.X.transpose()[0]		# 22/01/11

          self.reactants 	= parse.reactants
          self.species_ids  = parse.species
          self.reagents 	= parse.reagents
          self.rate_names   = parse.reactions
          self.propensities = parse.propensities
          self.species_names= parse.species_names
          self.affects      = parse.affects
          self.dep_graph    = parse.dep_graph
      except:
          self.IsExit = 1
          print "Error: It is impossible to parse the input file:", self.ModelFile, "from directory" , self.ModelDir
 
  def Execute(self,Trajectories,Endtime,Timesteps,TrackPropensities):       
    """
    Generates T trajectories of the markov jump process.
    Input: 
     - *Number of trajectories*
     - *Boolean for time or number of time steps simulation*
     - *Number of time steps or the sim. endtime*
    """
    self.species_pos = {}
    i=0
    for species in self.species_ids:
        self.species_pos[species] = i				# Determine once for each species the position in the X-matrix
        i+=1
    self.Dump = []
    self.X = self.Xinit.copy()
    self.M = len(self.propensities)				# Number of reactions
    self.a_mu = np.zeros(self.M)

    t1 = time.time()
    self.Trajectories = Trajectories
    self.Endtime = Endtime
    self.Timesteps = Timesteps
    self.IsTrackPropensities = TrackPropensities
    traj = 1
    if self.Trajectories == 1:					# 15/01/11
        print "Info: 1 trajectory is generated"
    else:
        file = open(self.OutputDir +'/ssa_sim.log','w')
        file.write("Trajectory\tNumber of time steps\tEnd time\n")
        print "Info:",self.Trajectories, "trajectories are generated\n"     
        print "Info: Time simulation output of the trajectories is stored at ",self.ModelFile[:-4]+'(traj_number).dat in directory: ',self.TempDir
        print "Info: output is written to:", self.OutputDir +'/ssa_sim.log'
    while traj<=self.Trajectories:
      self.t = 0
      self.BuildInits()   
      self.Propensities()      
      self.Initial_Conditions()
      if self.IsTrackPropensities:
          self.a_ravel = list(self.a_mu.ravel())
          self.a_ravel.insert(0,self.t)
          self.propensities_output.append(self.a_ravel)

      timestep = 0
      while self.t < self.Endtime and timestep < self.Timesteps:  
          self.a_0 = self.a_mu.sum()
          if self.a_0 <= 0: break                         # All reactants got exhausted              
          self.Run()                                      # Run next reaction method
           
          ### Start output Generation ###
          self.x_ravel = list(self.X)
          self.x_ravel.append(self.index+1) 
          self.x_ravel.insert(0,self.t)
          self.output.append(self.x_ravel)
          ###  End output Generation  ### 

          timestep += 1
          self.a_mu_prev = copy.copy(self.a_mu)                 
          self.vars_to_update = self.reagents[self.index] # Determine vars to update
          self.Propensities()                             # Update Propensities    
          if self.IsTrackPropensities:
              self.a_ravel = list(self.a_mu.ravel())
              self.a_ravel.insert(0,self.t)
              self.propensities_output.append(self.a_ravel)
          t_prev = self.output[timestep][0]
        
          for j in self.prop_to_update:
              if self.count == 999:
                  randoms = np.random.random(1000)  			# Create M random numbers
                  self.randoms_log = np.log(randoms)*-1
                  self.count = 0          
              if (self.a_mu_prev[j] > 0 and self.a_mu[j] >= 0):
                  if j == self.index:
                      tau_alpha = self.randoms_log[self.count]/self.a_mu_prev[j]+self.t
                      self.count+=1
                      self.a_mu_zero[j] = {'t1':self.t,'a_alpha_old':self.a_mu_prev[j],'tau_alpha':tau_alpha}
                  else:           
                      tau_alpha = self.taus[j]               
                      self.a_mu_zero[j] = {'t1':self.t,'a_alpha_old':self.a_mu_prev[j],'tau_alpha':tau_alpha}
          
          self.UpdateHeap()
          ##show_tree(self.tree.heap)  # //comment\\   
      self.X = self.Xinit.copy()        			# Reset X for next trajectory calc.
      #######################################   
      sim_dat = np.array(self.output,'d')
      self.data_stochsim = IntegrationStochasticDataObj()
      self.data_stochsim.trajectory = traj
      self.data_stochsim.setDist()
      self.data_stochsim.setTime(sim_dat[:,0])
      self.data_stochsim.setSpecies(sim_dat[:,1:-1], self.species_names)
      self.data_stochsim.setFiredReactions(sim_dat[:,-1][1:])
      if self.IsTrackPropensities: 
          self.data_stochsim.setPropensitiesLabels(self.rate_names)
          self.data_stochsim.setPropensities(self.propensities_output)
      ######################################

      if self.Trajectories == 1: print "Number of time steps",timestep," End time ",self.t
      elif self.Trajectories > 1:
          file.write(str(traj)+"\t"+ str(timestep) +"\t" + str(self.t)+"\n")
          name = self.TempDir+'/'+self.ModelFile+str(traj)+'.dat'
          cPickle.dump(self.data_stochsim,file = open(name,'w')) 	# Dump trajectory output
          self.Dump.append(name)      
      traj+=1
    t2 = time.time()
    print "Simulation time",t2-t1 

  def Initial_Conditions(self):                
      """
      This function initiates the output format with the initial concentrations
      output : A nested list, such as [[Time , 'X1','X2', 'R'],[0,100,100,'-'] ]
      """
      self.output = []    
      if self.IsTrackPropensities: self.propensities_output = []

      output_init = [self.t]      
      for init in self.X:                                    # Output at t = 0 
          if init < 0:
              print "Error: There are initial negative concentrations!"
              sys.exit()
          output_init.append(int(init))
      output_init.append(np.NAN)
      self.output.append(output_init)

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
      """
      Determines the propensities to fire for each reaction at the current time point. At t=0, all the rate equations are compiled. 
      """   
      if self.t == 0:			                            # Compile rate-eqs
        code_str = """"""      
        self.len = len(self.propensities)			        # Number of rate_eqs
        self.a_mu = np.zeros([self.len])			        # Initialize a(mu)
        for i in range(self.len):        
            code_str+='if self.rFire['+str(i)+']: r_vec['+str(i)+']='+self.propensities[i]+'\n'
 
        self.req_eval_code = compile(code_str,"RateEqEvaluationCode","exec")
        for s in range(len(self.species_ids)):              # Set species quantities
            setattr(self,self.species_ids[s],self.X[s])

      else:
          for s in self.vars_to_update:                     # Species to update   
              setattr(self,self.species_ids[s],self.X[s])
      self.rateFunc(self.req_eval_code,self.a_mu)           # Calc. Propensities 

  def Run(self):
      """ Perform a direct SSA time step and pre-generate M random numbers """ 
      #np.random.seed(5) 
      if self.t == 0:       
          randoms = np.random.random(self.M)                # Pre-generate for each time step M random numbers
          self.randoms_log_init = np.log(randoms)*-1
          self.InitialStep()

          self.count  = 0
          randoms = np.random.random(1000)                  # Create M random numbers
          self.randoms_log = np.log(randoms)*-1
      self.ReactionSelection()
      self.ReactionExecution()

      if self.count == 999:
          randoms = np.random.random(1000)                  # Create M random numbers
          self.randoms_log = np.log(randoms)*-1
          self.count = 0

  def InitialStep(self): 
      """ Monte Carlo step to determine all taus and to create a binary heap """
      self.taus = self.randoms_log_init[0:self.M]/self.a_mu # Calculate all initial taus
      pairs = []
      j=0
      while j<self.M:
          temp = (self.taus[j],j)
          pairs.append((self.taus[j],j))
          j+=1 	
      self.tree = BinaryHeap(pairs)                         # Create binary tree    
      ##show_tree(self.tree.heap)  

  def ReactionSelection(self):
      """ Function which selects a reaction that will fire once """
      self.rFire= np.zeros(self.M) 
      minimum = self.tree.heap[0]
      self.index =  minimum[1]                              # Pick reaction to executeO(1)
      tau = minimum[0]                                      # Pick tau O(1)     
      self.t = tau                                          # New time
      #self.r[self.index] = 1      
      self.prop_to_update = self.dep_graph[self.index]      # Propensities to update

      if self.index not in self.prop_to_update:
          self.prop_to_update.append(self.index)
      for pos in self.prop_to_update:
      #for i in range(len(self.rFire)):
          self.rFire[pos] = 1

  def ReactionExecution(self):
      """ Function that executes the selected reaction that will fire once """
      self.X += self.N[self.index]


  def UpdateHeap(self):       
      """
      This function calculates new tau values for reactions that are changed.
      After this calculations, the binary heap is updated, which is much more efficient then rebuilding the entire heap.
      """
      for j in self.prop_to_update:    
          location = self.tree.index[j]
          if j == self.index:                               # alpha = mu
              if self.count == 999:
                  randoms = np.random.random(1000)          # Create M random numbers
                  self.randoms_log = np.log(randoms)*-1
                  self.count = 0				
              if self.a_mu[j] != 0:
                  tau = self.randoms_log[self.count]/self.a_mu[j] + self.t
                  self.count +=1
              else: tau = 1000e1000
              self.taus[j] = tau
              self.tree.heap[location] = (tau,j)
          else:                                             # alpha != mu
              last_pos_a_mu = self.a_mu_zero[j]['a_alpha_old']
              t1 = self.a_mu_zero[j]['t1']
              if self.a_mu_prev[j] != 0 and last_pos_a_mu !=0: # a_j > 0
                  tau_alpha = self.taus[j]
                  tau = (float(self.a_mu_prev[j])/self.a_mu[j])*(tau_alpha-self.t)+self.t
              elif self.a_mu_prev[j] == 0 and last_pos_a_mu == 0 and t1 == 0:   # a_j zero from start
                  tau = self.randoms_log_init[j]/self.a_mu[j] + self.t
              else:                                         # a_j became zero after some time t1
                  tau_alpha = self.a_mu_zero[j]['tau_alpha']          
                  tau = (float(last_pos_a_mu)/self.a_mu[j])*(tau_alpha-t1)+self.t
              self.taus[j] = tau
              self.tree.heap[location] = (tau,j)
          self.tree.Done = 0
          while not self.tree.Done: self.tree.Update_AUX(tau,j) 

  def BuildInits(self):
      """
      Build initials that are necessary to generate a trajectory
      """    
      self.rFire= np.ones(self.M)
      self.a_mu_zero = []
      for i in range(0,self.M):
          self.a_mu_zero.append({'t1':0,'a_alpha_old':0,'tau_alpha':0})    
      self.taus = None                                      # Necessary for iteration
      self.tree = None                                      # Necessary for iteration 
