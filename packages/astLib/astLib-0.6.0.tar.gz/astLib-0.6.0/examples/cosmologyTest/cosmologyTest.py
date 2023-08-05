#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Tests astCalc routines

from astLib import astCalc
import numpy
import pylab
pylab.matplotlib.interactive(True)

# For interactive debugging, just put an ipshell() call where want to drop into program
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed([], banner = 'Dropping into IPython', exit_msg = 'Leaving Interpreter, back to program.')

omegaMs=[1.0, 0.2, 0.05]
omegaLs=[0.0, 0.8, 0.0]
styles=['r-', 'b--', 'g:']
z=numpy.arange(0, 6, 0.1)

# da
pylab.clf()
for m, l, s in zip(omegaMs, omegaLs, styles):
    astCalc.OMEGA_M0=m
    astCalc.OMEGA_L=l
    label="$\Omega_{m0}$ = %.2f $\Omega_\Lambda$ = %.2f" % (m, l) 
    dH=astCalc.C_LIGHT/astCalc.H0
    plotData=[]
    for i in z:
        plotData.append(astCalc.da(i)/dH)
    pylab.plot(z, plotData, s, label=label)
pylab.ylim(0, 0.5)
pylab.xlim(0, 5)
pylab.xlabel("$z$")
pylab.ylabel("$D_A/D_H$")
pylab.legend(loc='lower right')

# dV/dz
pylab.clf()
for m, l, s in zip(omegaMs, omegaLs, styles):
    astCalc.OMEGA_M0=m
    astCalc.OMEGA_L=l
    label="$\Omega_{m0}$ = %.2f $\Omega_\Lambda$ = %.2f" % (m, l) 
    dH=astCalc.C_LIGHT/astCalc.H0
    plotData=[]
    for i in z:
        plotData.append((1.0/dH)**3*astCalc.dVcdz(i))
    pylab.plot(z, plotData, s, label=label)
pylab.ylim(0, 1.1)
pylab.xlim(0, 5)
pylab.xlabel("$z$")
pylab.ylabel("$(1/D_H)^3 dV/dz/d\Omega$")
pylab.legend(loc='upper left')

ipshell()