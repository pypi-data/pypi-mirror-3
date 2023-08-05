"""
StochPy test/example script

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: 23 October, 2011
"""
import stochpy
mod = stochpy.SSA()
# 1: Basic Simulation with the Direct method
mod.TrackPropensities()      # Track Propensities
mod.DoStochSim()
mod.data_stochsim.simulation_endtime
mod.data_stochsim.simulation_timesteps
mod.GetWaitingtimes()
mod.GetMeanWaitingtimes()
mod.PrintMeanWaitingtimes()
# 2: Do some Plotting
mod.PlotTimeSim()
mod.PlotWaitingtimes()
mod.PlotPropensities()
# 3: Write data to a text file
mod.Write2File('TimeSim')
mod.Write2File('Waitingtimes')
mod.Write2File('Propensities')
# 4: Show the means from the data of 3-th trajectory
mod.DoStochSim(trajectories=3) # multiple trajectories
mod.data_stochsim.simulation_trajectory
mod.ShowMeans()
mod.ShowStandardDeviations()
# 5: Switch to data from trajectory 1 and show the means of each species
mod.GetTrajectoryData(1)
mod.ShowMeans()
mod.ShowStandardDeviations()
# 6: Do one long simulation
mod.DoStochSim(trajectories=1,end=1000000,mode='steps')
mod.ShowMeans()              # Lambda
mod.ShowStandardDeviations() # sqrt(Lambda)
# 7: Plot the PDF for different bin sizes
mod.PlotDistributions()
mod.PlotDistributions(bin_size=5)  # larger bin size
mod.PlotDistributions(bin_size=10) # again a larger bin size
mod.Write2File('Distributions')

# 8: Usage of the Reload Function: Ksyn = 20, kdeg = 0.2
mod.Reload()
mod.DoStochSim()
mod.ShowMeans()   # should be ~Ksyn/Kdeg

# 9: Use another model to show the Interpolation features
mod.Model('dsmts-001-01.xml.psc')
mod.DoStochSim(trajectories=1000,end=50,mode='time') 
mod.GetInterpolatedData()
mod.PrintInterpolatedData()  
mod.PlotInterpolatedData()  
mod.Write2File('Interpol') 

# 9: Test each method for different models: 
mod.Model('autoreg')
mod.DoStochSim(trajectories=1,end=1000,mode='steps')
mod.Method('NextReactionMethod')
mod.DoStochSim(trajectories=1,end=1000,mode='steps')
mod.data_stochsim.species
mod.PlotWaitingtimes()
mod.Method('FirstReactionMethod')
mod.DoStochSim(trajectories=1,end=1000,mode='steps')
mod.Method('TauLeaping')
mod.DoStochSim(trajectories=1,end=1000,mode='steps')

mod.Model('DecayingDimerizing')
mod.DoStochSim(method = 'Direct',trajectories=1,end=50,mode='time')
mod.DoStochSim(method = 'NextReactionMethod',trajectories=1,end=50,mode='time')
mod.DoStochSim(method = 'FirstReactionMethod',trajectories=1,end=50,mode='time')
mod.PlotWaitingtimes() 
mod.DoStochSim(method = 'TauLeaping',trajectories=1,end=50,mode='time',epsilon=0.03)  # Should outperform all other implementations
mod.PlotTimeSim()
mod.PlotWaitingtimes()   # Should give an error message



mod.Model('chain500')
mod.DoStochSim(method = 'Direct',trajectories=1,end=10000,mode='steps')
mod.DoStochSim(method = 'NextReactionMethod',trajectories=1,end=10000,mode='steps') # should outperform the direct method and all other implementations

# 10: Use the Next Reaction Method to test a model with an time event
mod.Model('dsmts-003-03.xml.psc')
mod.DoStochSim(method = 'NextReactionMethod',trajectories=1,end=10000,mode='steps')

mod.PlotDistributions(bin_size = 1)
mod.PlotDistributions(bin_size = 4)
mod.PlotDistributions(bin_size = 10)

mod.DoTestsuite()
mod.PlotInterpolatedData()

# 11: Use the First Reaction method to test a model with a concentration event 
mod.Model('dsmts-003-04.xml.psc')
mod.DoStochSim(method = 'FirstReactionMethod')
mod.DoTestsuite()
mod.PlotInterpolatedData()

# 12: Volume Models
mod.Model('dsmts-001-11.xml.psc')
mod.DoStochSim(method = 'Direct',trajectories=1000,end=50,mode ='time')
mod.PlotInterpolatedData()
