#!/usr/bin/env python
"""
=====================
Mock DMS for WebbPSF
=====================


This module provides a very simple mock version of the 
JWST Data Management System (DMS) for use with WebbPSF. 
Its purpose is to take the simple FITS files as produced by WebbPSF and
format them into the somewhat more complicated data products expected from
actual pipeline-processed JWST data, with realistic FITS header keywords 
and so on. 

In particular, it takes the small PSF arrays computed by WebbPSF (which will typically
be at most some tens of arcsec across) and embeds them into a full-sized detector array.

"""


import numpy as np
import matplotlib.pyplot as pl
import pyfits
from IPython.core.debugger import Tracer; stop = Tracer()
import logging
_log = logging.getLogger('webbpsf')


class MockDMS(object):
    def __init__(self):
        pass

    def convert(self, fitsfile):
        """
        Convert a given file

        Parameters
        ----------
        HDUlist_or_filename : pyfits.HDUlist or string
        FITS file containing image to display.
 
        """
        if isinstance(fitsfile, str):
            HDUlist = pyfits.open(fitsfile)
        elif isinstance(fitsfile, pyfits.HDUList):
            HDUlist = fitsfile
        else: raise ValueError("input must be a filename or HDUlist")





if __name__ == "__main__":
        
    logging.basicConfig(level=logging.INFO, format='%(name)-12s: %(levelname)-8s %(message)s',)

    pass


