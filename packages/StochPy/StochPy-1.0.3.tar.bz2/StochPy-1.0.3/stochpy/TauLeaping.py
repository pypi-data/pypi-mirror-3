#! /usr/bin/env python
"""
Optimized Tau-Leaping
=====================

This program performs Optimized Explicit Tau-leaping algorithm, which is an approximate version of the exact Stochastic Simulation Algorithm (SSA). Here, an efficient step size selection procedure for the tau-leaping method [1] is used.

[1] Cao. Y, Gillespie D., Petzold L. (2006), "Efficient step size selection for the tau-leaping method", J.Chem. Phys. 28:124-135

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: November 16, 2011
"""
############################## IMPORTS ###################################

from stochpy import model_dir
import sys,copy,re,time,os,cPickle,random

try: 
    import numpy as np
    np.seterr(divide = 'ignore') # catch the divide by zero error if species start at zero
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

try:from PyscesMiniModel import PySCeS_Connector
except: from stochpy.PyscesMiniModel import PySCeS_Connector	# installed

try:from PyscesMiniModel import IntegrationStochasticDataObj
except: from stochpy.PyscesMiniModel import IntegrationStochasticDataObj	# installed

########################### END IMPORTS ##################################

class Species():
  def __init__(self):
    """ Object that is created to store the species amounts """
    pass
    
__species__ = Species()

class OTL(PySCeS_Connector):
  """  
  Input:
   - *File*: filename.psc
   - *dir*:    /home/user/Stochpy/pscmodels/filename.psc
   - *Outputdir*: /home/user/Stochpy/ 
  """
  def __init__(self,File,dir,OutputDir,TempDir):
    self.OutputDir = OutputDir
    self.TempDir = TempDir
    self.IsExit = False
    self.Parse(File,dir)
    #if self.IsExit: sys.exit()  

  def Parse(self,File,dir):
    """
    Parses the PySCeS MDL input file, where the model is described

    Input:
     - *File*: filename.psc
     - *dir*: /home/user/Stochpy/pscmodels/filename.psc
    """
    self.ModelFile = File
    self.ModelDir = dir
    try:
        self.parse = PySCeS_Connector(self.ModelFile,self.ModelDir)	         # Parse model      
        if self.parse.IsConverted:
            self.ModelFile += '.psc'
            self.ModelDir = model_dir

        self.N_matrix = copy.deepcopy(self.parse.Mod.N)
        self.N_matrix_transpose = copy.deepcopy(self.N_matrix.transpose())    # 22 January 2011
        self.X_matrixinit = copy.deepcopy(self.parse.X_matrix.transpose()[0]) # 22 January 2011   
        self.reactants = copy.deepcopy(self.parse.reactants)
        self.species_stochmatrix = copy.deepcopy(self.parse.species)
        self.reagents = copy.deepcopy(self.parse.reagents)
        self.rate_names = copy.deepcopy(self.parse.reactions)
        self.propensities = copy.deepcopy(self.parse.propensities)
        self.fixed_species = copy.deepcopy(self.parse.fixed_species)
        self.fixed_species_amount = copy.deepcopy(self.parse.fixed_species_amount)
        self.rate_eqs = copy.deepcopy(self.parse.rate_eqs)
        self.aDict = copy.deepcopy(self.parse.Mod.__aDict__)
        self.eDict = copy.deepcopy(self.parse.Events)
        self.species = copy.deepcopy(self.species_stochmatrix)
        for species in sorted(self.aDict):
             self.species.append(species)
        self.species_pos  = {}
        i=0
        for species in self.species:
            self.species_pos[species] = i                       # Determine once for each species the position in the X-matrix
            i+=1
        self.sim_dump = [] 
        self.number_of_reactions = len(self.propensities)       # Number of reactions
        self.DetOptions = True
        self.IsFirst = True
    except:
        self.IsExit = True
        print "Error: It is impossible to parse the input file:", self.ModelFile, "from directory" , self.ModelDir
    
  def Execute(self,Trajectories,Endtime,Timesteps,TrackPropensities,epsilon = 0.03):
    """
    Generates T trajectories of the Markov jump process.

    Input:
     - *Trajectories* (integer)
     - *Endtime* (float)
     - *Timesteps* (integer)
     - *TrackPropensities* (boolean)
     - *epsilon* [default = 0.03] (float)
     
    Endtime or Timesteps is infinite
    """
    self.sim_a_mu = np.zeros(self.number_of_reactions)
    self.sim_epsilon = epsilon
    self.sim_Nc = 10
    self.g_vector = np.zeros(len(self.X_matrixinit))            # Initialize g vector 
    self.num_species = len(self.X_matrixinit)    
    self.sim_mu  = np.zeros(self.num_species)                   # Init mu  (32.a)
    self.sim_var = np.zeros(self.num_species)                   # Init var (32.b)
    self.state_change_vector = np.transpose(self.N_matrix)
    t1 = time.time()
    self.X_matrix = self.X_matrixinit.copy()
    self.Trajectories = Trajectories
    self.Endtime = Endtime
    self.Timesteps = Timesteps
    self.initOTLstep = 1
    self.IsTrackPropensities = TrackPropensities
    traj = 1
    if self.Trajectories == 1: print "Info: 1 trajectory is generated"
    else:
        file = open(self.OutputDir +'/ssa_sim.log','w')
        file.write("Trajectory\tNumber of time steps\tEnd time\tRatio of OTL steps\n")
        print "Info:",self.Trajectories, "trajectories are generated\n"     
        print "Info: Time simulation output of the trajectories is stored at ",self.ModelFile[:-4]+'(traj_number).dat in directory: ',self.TempDir
        print "Info: output is written to:", self.OutputDir +'/ssa_sim.log'
    while traj<=self.Trajectories:
    
      if self.IsFirst:
          self.IsFirst = False
          randoms = np.random.random(1000)
          self.randoms_log = np.log(randoms)*-1
          self.randoms = np.random.random(1000)
          self.count = 0      

      IsNegative = False
      self.sim_t = 0
      tauleapsteps = 0
      self.GetEventAtTime()
      self.GetEventAtAmount()
      self.Propensities()
      self.Initial_Conditions()
      (orders,hors,HO_info) = DetermineOrderHOR(self.rate_eqs,self.reactants)
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
        if not IsNegative:				        # If there are no negative conc. after a Tau-leap step
            self.CriticalReactions()   
            self.Propensities()
            self.GetG(orders,hors,HO_info)
            self.sim_a_0 = self.sim_a_mu.sum()           
            if self.sim_a_0 <= 0:                                          # All reactants got exhausted
                if self.Endtime < self.Timesteps:
                    last_output = self.sim_output[-1]
                    last_output[0] = self.Endtime
                    self.sim_output.append(last_output)
                break	
            self.GetMuVar()
            self.GetTauPrime()

        ##################### start Possible Feedback loop ##################
        self.DetermineMethod()
        ##### Optimized Tau-Leaping step #####

        if self.IsOTL:
          self.GetTauPrimePrime()
          self.GetK()
          self.Execute_K_Reactions()
          if not self.IsNegative:
            if self.IsTrackPropensities:
                a_ravel = list(self.sim_a_mu.ravel())
                a_ravel.insert(0,self.sim_t)
                self.propensities_output.append(a_ravel)

            self.sim_t += self.sim_tau
            IsNegative = False
            if self.sim_t > self.event_time and self.event_time != None:
                self.DoEvent()
                self.sim_t = copy.copy(self.event_time)
                self.event_time = None
            if self.event_amount != None:
                if self.X_matrix[self.event_amount_index] > self.event_amount: self.DoEvent()
            
            for i in range(len(self.X_matrix)):
                try:
                    self.distributions[i][self.sim_output[timestep][i+1]] += self.sim_t - self.sim_output[timestep][0]
                except:
                    self.distributions[i][self.sim_output[timestep][i+1]] = self.sim_t - self.sim_output[timestep][0]

            ### Start output Generation ### TODO
            temp = list(self.X_matrix)
            for amount in self.fixed_species_amount: temp.append(amount)
            if self.aDict != {}:
                self.AssignmentRules(timestep)
                for value in self.aDict_species: temp.append(value)
            temp.insert(0,self.sim_t)
            #for IsReaction in self.K_vector_vector.ravel(): temp.append(IsReaction)    # 15 September 2011
            ###  End output Generation  ### 
            tauleapsteps +=1
          elif self.IsNegative:                                 # Start feedback loop
              IsNegative = True
              self.sim_tau_prime = self.sim_tau_prime/2.0   
        elif self.IsExact:                                      # Direct SSA step
          m = 0         
          while m < 100 and self.sim_t < self.Endtime and timestep < self.Timesteps:
            self.Propensities()
            if self.IsTrackPropensities:
                a_ravel = list(self.sim_a_mu.ravel())
                a_ravel.insert(0,self.sim_t)
                self.propensities_output.append(a_ravel)

            self.sim_a_0 = self.sim_a_mu.sum()  
            if self.sim_a_0 <= 0:                                          # All reactants got exhausted
               if self.Endtime < self.Timesteps:
                   last_output = self.sim_output[-1]
                   last_output[0] = self.Endtime
                   self.sim_output.append(last_output)                 
               break       
            self.RunExactSSA()
                
            if self.sim_t > self.event_time and self.event_time != None:
                self.DoEvent()                                 # Time Event
                self.sim_t = copy.copy(self.event_time)
                self.event_time = None                
            if self.event_amount != None:                      # Amount Event
                if self.X_matrix[self.event_amount_index] > self.event_amount: self.DoEvent()
                
            try:
              for i in range(len(self.X_matrix)):              # Add dt to each species amount
                self.distributions[i][self.sim_output[timestep][i+1]] += self.sim_t - self.sim_output[timestep][0]
            except:
              for i in range(len(self.X_matrix)):
                self.distributions[i][self.sim_output[timestep][i+1]] = self.sim_t - self.sim_output[timestep][0]   
 
            ### Start output Generation ###
            temp = list(self.X_matrix)
            for amount in self.fixed_species_amount: temp.append(amount)
            if self.aDict != {}:
                self.AssignmentRules(timestep)
                for value in self.aDict_species: temp.append(value)
            temp.insert(0,self.sim_t)
            ###  End output Generation  ###
            if m < 99:
                self.sim_output.append(temp)
                timestep +=1
            m+=1
        #################### End possible feedback loop #################
        timestep +=1
        if not IsNegative: self.sim_output.append(temp)        
        
      self.X_matrix = self.X_matrixinit.copy()     			         # Reset X for next trajectory calc.
      #######################################      
      self.FillDataStochsim()    
      self.data_stochsim.setSimulationInfo(timestep,self.sim_t,traj)
      ######################################
      if self.Trajectories == 1:
          print "Number of time steps",timestep," End time",self.sim_t
          print "Ratio OTL steps",tauleapsteps/float(timestep),
          print "Number of OTL time steps:",tauleapsteps     
      elif self.Trajectories > 1:
          file.write(str(traj)+"\t"+ str(timestep) +"\t" + str(self.sim_t)+"\n")
          name = self.TempDir+'/'+self.ModelFile+str(traj)+'.dat'
          cPickle.dump(self.data_stochsim,file = open(name,'w')) 	# Dump trajectory output
          self.sim_dump.append(name)
      traj+=1
    t2 = time.time()
    if self.Trajectories > 1: file.close()
    print "Simulation time",t2-t1

  def RunExactSSA(self):
      """ Perform a direct method SSA time step"""
      if self.count == 1000:
          randoms = np.random.random(1000)
          self.randoms_log = np.log(randoms)*-1
          self.randoms = np.random.random(1000)
          self.count = 0    
      self.MonteCarlo()
      self.ReactionSelection()
      self.ReactionExecution()    
  
  def MonteCarlo(self):
      """ Monte Carlo step to determine tau """    
      self.sim_r2  = self.randoms[self.count]                   # Draw random number 2 [0-1]    
      self.sim_tau = self.randoms_log[self.count]/self.sim_a_0  # reaction time generation
      self.sim_t += self.sim_tau                                # Time update
      self.count+=1

  def ReactionSelection(self):
      """ Function which selects a reaction that will fire once """
      self.reaction_index = 0
      sum_of_as = self.sim_a_mu[self.reaction_index]
      criteria =  self.sim_r2*self.sim_a_0
      while sum_of_as < criteria:                               # Use r2 to determine which reaction will occur
          self.reaction_index += 1	                            # Index
          sum_of_as += self.sim_a_mu[self.reaction_index]

  def ReactionExecution(self):
      """ Function that executes the selected reaction that will fire once """
      try: self.X_matrix += self.N_matrix_transpose[self.reaction_index]
      except MemoryError: sys.exit() 

  def CriticalReactions(self):
      """ Determines the critical reactions (as a boolean vector) """
      if self.initOTLstep:
          self.initOTLstep = 0
          self.N__ = copy.copy(self.N_matrix)
          self.N__ = np.transpose(self.N__)
          self.N__[self.N__>=0]= np.nan
    
      self.critical_reactions = []
      x = self.X_matrix.ravel()
      output = x/abs(self.N__)
      minima = np.nanmin(output,axis=1)
      for reaction in minima:
          if reaction < self.sim_Nc:
              self.critical_reactions.append(1)
          else:
              self.critical_reactions.append(0)

  # SLOW 
  def GetG(self,orders,hors,hor_info):        
    """
    Determine the G-vector

    Input:
     - *orders*
     - *hors*: highest order of reaction for each species
     - *hor_info*
    """ 
    if self.DetOptions:
      #self.options = [0,0,0]
      self.options = np.zeros(len(self.X_matrixinit)) 		# bug fixed 12/11/10
      self.DetOptions = False
      i=0      
      for species in self.species_stochmatrix: 
        j=0
        for reactants in self.reactants:        
            if species in reactants:
                if orders[j] == 1 and self.g_vector[i] == 0:
                    self.options[i] = 1
                elif orders[j] == 2:
                    if hors[j] == 2 and self.g_vector[i]<2: self.options[i] = 2
                    elif hors[j] == 1 and self.g_vector[i]<2:
                        self.g_vector[i] = 2
                        self.options[i] = 3  
                elif orders[j] == 3:
                    if hors[j] == 1: self.options[i] = 4
                    elif hors[j] == 2:
                        if species == hor_info[j]: self.options[i] = 5
                        else:self.options[i] = 4
                    else: self.options[i] = 6
            j+=1 
        i+=1
    
    self.g_vector = np.ones(len(self.X_matrixinit)) 		# bug fixed 12/11/10
    i=0
    for option in self.options:      
        if option == 1: self.g_vector[i] = 1
        elif option == 2: self.g_vector[i] = 2 + 1.0/(self.X_matrix[i]-1)
        elif option == 3: self.g_vector[i] = 2
        elif option == 4: self.g_vector[i] = 3
        elif option == 5:
            try: self.g_vector[i] = 3 + 1.5/(self.X_matrix[i]-1)
            except: self.g_vector[i] = 3
        elif option == 6:
            try: self.g_vector[i] = 3 + 1.0/(self.X_matrix[i]-1) + 2.0/(self.X_matrix[i]-2)
            except: self.g_vector[i] = 3
        i+=1    

  def GetMuVar(self):
      """ Calculate the estimates of mu and var for each species (i) """      
      i=0
      for v_i in self.N_matrix:
          self.sim_mu[i] = np.dot(v_i,self.sim_a_mu)
          self.sim_var[i]= np.dot(v_i*v_i,self.sim_a_mu)
          i+=1

  def GetTauPrime(self):
      """ Calculate tau' """
      part = np.divide(self.X_matrix.ravel(),self.g_vector)*self.sim_epsilon # eps*x[i]/g[i] for all i
      num = np.array([part,np.ones(len(part))])              # eps*x[i]/g[i] for all i , 1 for all i
      numerator = num.max(axis=0)                            # max(eps*x[i]/g[i],1) for all i
      abs_mu = np.abs(self.sim_mu)                           # abs(mu) for all i
      bound1 = np.divide(numerator,abs_mu)                   # max(eps*x[i]/g[i],1) / abs(mu[i]) for all i
      numerator_square = np.square(numerator)    	
      bound2 = np.divide(numerator_square,self.sim_var)      # max(eps*x[i]/g[i],1)^2 / abs(mu[i]) for all i
      tau_primes = np.array([bound1,bound2])			
      try:
          self.sim_tau_prime = np.min(tau_primes[~np.isnan(tau_primes)])# min (bound1,bound2)
      except:
          self.sim_tau_prime = 10**6
      
  def DetermineMethod(self):
      """ Determines for each time step what to perform: exact of approximate SSA """         
      criteria = 10.0/self.sim_a_0                           # Based on literature [2] (Cao et et. 2006)
      if self.sim_tau_prime > criteria and self.sim_tau_prime != 10**6:
          self.IsExact = False
          self.IsOTL = True
      else:
          self.IsExact = True
          self.IsOTL = False

  def GetA0c(self):
      """ Calculate the total propensities for all critical reactions """
      self.sim_a_0_c = np.dot(self.critical_reactions,self.sim_a_mu)
  
  def GetTauPrimePrime(self):
      """ Calculate Tau'' """
      if self.count == 1000:                                 # Re-generate random numbers
          randoms = np.random.random(1000)  
          self.randoms_log = np.log(randoms)*-1         
          self.count = 0      
      self.GetA0c()  
      if self.sim_a_0_c == 0:					             # a_0_c = 0
          self.sim_tau_prime_prime = 10**6
      elif self.sim_a_0_c != 0:
          self.sim_tau_prime_prime = self.randoms_log[self.count]/self.sim_a_0_c
          self.count+=1      

  def GetK(self):        
    """ Determines the K-vector, which describes the number of firing reactions for each reaction. """
    self.K_vector = np.zeros((self.number_of_reactions,1),dtype = int)
    if self.sim_tau_prime < self.sim_tau_prime_prime:        # tau' < tau''
      self.sim_tau = self.sim_tau_prime
      j=0 
      for IsCritical in self.critical_reactions:        
        if not IsCritical:
            a_j = self.sim_a_mu[j]
            Lambda = self.sim_tau * a_j       
            k_j = np.random.poisson(Lambda)           
            self.K_vector[j] = [k_j] 
        j+=1      
    else:
      self.sim_tau = self.sim_tau_prime_prime                # tau' > tau''
      j = 0
      probs = []
      IsCrit = False
      for IsCritical in self.critical_reactions:         
          a_j = self.sim_a_mu[j]
          if IsCritical:
              IsCrit = True
              p = float(a_j)/self.sim_a_0          
              probs.insert(j,p)
              if p == 1:                                     # Only one critical reaction
                  self.K_vector[j] = [1]
          elif not IsCritical:
              probs.insert(j,0.0)
              Lambda = self.sim_tau * a_j
              k_j = np.random.poisson(Lambda)
              self.K_vector[j] = [k_j]
          j+=1
      if IsCrit:                                             # Bug fixed jan 15 2011
          (prob,index) = GetSample(probs)                    # Select one crit.reaction that fires once
          self.K_vector[index] = [1]

  def Execute_K_Reactions(self):
      """ Perform the determined K reactions """
      self.IsNegative = False  
      x_temp  = copy.copy(self.X_matrix)    
      x_temp += np.dot(self.N_matrix,self.K_vector).ravel()     
      MinConc = x_temp.min()
      if MinConc < 0:                                        # Check for negatives after the K reactions 
          self.sim_tau = self.sim_tau/2.0
          self.IsNegative = True
      else: self.X_matrix = x_temp                           # Confirm the done K reactions
          
  def Initial_Conditions(self):                
      """ This function initiates the output format with the initial concentrations  """
      self.sim_output = []    
      if self.IsTrackPropensities: 
          self.propensities_output = []           
          a_ravel = list(self.sim_a_mu.ravel())
          a_ravel.insert(0,self.sim_t)
          self.propensities_output.append(a_ravel)

      output_init = [self.sim_t]      
      for init in self.X_matrix:                             # Output at t = 0 
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
             #if i not in self.to_update: self.to_update.append(i)   # update species value for propensities for next reaction fire
         i+=1

  def AssignmentRules(self,timestep):
       """
       Builds the assignment rules
       
       Input:
        -*timestep*: integer
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
      exec(rate_eval_code)       

  def Propensities(self):
      """
      Determines the propensities to fire for each reaction at the current time point. At t=0, all the rate equations are compiled. 
      """   
      if self.sim_t == 0:		                            # Compile rate-eqs
          code_str = """"""
          self.sim_a_mu = np.zeros([self.number_of_reactions]) # Initialize a(mu)
          for i in range(self.number_of_reactions):
              code_str+='r_vec['+str(i)+']='+self.propensities[i]+'\n'
          self.req_eval_code = compile(code_str,"RateEqEvaluationCode","exec")
          for s in range(len(self.species_stochmatrix)):    # Set species quantities
              setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s])    
      else:     
          for s in range(len(self.species_stochmatrix)):    # Set species quantities
              setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s])    
      self.rateFunc(self.req_eval_code,self.sim_a_mu)       # Calc. Propensities
      if self.sim_a_mu.min() < 0:
          print "Error: Negative propensities are found"
      else: self.sim_a_mu = abs(self.sim_a_mu)
      
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
      self.data_stochsim.setSpecies(sim_dat[:,1:],all_species)           # no 'firing' column
      if self.IsTrackPropensities: 
          self.data_stochsim.setPropensitiesLabels(self.rate_names)
          self.data_stochsim.setPropensities(self.propensities_output)  

################### Useful functions #########################

def MinPositiveValue(List):
    """
    This function determines the minimum positive value

    Input:
     - *List*
    Output: 
     - *minimum positive value*
    """
    positives = []
    for value in List:
        if value > 0:
            positives.append(value)
    return min(positives)

def GetSample(probs):  
    """
    This function extracts a sample from a list of probabilities.
    The 'extraction chance' is identical to the probability of the sample.

    Input:
     - *probs*: (list)
    Output: 
     - *sample*
     - *sample index*
    """
    output = []
    MinimumProb = float(MinPositiveValue(probs))
    for prob in probs:
        for i in range(0,int(100*prob/MinimumProb)):
            output.append(probs.index(prob))
    random.sample(output,1)
    index = random.sample(output,1)[0]
    return (probs[index],index)

def DetermineOrderHOR(rate_vector,reactants): 
  """
  Determines once the order of each reaction and the highest order of reaction (HOR) for each species.

  Input:
   - *Rate_vector*: (list)
   - *Reactants*: (nested list)
  Output:
   - *orders*
   - *HORs*
   - *HO_info*
  """
  orders   = []
  hors     = []
  HO_info  = []
  hor_info = ''
  j = 0   
  for r in rate_vector:    
    reaction = r['RateEq']
    vars_names = reactants[j]    
    raw_reaction = reaction[:]    
    n = -1
    HOR = 0
    for var in vars_names:  			                     # slow...
        if re.search(var+ '[^\d]',reaction) or re.search(var+'$',reaction): # 29/7/2010 Use REGEX
            count = len(re.findall(var+ '[^\d]',reaction)) + len(re.findall(var+ '$',reaction))        
            if "pow" in reaction:                            # Example: k1*S1**2 as input --> k1*pow(S1,2)
                m = re.search(var+'\,\d\)',reaction)         # pow(S1,2) --> 2
                try: count = int(m.group(0)[len(var)+1:-1])  # count = 2 (for this example)
                except: pass
            if count > HOR:
                HOR = count        
                hor_info = var
            n+=1     
    j+=1
    order = n+HOR
    if hor_info == '':  			                         # zero-th order reaction
        order = 0
    HO_info.append(hor_info)
    orders.append(order)
    hors.append(HOR)  
  return (orders,hors,HO_info)
