#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Test of image scaling

from astLib import *
import pyfits

TEST_IMAGE="../../../../testingData/testImage1.fits"

img=pyfits.open(TEST_IMAGE)
wcs=astWCS.WCS(TEST_IMAGE)
d=img[0].data

scaled=astImages.scaleImage(d, wcs, 0.55)
astImages.saveFITS("output_scaleTest.fits", scaled['data'], scaled['wcs'])
