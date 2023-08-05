"""
N-nucleosome model builder, which can be used as input for Stochastic Simulation Algorithms. 

This model builder has several features:
- neighbour interactions
- neighbour/noise ratio value
- neighbour interaction describtions (exp, kwadratic, gaussion, linear, uniform)
- initial modifications are randomly determined (02/08/10)
- enzyme-landing-zones (23/08/10)

By default, a three-nucleosome model, with 2 neighbours is builded.

Output is automatically printed in model.psc

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@few.vu.nl
Last Change: Augustus 25, 2010
"""
import sys,random,copy,os
from math import exp

try:
  sys.path.append(os.getcwd()+'/modules/')
  from dnorm import *
except:
  print "Make sure that the directory modules exist in the current working directory and that the module dnorm.py is in this directory."
  sys.exit()

class Build():
  """
  This class builds the reactions for a N-nucleosome model. 
  It uses the number of neighbours and the names of the parameters as input.  
  """
  def __init__(self,N=20,Neighbours=20,IsExp=0,IsGaus=0,IsKwad=0,IsLin=0,IsUni=1,Ratio = 5):
    self.N = N  				# Number of nucleosome in the N-nucleosome model    
    self.neighbours = Neighbours		# Number of neighbours
    self.IsExp      = IsExp
    self.IsGaussian = IsGaus
    self.IsKwad     = IsKwad
    self.IsLinear   = IsLin
    self.IsUniform  = IsUni
    self.ratio = Ratio				# neighbour/noise	
    self.num = 0				# Reaction number
    self.species = ['M','U','A']		# Modification types   
    self.conversions = {'M':{'M':'M','U':'M','A':'U'},'U':{'M':'M','U':'U','A':'A'},'A':{'M':'U','U':'A','A':'A'}}     
    self.filename = 'model.psc'
    self.EntireModel()				# N-nucleosome model

  def Initials(self):  
    """ 
    Build and print the initial concentrations of the nucleosome modifications.
    Each nucleosome starts with a certain modification (M, U or A), which is determined randomly.
    """
    file = open(self.filename,'a')    
    file.write('\n# InitVar\n')
    pos = [[1,0,0],[0,1,0],[0,0,1]]		# Possibilities (random)
    modifications = ['M','U','A']
    n = 1
    while n<=self.N:
      values = random.choice(pos)		# Choice random pos
      for modification,value in zip(modifications,values):        
        file.write(modification+str(n)+'='+str(value)+'\n')
      n+=1
    file.close()

  def Kvalues(self):
    """
    Builds to velocity-constants, k2 untill km. k1 represents the noisy conversion rate, which is user input and determines the ratio noisy/neighbours.
    It is possible to use five types of decay: exponential, gaussian, kwadratic,linear or uniform.
    input: number of neighbours, Booleans for type of decay (all integers)
    output: [(k2, 1), (k3,0.367) .., ..., (km,...)]  a list of tuples
    """
    self.K = []
    for i in range(0,self.neighbours):
      if self.IsExp:				# Exponential decay
        strength = exp(-i)
      elif self.IsGaussian:			# Gaussian
        distribution = normalized_dnorm(range(-self.neighbours,self.neighbours))    
        centre = int(0.5*len(distribution)+0.5)
        strength = distribution[centre-self.neighbours/2+i]  
      elif self.IsKwad:				# Kwadratic decay
        strength = (i+1)/float((i+1)**2)
      elif self.IsLinear:			# Linear decay
        strength = 1-(0.1*i)
      elif self.IsUniform:			# Uniform
        strength = 1 

      self.K.append(('k'+str(i+2),strength))

  def PrintParms(self):
    """ Print the parameters that are used in the model """     
    file = open(self.filename,'a')    
    file.write('\n# InitPar\n')    
    file.write('knoise = '+str(1.0)+'\n')
    for name in self.K:     
      file.write(name[0]+" = "+str(self.ratio*name[-1])+'\n')
    file.close()

  def PrintLastReaction(self):
    """ Print the last created reaction """
    file = open(self.filename,'a')
    file.write(self.reaction_num+'\n'+self.reaction+'\n'+self.rate+'\n')
    file.close()

  def Previous(self,i,neighbour):
    """
    Builds in a multi-nucleosome model the interactions between nucleosome[i] and the number of desired neighbours before nucleosome i. 
    Example: 
    -interaction between Nucl[i]--Nucl[i-1]
    -interaction between Nucl[i]--Nucl[i-2] etc.
    Ofcourse, Nucl[-1] does not exist, so it does not create interactions with non-existing nucleosomes      
    """
    if (i-neighbour) > 0:
      self.num +=1
      self.reaction_num = 'R'+ str(self.num)+':'
      self.reaction = '    '+self.species_1+str(i)+' + '+self.species_2+str(i-neighbour)+' > '+self.conversions[self.species_1][self.species_2]+str(i)+ ' + '+self.species_2+str(i-neighbour)
      self.rate = '    '+str(self.K[neighbour-1][0])+'*'+self.species_1+str(i)+'*'+self.species_2+str(i-neighbour)
      self.PrintLastReaction()

  def Next(self,i,neighbour):  
    """
    Builds in a multi-nucleosome model the interactions between nucleosome[i] and the number of desired neighbour after nucleosome i. 
    Example: 
    interaction between Nucl[i]--Nucl[i+1]
    interaction between Nucl[i]--Nucl[i+2] etc.
    Ofcourse, Nucl[N+5], where N is the total number of nucleosomes does not exist, so it does not create interactions with non-existing nucleosomes.
    """
    if (i+neighbour) <= self.N:         
      self.num +=1
      self.reaction_num = 'R'+ str(self.num)+':'
      self.reaction = '    '+self.species_1+str(i)+' + '+self.species_2+str(i+neighbour)+' > '+self.conversions[self.species_1][self.species_2]+str(i)+ ' + '+self.species_2+str(i+neighbour)
      self.rate = '    '+str(self.K[neighbour-1][0])+'*'+self.species_1+str(i)+'*'+self.species_2+str(i+neighbour)
      self.PrintLastReaction()

  def Noisy1(self,i): 
    """
    Builds the noisy conversions from M --> U and from A --> U for each nucleosome in the model.
    """
    self.reaction_num = 'R'+ str(self.num)+':'    
    self.reaction = '    '+self.species_1+str(i)+' > '+'U'+str(i)
    self.rate = '    knoise*'+self.species_1+str(i)
    self.PrintLastReaction()
  
  def Noisy2(self,i): 
    """
    Builds the noisy conversions from U--> A and U--> M for each nucleosome in the model.
    """     
    self.reaction_num = 'R'+ str(self.num)+':'
    self.reaction = '    '+'U'+str(i)+' > '+'M'+str(i)
    self.rate = '    knoise*'+'U'+str(i)            
    self.PrintLastReaction()
    self.num+=1
    self.reaction_num = 'R'+ str(self.num)+':'
    self.reaction = '    '+'U'+str(i)+' > '+'A'+str(i)     
    self.PrintLastReaction()

  def EntireModel(self):

    """
    Uses all the pre-defined functions in this class to build the entire model.
    """   
    file = open(self.filename,'w')

    self.Kvalues()
    for i in range(1,self.N+1):			
      IsNoisy = 1      
      for neighbour in range(1,self.neighbours+1):
        for self.species_1 in self.species:
          for self.species_2 in self.species: 
            if self.species_1 != self.species_2 and self.species_2 != 'U':    
              self.Previous(i,neighbour)	# n + n-1 
              self.Next(i,neighbour)		# n + n+1
          if IsNoisy:
            self.num+=1
            if self.species_1 == 'M' or self.species_1 =='A':
              self.Noisy1(i)			# Noisy n -->
            elif self.species_1 == 'U':
              self.Noisy2(i)			# Noisy n -->
        IsNoisy = 0
      if self.neighbours == 0:
        for self.species_1 in self.species: 
            self.num+=1
            if self.species_1 == 'M' or self.species_1 =='A':
              self.Noisy1(i)			# Noisy n -->
            elif self.species_1 == 'U':
              self.Noisy2(i)	
        
 
    self.PrintParms()
    self.Initials()
    self.num = 0    
    file.close()
    print "output is saved in 'model.psc' at the current working directory"

  def ChangeN(self,n):
    self.N = n    

if __name__ == "__main__":
  ##################### Main ###################
  n = 20					# Number of nucleosomes
  neighbours = 0				# Number of desired neighbours
  ratio = 1 					# Ratio neighbours/noise


  build = Build(N=n,Neighbours= neighbours,Ratio = ratio)

  # build.N = 5
  # build.EntireModel()
  # build.neighbours = 3
  # build.EntireModel() 
  

  ##############################################



  

