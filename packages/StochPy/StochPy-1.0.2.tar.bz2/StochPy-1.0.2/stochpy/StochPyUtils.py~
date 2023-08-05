 #! /usr/bin/env python
"""
StochPy Utils
=============

Module that contains functions that are created by the users of StochPy. New functions will be added in the next release of StochPy.

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: November 12, 2011
"""

import stochpy as _stochpy_
import numpy as np

mod = _stochpy_.SSA()


def GetAnalyticalPDF(kon,koff,kdeg,ksyn):
    """ Get the analytical probability density function. The analytical solution is taken from Sharezaei and Swain 2008 - Analytical distributions for stochastic gene expression """
    import mpmath        
    mpmath.mp.pretty = True
    x_values = np.linspace(0,50,10000)
    y_values = []
    for m in x_values:
        a = ((ksyn/kdeg)**m)*np.exp(-ksyn/kdeg)/mpmath.factorial(m)
        b = mpmath.mp.gamma((kon/kdeg)+m) * mpmath.mp.gamma(kon/kdeg + koff/kdeg)/ (mpmath.mp.gamma(kon/kdeg + koff/kdeg + m)* mpmath.mp.gamma(kon/kdeg))
        c = mpmath.mp.hyp1f1(koff/kdeg,kon/kdeg + koff/kdeg + m,ksyn/kdeg)
        y_values.append(a*b*c)
    return x_values,y_values


def GetAnalyticalWaitingtimes(kon,koff,ksyn):
    """ Get analytical waiting times """
    import mpmath        
    mpmath.mp.pretty = True    
    A = mpmath.sqrt(-4*ksyn*kon+(koff + kon + ksyn)**2)
    x = []
    for i in np.linspace(-20,5,5000):
        x.append(mpmath.exp(i))     
    y = []
    for t in x:
        B = koff + ksyn - (mpmath.exp(t*A)*(koff+ksyn-kon))-kon+A+ mpmath.exp(t*A)*A
        p01diff = mpmath.exp(-0.5*t*(koff + kon + ksyn+A))*B/(2.0*A)
        y.append(p01diff*ksyn)        
    return (x,y)   

class Utils():
    def __init__(self):
        pass

    def doExample1(self):
        """ Example 1 of http://stompy.sourceforge.net/examples.html """        
        import numpy as np
        mod.Model('ImmigrationDeath.psc')  # Ksyn = 10, Kdeg = 0.2, and mRNA(init) = 50
        lambda_ = 50
        N = 1500000
        data = np.random.poisson(lambda_,N)
        mod.DoStochSim(end=N,mode='steps')
        mod.PlotDistributions(linestyle= 'solid')
        n, bins, patches = _stochpy_.plt.hist(data-0.5, max(data)-min(data),normed=1, facecolor='green')
        mod.ShowMeans()
        mod.ShowStandardDeviations()        
    
    def doExample2(self):
        """ Example 2 of http://stompy.sourceforge.net/examples.html """
        mod.Model('dsmts-003-04.xml.psc')
        mod.DoStochSim(end = 50,mode = 'time',trajectories = 10000)
        mod.PlotInterpolatedData()
        mod.PrintInterpolatedData()
        
    def doExample3(self):
        mod.Model('Burstmodel.psc')  # Parameter values in Burstmodel.psc: kon = koff = 0.05
        ntimesteps = 1500000
        mod.DoStochSim(end=ntimesteps,mode='steps')
        mod.PlotDistributions(species2plot = 'mRNA', colors=['#00FF00'],linestyle = 'solid') # Usage of html color codes
        mod.PlotWaitingtimes('R3', colors=['#00FF00'],linestyle = 'None',marker='o')
        
        print 'Change Parameter values in Burstmodel.psc: kon = koff = 5.0'
        temp = raw_input('Press any button if you have done this')
        mod.Reload()
        mod.DoStochSim(end=ntimesteps,mode='steps')
        mod.plot.plotnum = 1
        mod.PlotDistributions(species2plot = 'mRNA', colors='r',linestyle = 'solid')
        
        kon = 0.05
        koff = 0.05
        kdeg = 2.5
        ksyn = 80.0
        x,y = GetAnalyticalPDF(kon,koff,kdeg,ksyn)
        _stochpy_.plt.figure(1)
        _stochpy_.plt.step(x,y,color ='k')

        kon = 5.0
        koff = 5.0
        x,y = GetAnalyticalPDF(kon,koff,kdeg,ksyn)
        _stochpy_.plt.step(x,y,color ='k')
        _stochpy_.plt.xlabel('mRNA copy number per cell')
        _stochpy_.plt.ylabel('Probability mass')
        _stochpy_.plt.legend(['Bimodal','Unimodal', 'Analytical solution'],numpoints=1,frameon=False)
        _stochpy_.plt.title('')
        _stochpy_.plt.ylim([0,0.045])
        
        mod.PlotWaitingtimes('R3', colors=['r'],linestyle = 'None',marker='v')
        kon = 0.05
        koff = 0.05
        (x,y) = GetAnalyticalWaitingtimes(kon,koff,ksyn)
        _stochpy_.plt.figure(2)
        _stochpy_.plt.plot(x,y,color ='k')

        kon = 5.0
        koff = 5.0
        (x,y) = GetAnalyticalWaitingtimes(kon,koff,ksyn)
        _stochpy_.plt.plot(x,y,color ='k')
        _stochpy_.plt.xlabel('Time between RNA synthesis events')
        _stochpy_.plt.ylabel('Probability density')
        _stochpy_.plt.legend(['Bimodal','Unimodal', 'Analytical solution'],numpoints=1,frameon=False,loc='lower left')
        _stochpy_.plt.title('')
        _stochpy_.plt.xlim([10**-7,10**3])
        _stochpy_.plt.ylim([10**-9,10**3])        
