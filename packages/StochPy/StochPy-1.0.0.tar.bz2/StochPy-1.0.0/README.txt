StochPy Stochastic modeling in Python
====================================

Copyright (c) 2010-2011, Timo R. Maarleveld
All rights reserved.

StochPy is distributed under a BSD style licence.

Author information
------------------

Timo R. Maarleveld
VU University, Amsterdam, Netherlands

email: tmd200@users.sourceforge.net
web:   http://sourceforge.net/projects/stompy/

Documentation can be found in the user guide (see Documentation directory)

Installation
------------
The following software is required before installling StomPy:

- Python 2.x+
- NumPy 1.x+
- Matplotlib (optional)
- libsbml
- libxml2

Linux/MAC OS/Cygwin
~~~~~~~~~~~~~
as root  (sudo -s):
1) cd to directory StochPy-1.0.0
2) python setup install

Windows
~~~~~~~
Use the windows installer in directory: /StochPy-1.0.0/dist

Usage
-----
>>> import stompy
>>> help(stompy)
>>> mod = stompy.SSA()
>>> help(mod)
>>> mod.DoStochSim()               # Do a stochastic time simulation
>>> mod.PlotTimeSim()  
>>> mod.PlotDistributions()
>>> mod.PlotPropensities()
>>> mod.PlotWaitingtimes()
>>> mod.DoStochSim(trajectories = 10,method = 'Direct',end = 1000, mode = 'steps')
>>> mod.data_stochsim              # data object that stores the data of a simulation trajectory (See user guide)
>>> mod.data_stochsim.trajectory   # trajectory
>>> mod.GetTrajectoryData(3)       # Get data from the third trajectory
>>> mod.ShowMeans()                # shows the means of every species in the model for the selected trajectory (3)
>>> mod.ShowStandardDeviations()
>>> mod.GetInterpolatedData()
>>> mod.data_stochsim_interpolated # data object that stores the interpolated data
>>> mod.data_stochsim_interpolated.means # means for every time point
