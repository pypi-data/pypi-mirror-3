#! /usr/bin/env python
"""
Analysis
========

This module provides functions for Stochastic Simulation Algorithms Analysis (SSAA). Implemented SSAs import this module to perform their analysis. It plots time simulations, distributions and waiting times.

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 15, 2011
"""

try: import matplotlib.pyplot as plt  
except: print "The MatPlotLib module is not available, so it is impossible to create plots"

try: import numpy as np
except:
    print "Error: The NumPy module is not available. "
    sys.exit()

from math import ceil,log,sqrt

def BuildDistributions(data_stochsim):
    """
    Builds distributions for each molecule/species/metabolite.

    Input:
     - *data_stochsim*: data object that stores all simulation data
    Output: 
      - *data_stochsim*: distributions are attached to the data object

    The dictionairy keys refer to a molecular count and the values to the probability for that particular count. 

    Note: Use Distributions from the class CreatePlots to plot these distributions.  
    """
    timepoints = len(data_stochsim.time)
    number_of_species = len(data_stochsim.species_labels)

    i = 0
    while i<(number_of_species):  
        Dict = {}
        temp = []
        t = 0
        j = 1
        while j<(timepoints-1):  
            t1 = data_stochsim.getSpecies()[j][0]
            t2 = data_stochsim.getSpecies()[j+1][0]  
            dt = t2-t1
            t+=dt
            x = data_stochsim.getSpecies()[j][i+1] # species amount
            if x not in Dict:
                Dict[x] = 0
            if x in Dict:
                Dict[x] += dt                      # Calculate N*dt for each N
            j+=1    
    
        amounts = Dict.keys()                      # species amounts    
        amounts.sort()
        mean = 0
        mean_sqrt = 0    
        for amount in amounts:      
            old = Dict[amount]      
            dt_T = float(old)/t                   # Calculate x*dt/T for each x
            temp.append((amount,dt_T))	
            mean += amount*dt_T                   # Calculate <x> = Sum[N*dt/T]
            mean_sqrt += amount*amount*dt_T       # Calculate <x^2> = Sum[N^2 * dt/T]
      
        species_name = data_stochsim.species_labels[i]
        data_stochsim.distributions.append(temp)
  
        var = mean_sqrt - mean*mean               # Calculate var = <x^2> - <x>^2 
        sd = sqrt(var)
        data_stochsim.means[species_name] = mean
        data_stochsim.standard_deviations[species_name]  = sd
        i+=1    
    return (data_stochsim)

def Count(data_,edges_):
    """
    Input:
     - *data_*
     - *edges_*
    """
    output = np.zeros(len(edges_))  
    for value in data_:    
        for i in range(0,len(edges_)-1):
            if value >= edges_[i] and value < edges_[i+1]:
                output[i]+=1  
    return np.array(output)

def LogBin(data,factor):  
    """
    Function that creates log bins  

    Input: 
     - *data*: list
     - *factor* : float (determines the width of the bins)
    Output: 
     - *x*: x-values (list)
     - *y*: y-values (list)
     - *nbins*: number of bins (integer)
    """
    xmin = float(min(data))    
    nbins = int(ceil(log(max(data)/xmin)/log(factor)))  
    edges = np.zeros(nbins)
    edges[0] = xmin
  
    for i in range(1,nbins):
        edges[i] = edges[i-1]*factor
  
    x  = edges[0:(nbins-1)]+np.diff(edges)/2  
    dp = Count(data,edges)
    ry = np.array(dp[0:(nbins-1)])  
    dedges = np.array(np.diff(edges))  
    y = ry/(sum(ry)*dedges) 
    return(x,y,nbins)

def ObtainWaitingtimes(data_stochsim,num_reactions):
    """    
    This function extracts the waiting times for each reaction of the model from the used SSA output.

    Input:
     - *data_stochsim*: data object that stores all simulation data
     - *num_reactions*: number of reactions (integer)
    output:
     - *waiting times*: nested list
  
    Note: It is impossible to use this function in combination with the Tau-leaping method, because the results are not exact! (Therefore, it does not work)
    """
    time = data_stochsim.time.flatten()
    fired_reactions = data_stochsim.fired_reactions             # Reactions that fired at some time point

    waiting_times  = {}
    last_fire_time = {}
    for reaction in fired_reactions:
        waiting_times[reaction] = []
    for (current_time,reaction) in zip(time,fired_reactions):
        for i in range(1,num_reactions+1): 
            if reaction == i:        
                try:       
                    last_fire_time[reaction]                    # A previous firing time is necessary
                    waiting_times[reaction].append(current_time-last_fire_time[reaction]) # Add interarrival time
                    last_fire_time[reaction] = current_time     # Update last firing time
                except:
                    last_fire_time[reaction] = current_time     # Initial firing time
    return waiting_times

def ObtainInterpolationResults(interpolated_output,points):  
    """
    Gets the interpolated output after interpolation

    Input: 
     - *interpolated data*: nested list
     - *points*: integer time points of interpolation
    """
    means = []
    sds = []
    smallest_line = 1000e1000   
    for line in interpolated_output[0]:    
        len_line = len(line)
        if len_line < smallest_line:
            smallest_line = len_line
    i=0  
    for species in interpolated_output:    
        j=0
        for line in species:
            interpolated_output[i][j] = line[0:smallest_line]
            j+=1
        i+=1
    interpolated_output = np.array(interpolated_output)
    for interpolated_species_output in interpolated_output:
        means.append(np.mean(interpolated_species_output,0))
        sds.append(np.std(interpolated_species_output,0))
    
    x_axis =(points[0:smallest_line]) 
    return means,sds,x_axis
   
class DoPlotting():
  """
  This class initiates the plotting options.

  Input: 
   - *species vector*: [S1,S2 .. Sn]
   - *rate names*:  [R1, R2 .. Rm] 
  """
  def __init__(self,species_labels,rate_labels):
      self.species_labels = species_labels
      self.rate_labels = rate_labels
      self.number_of_rates = len(rate_labels)
      self.plotnum  = 1
      # html hex color codes 
      self.colors = ['#0000FF','#00CC00','#FF0033','#FF00CC','#6600FF','#FFFF00','#000000','#CCCCCC','#00CCFF','#99CC33','#FF6666','#FF99CC','#CC6600','#003300','#CCFFFF','#9900FF','#CC6633']
    
  def ResetPlotnum(self):
      """ Reset figure numbers if trajectories > 1 """
      self.plotnum = 1 
  
  def TimeSimulation(self,data,species2plot,traj_index,linestyle,title):
      """
      Time simulation plot

      Input:
       - *data_stochsim*
       - *species2plot*
       - *traj_index*
       - *linestyle*
       - *title*
      """
      plt.figure(self.plotnum)
      time = data[:,0]

      species2plot_indices = []
      for species in species2plot: species2plot_indices.append(self.species_labels.index(species))

      if len(species2plot) == 1: j = traj_index
      else: j=0

      for i in species2plot_indices:
          y = data[:,i+1]
          plt.plot(time,y,ls = linestyle,color = self.colors[j]) 
          j+=1
          if j == len(self.colors): j=0 	# Reset to first color                 

      plt.legend(species2plot)      
      plt.title(title)
      plt.xlabel('Time') 
      plt.ylabel('Species Amounts')   
      self.plotnum+=1 
 
  def Distributions(self,distributions,species2plot,traj_index,linestyle,title):
      """
      Plots the distributions of the simulated metabolites/molecules.

      Input:
       - *distributions*
       - *species2plot*
       - *traj_index*
       - *linestyle*
       - *title*

      Makes use of the output of BuildDistributions()
      """ 
      plt.figure(self.plotnum)
      species2plot_indices = []
      for species in species2plot: species2plot_indices.append(self.species_labels.index(species))

      if len(species2plot) == 1: j = traj_index
      else: j=0

      for i in species2plot_indices:
          dist = zip(*distributions[i])			# Transpose List
          conc = np.array(dist[0])+0.5      
          prob = dist[1]      
          plt.step(conc,prob,ls = linestyle,color = self.colors[j])	# Plot
          j+=1
          if j == len(self.colors):
            j=0

      plt.legend(species2plot)
      plt.title(title)
      plt.xlabel('Number of Molecules')
      plt.ylabel('Probability')
      self.plotnum+=1

  def Propensities(self,data_stochsim,rates2plot,traj_index,linestyle,title):
      """
      Tracks the propensities through time

      Input: 
       - *data_stochsim*
       - *rates2plot*
       - *traj_index*
       - *linestyle*
       - *title*
      """
      plt.figure(self.plotnum) 
      time = data_stochsim.getTime()  

      rates2plot_indices = []
      for rates in rates2plot: rates2plot_indices.append(self.rate_labels.index(rates))
   
      if len(rates2plot) == 1: j = traj_index
      else: j=0

      for i in rates2plot_indices:    
          y = data_stochsim.propensities[:,i]    
          plt.plot(time,y,ls = linestyle,color = self.colors[j]) 
          j+=1
          if j == len(self.colors):		# reset to first color
              j=0
      
      plt.legend(rates2plot)
      plt.title(title)
      plt.xlabel('Time') 
      plt.ylabel('Propensities')   
      self.plotnum+=1

  def Waitingtimes(self,waiting_times,rates2plot,traj_index,linestyle,title):
      """
      Plots the waiting times for each reaction in the model. Makes use of ObtainWaitingtimes to derive the waiting times out of the SSA output.
 
      Input: 
       - *waiting times*
       - *rates2plot*
       - *traj_index*
       - *linestyle*
       - *title*
      """
      plt.figure(self.plotnum)    
      rates2plot_indices = []
      for rates in rates2plot: rates2plot_indices.append(self.rate_labels.index(rates))
    
      if len(rates2plot) == 1: j = traj_index
      else: j=0  

      legend_names = []
      for i in rates2plot_indices:
          waiting_time = waiting_times[i+1]        
          if len(waiting_time) > 1:					# At least 2 waiting times are necessary per reaction
              (x,y,nbins) = LogBin(waiting_time,1.5) 	# Create logarithmic bins
              plt.loglog(x,y,ls = linestyle,color = self.colors[j])
              legend_names.append(self.rate_labels[i])  
              j+=1 
              if j == len(self.colors): j=0

      plt.title(title)
      plt.xlabel('Interarrival time t')
      plt.ylabel('Frequency')
      plt.legend(legend_names)    
      self.plotnum+=1  
         
  def AverageTimeSimulation(self,means_set,sds_set,time,linestyle,title):
      """ Plots the interpolated time simulation results. Makes use of the ObtainInterpolationResults function, which determines the input for this function out of the SSA output.

      Input:
       - *means_set*: nested list
       - *sds_set*: nested list
       - *time*: list
       - *linestyle*: linestyle (string)
       - *title*
      """
      plt.figure(self.plotnum)    
      j=0
      for (means,sds) in zip(means_set,sds_set):
          plt.errorbar(time,means,yerr = sds,color = self.colors[j],ls = linestyle) # plot with y-axis error bars
          j+=1
          if j == len(self.colors): 
              j=0
      plt.title(title)
      plt.xlabel('Time')
      plt.ylabel('Species Amounts')
      plt.legend(self.species_labels)
