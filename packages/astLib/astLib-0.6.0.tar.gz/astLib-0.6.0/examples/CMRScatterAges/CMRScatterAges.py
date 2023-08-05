#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Estimates galaxy ages in a cluster from the observed scatter about the color-magnitude relation, for
# a given stellar population model. This is very slow! Reducing size of time steps gives bad results.
# real    782m43.019s eeeek!

import sys
import os
from astLib import astStats
from astLib import astSED
from astLib import astCalc
import pylab
import numpy
import math
import random

# Constants
TEND_STEPS=10   # number of time steps
NGAL=100        # number of simulated galaxies

# Parameters - for RX J0152.7-1357 z=0.83 (Blakeslee et al. 2006, ApJ, 644, 30)
modelFileName="../../../../testingData/models/tau0p1Gyr_m62.1" # BC03 model, solar metallicity, 0.1 Gyr burst
filt1FileName="../../../../testingData/filters/F625W_WFC.res"
filt2FileName="../../../../testingData/filters/F850LP_WFC.res"
colourName="r625-z850"
zCluster=0.83
obsScatter=0.083
errObsScatter=0.009
outDir="output_CMRScatterAges"

csp=astSED.BC03Model(modelFileName)
filt1=astSED.Passband(filt1FileName)
filt2=astSED.Passband(filt2FileName)
if os.path.exists(outDir) == False:
    os.mkdir(outDir)
    
tEndMin=0.0
tEndMax=astCalc.tz(zCluster)
tEndSteps=TEND_STEPS
tEndStepSize=(tEndMax-tEndMin)/tEndSteps

scatters=[]     # list of scatters as a function of tEnd
meanColours=[]  # list of means of galColours for each tEnd
galColours=[]   # all galaxy colours generated for tEnd, in case we need to store them for post processing
galAges=[]      # all the individual galaxy ages at the cluster redshift (tz(zCLuster)-tBirth)
lumAges=[]      # mean luminosity weighted age
tEnds=[]        # just makes it easier to plot etc. using pylab
minAges=[]      # this is just tzCluster-tEnd

tzCluster=astCalc.tz(zCluster)

for t in range(1,tEndSteps):
    
    tEnd=tEndMin+t*tEndStepSize
    tEnds.append(tEnd)
    minAges.append(tzCluster-tEnd)
    
    print "--> tEnd = "+str(tEnd)
    
    colours=[]
    ages=[]
    for n in range(NGAL):
        
        # Progress update
        tenPercent=NGAL/10
        for j in range(0,11):
            if n == j*tenPercent:
                print "... "+str(j*10)+"% complete ..."
        
        tBirth=random.uniform(0, tEnd)
        sed=csp.getSED(tzCluster-tBirth, z = zCluster)
        col=sed.calcColour(filt1, filt2, magType="AB")
        colours.append(col)
        ages.append(tzCluster-tBirth)
    
    scatters.append(astStats.biweightScale(colours, 6.0))
    meanColours.append(astStats.biweightLocation(colours, 6.0))
    
    # To get the mean luminosity weighted age, weight by the number of galaxies of a particular colour
    colourMin=min(colours)
    colourMax=max(colours)
    colourBins=NGAL/100
    colourBinStep=(colourMax-colourMin)/colourBins
    colourBinAges=[]    # store all the ages for each colour bin here, then average them
    colourBinN=[0]*colourBins
    for b in range(colourBins):
        colourBinAges.append([])
    for a, c in zip(ages, colours):
        for b in range(colourBins):
            if c > colourMin+b*colourBinStep and c <= colourMin+(b+1)*colourBinStep:
                colourBinAges[b].append(a)
                colourBinN[b]=colourBinN[b]+1
    weightedAges=[]
    for a, c in zip(colourBinAges, colourBinN):
        weightedAges.append([numpy.mean(a), c])
    lumAges.append(astStats.weightedMean(weightedAges))

# PLOTS
plotGyrRange=range(6)

# Intrinsic scatter vs. minimum age plot
pylab.cla()
pylab.plot(minAges, scatters)
pylab.plot(plotGyrRange, len(plotGyrRange)*[obsScatter-errObsScatter], 'r--')
pylab.plot(plotGyrRange, len(plotGyrRange)*[obsScatter], 'r-')
pylab.plot(plotGyrRange, len(plotGyrRange)*[obsScatter+errObsScatter], 'r--')
pylab.ylabel(colourName+' Intrinsic Scatter')
pylab.xlabel('Minimum Age (Gyr)')
pylab.savefig(outDir+"/"+colourName+'_'+str(zCluster)+'_minAgeScatter.png')

# Intrinsic scatter vs. luminosity weighted age plot
pylab.cla()
pylab.plot(lumAges, scatters)
pylab.plot(plotGyrRange, len(plotGyrRange)*[obsScatter-errObsScatter], 'r--')
pylab.plot(plotGyrRange, len(plotGyrRange)*[obsScatter], 'r-')
pylab.plot(plotGyrRange, len(plotGyrRange)*[obsScatter+errObsScatter], 'r--')
pylab.ylabel(colourName+' Intrinsic Scatter')
pylab.xlabel('Luminosity Weighted Age (Gyr)')
pylab.savefig(outDir+"/"+colourName+'_'+str(zCluster)+'_lumAgeScatter.png')

# Write output to .ages file
outFile=file(outDir+"/"+colourName+'_'+str(zCluster)+'.ages', "wb")
outFile.write("#nGal = "+str(NGAL)+"\n")
outFile.write("#tEnd (Gyr)\tscatter\tmeanColour\tminAge (Gyr)\tlumAge (Gyr)\n")
for t, s, c, m, a in zip(tEnds, scatters, meanColours, minAges, lumAges):
    outFile.write(str(t)+"\t"+str(s)+"\t"+str(c)+"\t"+str(m)+"\t"+str(a)+"\n")
outFile.close()
