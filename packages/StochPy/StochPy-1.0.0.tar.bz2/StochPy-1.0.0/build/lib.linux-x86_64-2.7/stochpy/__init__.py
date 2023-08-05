#! /usr/bin/env python
"""
StochPy - Stochastic Modeling in Python (http://stompy.sourceforge.net)

Copyright (C) 2010-2011 T.R Maarlveld,  B.G. Olivier all rights reserved.

Timo R. Maarleveld (tmd200@users.sourceforge.net)
VU University, Amsterdam, Netherlands

Permission to use, modify, and distribute this software is given under the
terms of the StochPy (BSD style) license. 

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
"""

__doc__ =   """        
            StochPy: Stochastic Modeling in Python
            =====================================
            
            StochPy (Stochastic modelling in Python) is an easy-to-use package, which provides several stochastic simulation algorithms (SSAs), which can be used to simulate a biochemical system in a stochastic manner. Further, several unique and easy-to-use analysis techniques are provided by StochPy.

            Actually, StochPy is an extention of PySCeS. PySCeS - the Python Simulator for Cellular Systems - is an extendable toolkit for the analysis and investigation of cellular systems. It is available for download from: http://pysces.sourceforge.net

            
            Options:
            --------
            - Stochastic Simulations
            - Variety of stochastic simulation output analysis:
              --> Time Simulation
              --> Distribution
              --> Waiting times
              --> Propensities
            - Nucleosome Modification Simulations            
            - Converts automatically deterministic rate equations into stochastic rate equations
            - SBML and psc input format.

            StochPy can be used in an interactive Python shell:

            Usage
            -----            
            >>> import stochpy
            >>> sim = stochpy.NucSim()
            >>> help(sim)
            >>> help(stochpy.NucSim)   # (some windows versions)
            >>> mod = stochpy.SSA()    # stochastic simulation algorithm module
            >>> help(mod)
            >>> help(stochpy.SSA)      # (some windows versions)
            >>> model = stochpy.NucModel()
            >>> help(model)
            >>> help(stochpy.model)    # (some windows versions)
            >>> converter = stochpy.SBML2PSC()
            >>> help(converter)
            >>> help(stochpy.SBML2PSC) # (some windows versions)            
            ...
            ...
            """

__version__ = '1.0'

import os

try:
    from numpy.distutils.core import setup#, Extension
except Exception, ex:
    print ex
    print "StochPy requires NumPy \n"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    os.sys.exit(-1)

try:
    import matplotlib.pyplot as plt
    import pylab
except:
    print "Warning: The Matplotlib module is not available, so it is impossible to create plots"
    print "Info: See http://matplotlib.sourceforge.net/ for more information about Matplotlib"

def InitiateModels(Dir):
  """
  Builds at the first import of StochPy several psc models
  """
  import pscmodels
  import stochpy.pscmodels.Burstmodel as Burstmodel
  import stochpy.pscmodels.BirthDeath as BirthDeath
  import stochpy.pscmodels.ImmigrationDeath as ImmigrationDeath
  import stochpy.pscmodels.DecayingDimerizing as DecayingDimerizing
  import stochpy.pscmodels.autoreg as autoreg
  import stochpy.pscmodels.autoreg_xml as autoreg_xml
  import stochpy.pscmodels.OneNucleosome as OneNucleosome
  import stochpy.pscmodels.TwoNucleosome as TwoNucleosome
  import stochpy.pscmodels.ThreeNucleosome as ThreeNucleosome  

  import stochpy.pscmodels.model1 as model1
  import stochpy.pscmodels.model2 as model2
  import stochpy.pscmodels.model3 as model3
  import stochpy.pscmodels.model4 as model4
  import stochpy.pscmodels.model5 as model5
  import stochpy.pscmodels.model6 as model6
  import stochpy.pscmodels.model7 as model7
  import stochpy.pscmodels.model8 as model8

  import stochpy.pscmodels.chain5 as chain5
  import stochpy.pscmodels.chain50 as chain50
  import stochpy.pscmodels.chain500 as chain500
  import stochpy.pscmodels.chain1500 as chain1500

  import stochpy.pscmodels.uniform_bistable as UniformBistable
  import stochpy.pscmodels.uniform_monostable as UniformMonostable
  import stochpy.pscmodels.uniform_inbetween as UniformInbetween

  models = {}
  models['Burstmodel']       = Burstmodel.model
  models['ImmigrationDeath'] = ImmigrationDeath.model
  models['BirthDeath']       = BirthDeath.model
  models['DecayingDimerizing']  = DecayingDimerizing.model
  models['autoreg']  	     = autoreg.model
  models['autoreg.xml']	     = autoreg_xml.model

  models['OneNucleosome']    = OneNucleosome.model
  models['TwoNucleosome']    = TwoNucleosome.model
  models['ThreeNucleosome']  = ThreeNucleosome.model
  models['UniformBistable']  = UniformBistable.model
  models['UniformMonostable']= UniformMonostable.model
  models['UniformInbetween'] = UniformInbetween.model  

  models['chain5']     = chain5.model
  models['chain50']    = chain50.model
  models['chain500']   = chain500.model
  models['chain1500']  = chain1500.model

  models['model1'] = model1.model
  models['model2'] = model2.model
  models['model3'] = model3.model
  models['model4'] = model4.model
  models['model5'] = model5.model
  models['model6'] = model6.model
  models['model7'] = model7.model
  models['model8'] = model8.model

  mods = models.keys()
  for mod in mods:
    if '.xml' in mod:
      file = open(Dir+'/'+mod,'w')
      file.write(models[mod])
      file.close()
    else:
      file = open(Dir+'/'+mod+'.psc','w')
      file.write(models[mod])
      file.close()

  del Burstmodel,ImmigrationDeath,DecayingDimerizing,OneNucleosome,TwoNucleosome,ThreeNucleosome,UniformBistable,UniformMonostable,UniformInbetween

mutput_dir = None
model_dir = None
Initiate = 0
if os.sys.platform != 'win32':
  if not os.path.exists(os.path.join(os.path.expanduser('~'),'Stochpy')):
      os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy'))
  if not os.path.exists(os.path.join(os.path.expanduser('~'),'Stochpy', 'pscmodels')):
      os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels'))
  if not os.path.exists(os.path.join(os.path.expanduser('~'),'Stochpy', 'temp')):
      os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy','temp'))
      Initiate = 1

  output_dir = os.path.join(os.path.expanduser('~'),'Stochpy')
  model_dir  = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
  temp_dir  = os.path.join(os.path.expanduser('~'),'Stochpy','temp')

  if Initiate: InitiateModels(model_dir) 
else:
  if not os.path.exists(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy')):
      os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy'))
  if not os.path.exists(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')):
      os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels'))
  if not os.path.exists(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp')):                            
      os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp'))
      Initiate = 1
  output_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy',)
  model_dir  = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
  temp_dir  = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp')

  if Initiate: InitiateModels(model_dir)
 
import modules
import lib
from SBML2PSC import SBML2PSC
from StochSim import SSA                        # Perform SSAs
from NucleosomeModel import NucModel            # Build Nucleosome Modifcation models
from NucleosomeSimulations import NucSim        # Use SSAs on nucleosome modification models

def DeletePreviousOutput(path,pattern):
    for each in os.listdir(path):
        if pattern in each:
            name = os.path.join(path,each)           
            os.remove(name)

DeletePreviousOutput(temp_dir,'.dat')
DeletePreviousOutput(temp_dir,'temp_parse_module')

print """
#######################################################################
#                                                                     #
#            Welcome to the interactive StochPy environment           #
#                                                                     #
#######################################################################
#    StochPy: Stochastic modelling in Python                          #
#    http://stompy.sourceforge.net                                    #
#    Copyright(C) T.R Maarleveld, B.G. Olivier 2010-2011              #
#    Email: tmd200@users.sourceforge.net                              #
#    VU University, Amsterdam, Netherlands                            #
#    StochPy is distributed under the BSD licence.                    #
#######################################################################
"""
print "Version",__version__
print "Output Directory:",output_dir
print "Model Directory:", model_dir

del Initiate
