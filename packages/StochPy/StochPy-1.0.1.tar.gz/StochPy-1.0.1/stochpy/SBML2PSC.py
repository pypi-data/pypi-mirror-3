"""
Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 15, 2011
"""

class SBML2PSC():
  """
  Module that converts SBML models into PSC models if libxml and libsbml are installed

  Usage:
  >>> converter = stochpy.SBML2PSC()
  >>> converter.SBML2PSC('file.xml',directory) 
  """   
  def __init__(self):
      pass

  def SBML2PSC(self,sbmlfile, sbmldir=None, pscfile=None, pscdir=None):
      """
      Converts a SBML file to a PySCeS MDL input file.

      Input:
       - *sbmlfile*: the SBML file name
       - *sbmldir*: [default = None] the directory of SBML files (if None current working directory is assumed)
       - *pscfile*: [default = None] the output PSC file name (if None *sbmlfile*.psc is used)
       - *pscdir*: [default = None] the PSC output directory (if None the pysces.model_dir is used)
      """
      import stochpy.PyscesInterfaces as module
      module.Core2interfaces().convertSBML2PSC(sbmlfile,sbmldir,pscfile,pscdir)
