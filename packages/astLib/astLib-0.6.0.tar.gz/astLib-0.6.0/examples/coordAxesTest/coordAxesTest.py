#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Miscellaneous tests of coord axes labelling
# 
from astLib import *
import pyfits

# Tests high dec
img=pyfits.open("../../../../testingData/testImage3.fits")
d=img[0].data
wcs=astWCS.WCS("../../../../testingData/testImage3.fits")
RADeg, decDeg=wcs.getCentreWCSCoords()
clip=astImages.clipRotatedImageSectionWCS(d, wcs, RADeg, decDeg, 18.0/60.0)
ip=astPlots.ImagePlot(clip['data'], clip['wcs'], axesLabels="sexagesimal")
ip.save("testHighDec.png")

# Tests 0h wraparound of coord axes labelling
img=pyfits.open("../../../../testingData/testCEAImage.fits")
d=img[0].data
wcs=astWCS.WCS("../../../../testingData/testCEAImage.fits")
ip=astPlots.ImagePlot(d, wcs, axesLabels="sexagesimal")
ip.save("testWraparound.png")

# Second test of 0h wraparound, tan projection image
# Tests 0h wraparound of coord axes labelling
img=pyfits.open("../../../../testingData/0hCrossing.fits")
d=img[0].data
wcs=astWCS.WCS("../../../../testingData/0hCrossing.fits")
ip=astPlots.ImagePlot(d, wcs, axesLabels="sexagesimal", cutLevels = [-200, 100])
ip.save("testWraparoundTan.png")

