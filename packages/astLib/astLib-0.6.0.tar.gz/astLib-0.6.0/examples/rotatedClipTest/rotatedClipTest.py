#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Quick script to test out rotation, clipping

import pyfits
from astLib import *

img=pyfits.open("../../../../testingData/testImage1.fits")
wcs=astWCS.WCS("../../../../testingData/testImage1.fits")
d=img[0].data

# Clip slightly off centre
RADeg, decDeg=wcs.getCentreWCSCoords()
RADeg=RADeg+1.2/60.0
decDeg=decDeg-1.0/60.0

clip=astImages.clipRotatedImageSectionWCS(d, wcs, RADeg, decDeg, 3.0/60.0)
clipnr=astImages.clipImageSectionWCS(d, wcs, RADeg, decDeg, 3.0/60.0)

astImages.saveFITS("output_rotated.fits", clip['data'], clip['wcs'])
astImages.saveFITS("output_notRotated.fits", clipnr['data'], clipnr['wcs'])   
