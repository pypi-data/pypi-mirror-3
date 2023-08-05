#! /usr/bin/env python
"""
Analysis
========

This module provides functions for Stochastic Simulation Algorithms Analysis (SSA). Implemented SSAs import this module to perform their analysis. It plots time simulations, distributions and waiting times.

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: October 21, 2011
"""

try: import matplotlib.pyplot as plt  
except: print "The MatPlotLib module is not available, so it is impossible to create plots"

try: import numpy as np
except:
    print "Error: The NumPy module is not available. "
    sys.exit()

import copy
from math import ceil,log,sqrt

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
    
def Binning(x,y,bin_size):
    """
    Binning of the PDF
    
    Input:
     - *x*: list of x-values
     - *y*: list of probabilities for each x[i]
     - *bin_size*: (integer)     
    """
    temp = []
    number_of_prob = len(x)
    if bin_size > number_of_prob or bin_size < 1:
        print "Bin Size is negative or too large and therefore re-setted to 1"
        bin_size = 1
    if bin_size > 1:
        dif = x[1]-x[0]
        if dif>1 and not bin_size%2:
            bin_size /= dif
        elif dif>1 and bin_size%2:
           n=0
           for i in range(x[0],x[-1]):
               if i not in x:
                    for j in range(dif-1):
                        x.insert(i-x[0],i)
                        y.insert(i-x[0],y[n])
                    n+=dif
        number_of_prob = len(x)
        max_index = y.index(max(y))                           # maximum prob index
        ### Get interval around the maximum value ###
        interval = range(max_index-(bin_size/2)+1,max_index+int(round(bin_size/2.0)+1)) # Get interval around maximum prob
        min_value = min(interval)
        while min_value < 0:
            interval.remove(min_value)
            interval.append(interval[-1]+1)
            min_value = min(interval)
        while interval[-1] > (number_of_prob-1):
            interval.pop()
            interval.insert(0,interval[0]-1)
        
        #############################################
        #if bin_size%2:
        temp.append([x[interval[-1]]+0.5,sum(y[interval[0]:interval[-1]+1])/float(bin_size)])  # +-0.5?
        #else: temp.append([x[interval[-1]],sum(y[interval[0]:interval[-1]+1])/float(bin_size)])
        individuals = []                                  # locations with bin_size = 1
        if interval[0]:
            nbins1 = (interval[0]-1)/bin_size             # nbins before interval around max prob
            start1 = interval[0]-1 - nbins1*bin_size      # start location of binning before interval
            if interval[0] == 1:
                individuals.append(0)
        else:                                             # interval around max goes until the first species amount
            temp.append([x[interval[0]]+0.5,sum(y[interval[0]:interval[-1]+1])/float(bin_size)])  # +-0.5?
            nbins1 = 0
            start1 = 0
            individuals.append(0)
        start2 =  interval[-1]                            # start location of binning after interval
        nbins2 = (number_of_prob-1 - start2)/bin_size     # nbins after interval around max prob
        for i in range(0,start1): individuals.append(i)
        for i in range(start2+1+(bin_size*nbins2),number_of_prob): individuals.append(i)
        x_ = np.array(x)
        y_ = np.array(y)
        # print individuals
        #print start1,nbins1,interval,start2,nbins2
        for i in range(nbins1):
            #if bin_size%2: temp.append([np.mean(x_[start1:start1+bin_size])+0.5,sum(y_[start1:start1+bin_size])/float(bin_size)])
            #else: temp.append([np.mean(x_[start1:start1+bin_size]),sum(y_[start1:start1+bin_size])/float(bin_size)])
            temp.append([x_[start1+bin_size]+0.5,sum(y_[start1:start1+bin_size])/float(bin_size)])
            #else: temp.append([x_[start1+bin_size],sum(y_[start1:start1+bin_size])/float(bin_size)]) 
            start1+=bin_size   
        for i in range(nbins2):
            #if bin_size%2: temp.append([np.mean(x[start2:start2+bin_size])+0.5,sum(y[start2:start2+bin_size])/float(bin_size)])    
            #else: temp.append([np.mean(x[start2:start2+bin_size]),sum(y[start2:start2+bin_size])/float(bin_size)])
            temp.append([x[start2+bin_size]+0.5,sum(y[start2:start2+bin_size])/float(bin_size)])
            #else: temp.append([x[start2+bin_size],sum(y[start2:start2+bin_size])/float(bin_size)])
            start2+=bin_size     
        for i in individuals:
            temp.append([x[i]+0.5,y[i]])
        data = np.array(sorted(temp))
        #print data
    else:
        data = np.array([x,y]).transpose()      
        data[:,0]+=0.5        
    return data        

def LogBin(data,factor):  
    """
    Function that creates log bins  

    Input: 
     - *data*: list
     - *factor* : determines the width of the bins (float)
    Output: 
     - *x*: x-values (list)
     - *y*: y-values (list)
     - *nbins*: (integer)
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
  
    Note: It is impossible to use this function in combination with the Tau-leaping method, because the Tau-Leaping results are not exact!
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
                    waiting_times[reaction].append(current_time-last_fire_time[reaction]) # Add inter-arrival time
                    last_fire_time[reaction] = current_time     # Update last firing time
                except:
                    last_fire_time[reaction] = current_time     # Initial firing time
    return waiting_times

def ObtainInterpolationResults(interpolated_output,points):  
    """
    Gets the interpolated output after interpolation

    Input: 
     - *interpolated_output*: (nested list)
     - *points*: list of integer time points of interpolation
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
   - *species_labels*: [S1,S2, ..., Sn]
   - *rate_labels*:  [R1, R2, ..., Rm] 
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
       - *data*: (array)
       - *species2plot* (list) 
       - *traj_index* (integer)
       - *linestyle* (string)
       - *title* (string)
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
 
  def Distributions(self,distributions,species2plot,traj_index,linestyle,title,bin_size):
      """
      Plots the distributions of the simulated metabolites/molecules.

      Input:
       - *distributions* (nested list)
       - *species2plot* (list)
       - *traj_index* (integer)
       - *linestyle* (string)
       - *title* (string)
      """ 
      plt.figure(self.plotnum)
      species2plot_indices = []
      for species in species2plot: species2plot_indices.append(self.species_labels.index(species))

      if len(species2plot) == 1: j = traj_index
      else: j=0

      for i in species2plot_indices: 
          x = list(copy.copy(distributions[i][0]))
          y = list(copy.copy(distributions[i][1]))
          data = Binning(x,y,bin_size)          
            
          plt.step(data[:,0],data[:,1],ls = linestyle,color = self.colors[j])	# Plot
          j+=1
          if j == len(self.colors):
            j=0

      plt.legend(species2plot)
      plt.title(title)
      plt.xlabel('Number of Molecules')
      plt.ylabel('Probability/Bin Size')
      self.plotnum+=1

  def Propensities(self,data_stochsim,rates2plot,traj_index,linestyle,title):
      """
      Tracks the propensities through time

      Input: 
       - *data_stochsim*: data object
       - *rates2plot* (list)
       - *traj_index* (integer)
       - *linestyle* (string)
       - *title* (string)
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
       - *waiting_times* (dict)
       - *rates2plot* (list)
       - *traj_index* (integer)
       - *linestyle* (string)
       - *title* (string)
      """
      plt.figure(self.plotnum)    
      rates2plot_indices = []
      for rates in rates2plot: rates2plot_indices.append(self.rate_labels.index(rates))
    
      if len(rates2plot) == 1: j = traj_index
      else: j=0  

      legend_names = []
      for i in rates2plot_indices:
        try:
          waiting_time = waiting_times[i+1] 
          if len(waiting_time) > 1:					    # At least 2 waiting times are necessary per reaction
              (x,y,nbins) = LogBin(waiting_time,1.5) 	# Create logarithmic bins
              plt.loglog(x,y,ls = linestyle,color = self.colors[j])
              legend_names.append(self.rate_labels[i])  
              j+=1 
              if j == len(self.colors): j=0
        except: pass

      plt.title(title)
      plt.xlabel('Interarrival time t')
      plt.ylabel('Frequency')
      plt.legend(legend_names)    
      self.plotnum+=1  
         
  def AverageTimeSimulation(self,means_set,sds_set,time,linestyle,title):
      """ Plots the interpolated time simulation results. Makes use of the ObtainInterpolationResults function, which determines the input for this function out of the SSA output.

      Input:
       - *means_set*: (nested list)
       - *sds_set*: (nested list)
       - *time*: (list)
       - *linestyle*: (string)
       - *title* (string)
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
