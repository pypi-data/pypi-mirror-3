#! /usr/bin/env python
"""
Optimized Tau-Leaping
=====================

This program performes Optimized Expliced Tau-leaping algorithm, which is an approximate version of the exact Stochastic Simulation Algorithm (SSA). Here, an efficient step size selection procedure for the tau-leaping method [1] is used.

[1] Cao. Y, Gillespie D., Petzold L. (2006), "Efficient step size selection for the tau-leaping method", J.Chem. Phys. 28:124-135

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 15, 2011
"""
############################## IMPORTS ###################################

from stochpy import model_dir
import sys,copy,re,time,os,cPickle,random

try: import numpy as np
except: 
    print "Make sure that the module NumPy is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

try:from PyscesMiniModel import PySCeS_Connector
except: from stochpy.PyscesMiniModel import PySCeS_Connector	# installed

try:from PyscesMiniModel import IntegrationStochasticDataObj
except: from stochpy.PyscesMiniModel import IntegrationStochasticDataObj	# installed

########################### END IMPORTS ##################################

class OTL(PySCeS_Connector):
  """  
  Input:
   - *File*  = filename.psc
   - *dir*   = /home/user/Stochpy/pscmodels/filename.psc
   - *Outputdir* = /home/user/Stochpy/ 
  """
  def __init__(self,File,dir,OutputDir,TempDir):
    self.OutputDir = OutputDir
    self.TempDir = TempDir
    self.IsExit = False
    self.Parse(File,dir)
    if self.IsExit: sys.exit()  

  def Parse(self,File,dir):
    """
    Parses the PySCeS MDL input file, where the model is desribed

    Input:
     - *File*  = filename.psc
     - *dir*   = /home/.../Stochpy/pscmodels/filename.psc
    """
    self.ModelFile = File
    self.ModelDir = dir
    try:
      parse = PySCeS_Connector(self.ModelFile,self.ModelDir)	# Parse model      
      if parse.IsConverted:
        self.ModelFile += '.psc'
        self.ModelDir = model_dir

      self.N 		= parse.Mod.N
      self.Xinit 	= parse.X
      self.reactants 	= parse.reactants
      self.species_ids  = parse.species
      self.reagents 	= parse.reagents
      self.rate_names   = parse.reactions
      self.propensities = parse.propensities
      self.species_names= parse.species_names
      self.rate_eqs     = parse.rate_eqs
      self.DetOptions = 1
      self.IsFirst = True
    except:
      self.IsExit = True
      print "Error: It is impossible to parse the input file:", self.ModelFile, "from directory" , self.ModelDir
    
  def Execute(self,Trajectories,Endtime,Timesteps,TrackPropensities):
    """
    Generates T trajectories of the markov jump process.

    Input:
     - *Number of trajectories*
     - *Boolean for time or number of time steps simulation*
     - *Number of time steps / endtime*
    """    
    self.species_pos  = {}
    i=0
    for species in self.species_ids:
        self.species_pos[species] = i                   # Determine once for each species the position in the X-matrix
        i+=1
    self.Dump = [] 
    self.M = len(self.propensities)                     # Number of reactions
    self.a_mu = np.zeros(self.M)
    self.r = np.zeros((self.M,1))	                    # Initialize once a reaction vector
    self.epsilon = 0.03
    self.Nc = 10
    self.g = np.zeros(len(self.Xinit))                  # Initialize g vector 
    self.num_species = len(self.Xinit)    
    self.mu  = np.zeros(self.num_species)               # Init mu  (32.a)
    self.var = np.zeros(self.num_species)               # Init var (32.b)
    self.state_change_vector = np.transpose(self.N)
    t1 = time.time()
    self.X = self.Xinit.copy()
    self.Trajectories = Trajectories
    self.Endtime = Endtime
    self.Timesteps = Timesteps
    self.initOTLstep = 1
    self.IsTrackPropensities = TrackPropensities

    traj = 1
    if self.Trajectories == 1: print "Info: 1 trajectory is generated"
    else:
        file = open(self.OutputDir +'/ssa_sim.log','w')
        file.write("Trajectory\tNumber of time steps\tEnd time\tPercentage of OTL steps\n")
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

      self.t = 0
      IsNegative   = False
      tauleapsteps = 0
      self.Initial_Conditions()
      (orders,hors,HO_info) = DetermineOrderHOR(self.rate_eqs,self.reactants)
      timestep = 0
      while self.t < self.Endtime and timestep < self.Timesteps: 
        if not IsNegative:				        # If there are no negative conc. after a Tau-leap step
          self.CriticalReactions()   
          self.Propensities()
          if self.IsTrackPropensities:
              self.a_ravel = list(self.a_mu.ravel())
              self.a_ravel.insert(0,self.t)
              self.propensities_output.append(self.a_ravel)
          self.GetG(orders,hors,HO_info)
          self.a_0 = self.a_mu.sum()           
          if self.a_0 <= 0:  break 	
          self.GetMuVar(self.a_mu)
          self.GetTauPrime()  

        ##################### start Possible Feedback loop ##################
        self.DetermineMethod()    
        ##### Optimized Tau-Leaping step ##### 

        if self.IsOTL: 
          self.GetA0c()
          self.GetTauPrimePrime()
          self.GetK()         
          self.Execute_K_Reactions()  
          if not self.IsNegative:
            if self.IsTrackPropensities:
                self.a_ravel = list(self.a_mu.ravel())
                self.a_ravel.insert(0,self.t)
                self.propensities_output.append(self.a_ravel)

            self.t += self.tau
            IsNegative = False
            temp = [self.t]
            for conc in self.X.ravel(): temp.append(conc)        
            #for IsReaction in self.K.ravel(): temp.append(IsReaction)    # 15 September 2011
            tauleapsteps +=1  
            ### End output Generation   ###  

          elif self.IsNegative:    			       # start feedback loop         
              IsNegative = True
              self.tau_prime = self.tau_prime/2.0   
        elif self.IsExact:    ###### Direct SSA step #######
          m = 0         
          while m < 100 and self.t < self.Endtime and timestep < self.Timesteps:
            self.Propensities()
            if self.IsTrackPropensities:
                self.a_ravel = list(self.a_mu.ravel())
                self.a_ravel.insert(0,self.t)
                self.propensities_output.append(self.a_ravel)

            self.a_0 = self.a_mu.sum()  
            if self.a_0 == 0: break
            self.RunExactSSA()
 
            ### Start output Generation ###
            temp = [self.t]
            for conc in self.X.ravel(): temp.append(conc)  
            #for IsReaction in self.r.flatten(): temp.append(IsReaction)
            self.r[self.n] = 0					        # Reset  
            ###  End output Generation  ###
            if m < 99:
                self.output.append(temp)
                timestep +=1
            m+=1
        #################### End possible feedback loop #################
        timestep +=1
        if not IsNegative: self.output.append(temp)

      self.X = self.Xinit.copy()     			        # Reset X for next trajectory calc.
      ####################################### 
      sim_dat = np.array(self.output,'d')
      self.data_stochsim = IntegrationStochasticDataObj()
      self.data_stochsim.trajectory = traj
      self.data_stochsim.setDist()
      self.data_stochsim.setTime(sim_dat[:,0])
      self.data_stochsim.setSpecies(sim_dat[:,1:], self.species_names)
      #self.data_stochsim.setFiredReactions(sim_dat[:,-1][1:])
      if self.IsTrackPropensities: 
          self.data_stochsim.setPropensitiesLabels(self.rate_names)
          self.data_stochsim.setPropensities(self.propensities_output)
      self.data_stochsim.setSimulationInfo(timestep,self.t)
      ######################################

      if self.Trajectories == 1:
          print "Number of time steps",timestep," End time",self.t
          print "Percentage OTL steps",tauleapsteps/float(timestep),
          print "Number of OTL timesteps:",tauleapsteps     
      elif self.Trajectories > 1:
          file.write(str(traj)+"\t"+ str(timestep) +"\t" + str(self.t)+"\n")
          name = self.TempDir+'/'+self.ModelFile+str(traj)+'.dat'
          cPickle.dump(self.data_stochsim,file = open(name,'w')) 	# Dump trajectory output
          self.Dump.append(name)      
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
      self.r2  = self.randoms[self.count]                  # Draw random number 2 [0-1]    
      self.tau = self.randoms_log[self.count]/self.a_0     # reaction time generation
      self.t   = self.t + self.tau                         # Time update
      self.count+=1

  def ReactionSelection(self):    
      """ Function which selects a reaction that will fire once """
      sum_of_as = 0.0
      self.n = -1
      criteria =  self.r2*self.a_0
      while sum_of_as < criteria:                          # Use r2 to determine which reaction will occur
          self.n += 1                                      # Index
          sum_of_as = sum_of_as + self.a_mu[self.n]     
      self.r[self.n] = [1]                                 # Boolean Vector

  def ReactionExecution(self):
      """ Function that executes the selected reaction that will fire once """
      self.X += np.dot(self.N,self.r)                      # Matrix multiplication

  def CriticalReactions(self):
      """ Determines the critical reactions (as a boolean vector) """
      if self.initOTLstep:                                 # Do this only once
          self.initOTLstep = 0
          self.N__ = copy.copy(self.N)
          self.N__ = np.transpose(self.N__) 
          self.N__[self.N__>=0]= np.nan      
    
      self.critical_reactions = []
      x = self.X.ravel()
      output = x/abs(self.N__)
      minima = np.nanmin(output,axis=1)

      for reaction in minima:
          if reaction < self.Nc:
              self.critical_reactions.append(1)
          else:
              self.critical_reactions.append(0)

  # SLOW 
  def GetG(self,orders,hors,hor_info):        
    """
    Determine the G vector

    Input:
     - *orders*
     - *hors*: highest order of reaction for each species
     - *hor_info*
    """ 
    if self.DetOptions:
      self.options = [0,0,0]
      self.DetOptions = 0     
      i=0
      for species in self.species_ids:      
        j= 0
        for reactants in self.reactants:        
          if species in reactants:
            if orders[j] == 1 and self.g[i] == 0:
              self.options[i] = 1
            elif orders[j] == 2:
              if hors[j] == 2 and self.g[i]<2:
                self.options[i] = 2
              elif hors[j] == 1 and self.g[i]<2:
                self.g[i] = 2  # 3
                self.options[i] = 3  
            elif orders[j] == 3:
              if hors[j] == 1:
                self.options[i] = 4
              elif hors[j] == 2:
                if species == hor_info[j]:        
                  self.options[i] = 5
                else:
                  self.options[i] = 4
              else:
                self.options[i] = 6
          j+=1 
        i+=1
    
    self.g = np.ones(len(self.Xinit)) 		# bug fixed 12/11/10
    i=0
    for option in self.options:      
      if option == 1:
        self.g[i] = 1
      elif option == 2:
        self.g[i] = 2 + 1.0/(self.X[i]-1)
      elif option == 3:
        self.g[i] = 2
      elif option == 4:
        self.g[i] = 3
      elif option == 5:
        try:
          self.g[i] = 3 + 1.5/(self.X[i]-1)
        except:
          self.g[i] = 3
      elif option == 6:
        try:
          self.g[i] = 3+ 1.0/(self.X[i]-1) + 2.0/(self.X[i]-2)
        except:
          self.g[i] = 3
      i+=1    

  def GetMuVar(self,a_mu):
      """
      Calculate the estimaters of mu and var for each species (i)
    
      Input: 
       - *a(mu)*: list
      """
      self.a_mu = a_mu
      i=0
      for v_i in self.N:
          self.mu[i] = np.dot(v_i,a_mu)	
          self.var[i]= np.dot(v_i*v_i,a_mu)
          i+=1

  def GetTauPrime(self):
      """ Calculate tau' """
      part = np.divide(self.X.ravel(),self.g)*self.epsilon # eps*x[i]/g[i] for all i
      num  = np.array([part,np.ones(len(part))])         # eps*x[i]/g[i] for all i , 1 for all i
      numerator = num.max(axis=0)                        # max(eps*x[i]/g[i],1) for all i
      abs_mu = np.abs(self.mu)                           # abs(mu) for all i

      bound1 = np.divide(numerator,abs_mu)               # max(eps*x[i]/g[i],1) / abs(mu[i]) for all i
      numerator_square = np.square(numerator)    	
      bound2 = np.divide(numerator_square,self.var)      # max(eps*x[i]/g[i],1)^2 / abs(mu[i]) for all i
      tau_primes = np.array([bound1,bound2])			
      try: self.tau_prime = np.min(tau_primes[~np.isnan(tau_primes)])# min (bound1,bound2)
      except: self.tau_prime = 10**6
      
  def DetermineMethod(self):
      """ Determines for each time step what to perform: exact of approximate SSA """         
      criteria = 10.0/self.a_0                           # Based on literature [2] (Cao 2006)
      if self.tau_prime > criteria and self.tau_prime != 10**6:
          self.IsExact = False
          self.IsOTL = True
      else:
          self.IsExact = True
          self.IsOTL = False

  def GetA0c(self):
      """ Calculate the total propensities for all critical reactions """
      self.a_0_c = np.dot(self.critical_reactions,self.a_mu)
  
  def GetTauPrimePrime(self):
      """ Calculate Tau'' """
      if self.count == 1000:                             # Re-generate random numbers
          randoms = np.random.random(1000)  
          self.randoms_log = np.log(randoms)*-1         
          self.count = 0
      
      self.GetA0c()  
      if self.a_0_c == 0:					             # a_0_c = 0
          self.tau_prime_prime = 10**6
      elif self.a_0_c != 0:
          self.tau_prime_prime = self.randoms_log[self.count]/self.a_0_c
          self.count+=1    
    

  def GetK(self):        
    """
    Determines the K-vector, which describes the number of firing reactions for each reaction.
    """
    self.K = np.zeros((self.M,1))
    if self.tau_prime < self.tau_prime_prime:           # tau' < tau''
      self.tau = self.tau_prime
      j=0 
      for IsCritical in self.critical_reactions:        
        if not IsCritical:
            a_j = self.a_mu[j]
            Lambda = self.tau * a_j       
            k_j = np.random.poisson(Lambda)           
            self.K[j] = [k_j]        
        j+=1    
      
    else:
      self.tau = self.tau_prime_prime                   # tau' > tau''
      j = 0
      probs = []
      IsCrit = False
      for IsCritical in self.critical_reactions:         
          a_j = self.a_mu[j]
          if IsCritical:
              IsCrit = True
              p = float(a_j)/self.a_0          
              probs.insert(j,p)
              if p == 1:                                # Only one critical reaction
                  self.K[j] = [1]
          elif not IsCritical:
              probs.insert(j,0.0)
              Lambda = self.tau * a_j
              k_j = np.random.poisson(Lambda)
              self.K[j] = [k_j]
          j+=1
      if IsCrit:                                        # Bug fixed jan 15 2011
          (prob,index) = GetSample(probs)               # Select one crit.reaction that fires once
          self.K[index] = [1]

  def Execute_K_Reactions(self):
      """ Perform the determined K reactions """
      self.IsNegative = False  
      x_temp  = copy.copy(self.X) 
      x_temp += np.dot(self.N,self.K)    
      MinConc = x_temp.min()
      if MinConc < 0:                                   # Check for negatives after the K reactions 
          self.tau = self.tau/2.0
          self.IsNegative = True
      else: self.X = x_temp                             # Confirm the done K reactions
          
  def Initial_Conditions(self):                
      """ This function initiates the output format with the initial concentrations """
      self.output = []    
      if self.IsTrackPropensities: self.propensities_output = []

      output_init = [self.t]      
      for init in self.X:                               # Output at t = 0 
          if init < 0:
              print "Error: There are initial negative concentrations!"
              sys.exit()
          output_init.append(int(init))
      #for i in range(len(self.rate_names)): output_init.append(np.NAN)
      self.output.append(output_init)

  def rateFunc(self,rate_eval_code,r_vec):
      """
      Calculate propensities from the compiled rate equations
    
      Input:
       - *compiled rate eqs*
       - *r_vec*: output for the calculated propensities
      """
      exec(rate_eval_code)       

  def Propensities(self):
      """
      Determines the propensities to fire for each reaction at the current time point. At t=0, all the rate equations are compiled. 
      """   
      if self.t == 0:		                            # Compile rate-eqs
          code_str = """"""      
          self.len = len(self.propensities)			    # Number of rate_eqs
          self.a_mu = np.zeros([self.len])			    # Initialize a(mu)
          for i in range(self.len):
              code_str+='r_vec['+str(i)+']='+self.propensities[i]+'\n'
          ##print code_str   
          self.req_eval_code = compile(code_str,"RateEqEvaluationCode","exec")
          for s in range(len(self.species_ids)):        # Set species quantities
              setattr(self,self.species_ids[s],self.X[s][0])    
      else:     
          for s in range(len(self.species_ids)):        # Set species quantities
              setattr(self,self.species_ids[s],self.X[s][0])    
      self.rateFunc(self.req_eval_code,self.a_mu)       # Calc. Propensities

################### Usefull functions #########################

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
     - *probs*: list
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
     - *rate_vector*: (list)
     - *reactants: nested list
    Output:
     - *orders*
     - *HORs*
     - *HOR-info*
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
        for var in vars_names:  			                 # slow ...
            if re.search(var+ '[^\d]',reaction) or re.search(var+'$',reaction): # 29/7/10 Use REGEX
              count = len(re.findall(var+ '[^\d]',reaction)) + len(re.findall(var+ '$',reaction))        
              if "pow" in reaction:                          # Example: k1*S1**2 as input --> k1*pow(S1,2)
                  m = re.search(var+'\,\d\)',reaction)       # pow(S1,2) --> 2
                  try: count = int(m.group(0)[len(var)+1:-1])# count = 2 (for this example)
                  except: pass
              if count > HOR:          
                  HOR = count        
                  hor_info = var[5:]
              n+=1     
        j+=1
        order = n+HOR
        if hor_info == '': order = 0                         # zero-th order reaction        
        HO_info.append(hor_info)
        orders.append(order)
        hors.append(HOR)  
    return (orders,hors,HO_info)
