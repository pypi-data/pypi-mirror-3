#!/usr/bin/env python

__doc__ = "StochPy (Stochastic modeling in Python) provides several stochastic simulation algorithms to simulate (bio)chemical systems of reactions in a stochastic manner."
__version__ = '1.0'

import os

try:
    from numpy.distutils.core import setup, Extension
except Exception, ex:
    print ex
    print "StochPy requires NumPy \n"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    os.sys.exit(-1)

local_path = os.path.dirname(os.path.abspath(os.sys.argv[0]))		# Get the dir of setup.py
os.chdir(local_path)

mydata_files = []
modfold = os.path.join(local_path, 'stochpy', 'pscmodels')
mods = os.listdir(modfold)
temp = []
for x in mods:
    if x[-4:] != '.psc': pass
    else: temp.append(os.path.join(modfold,x))
#mydata_files.append((os.path.join('pysnums','pscmodels'),temp))		# Add psc models 

mypackages = ['stochpy','stochpy.lib','stochpy.modules','stochpy.pscmodels','stochpy.core2']		# My subpackage list

setup(name="StochPy",
    version = __version__,
    description = __doc__,
    long_description = """
    Welcome to the installation of StochPy 1.0.0!

    StochPy (Stochastic modelling in Python) is an easy-to-use package, which provides several stochastic simulation algorithms (SSAs), which can be used to simulate a biochemical system in a stochastic manner. Further, several unique and easy-to-use analysis techniques are provided by StochPy.

    StochPy is an extension of PySCeS. PySCeS - the Python Simulator for Cellular Systems - is an extendible tool kit for the analysis and investigation of cellular systems. StochPy operates independently of PySCeS, but it uses several parts of the PySCeS package, such as the text based Model Description Language of PySCeS.     
    """,
    author = "T.R. Maarleveld",
    author_email = "tmd200@users.sourceforge.net",
    maintainer = "T.R. Maarleveld",
    maintainer_email = "tmd200@users.sourceforge.net",
    url = "http://stompy.sourceforge.net",
    download_url = "http://stompy.sourceforge.net/download.html",
    license = " BSD License ",
    keywords = " Bioinformatics, Computational Systems Biology, Bioinformatics, Modelling, Simulation, Stochastic Simulation Algorithms, Stochastic,Nucleosomes", 
    zip_safe = False,
    requires = ['NumPy'],
    platforms = ["Windows", "Linux"],#, "Solaris", "Mac OS-X", "Unix"],
    classifiers = [
    'Development Status :: 1-Alpha',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: OS Independent',    
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Simulations'],
    packages = mypackages,
    data_files = mydata_files
    #ext_modules = mymodules
    )
