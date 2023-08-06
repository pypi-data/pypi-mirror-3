# -*- python -*-
# -*- coding: utf-8 -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: http://www.ebi.ac.uk/saezrodriguez/software.html
#
##############################################################################
# $Id: tools.py 2193 2012-08-22 21:39:17Z cokelaer $
"""Utilities for cnolab.wrapper

Created by Thomas Cokelaer <cokelaer@ebi.ac.uk>
Copyright (c) 2011. GPL

.. testsetup:: *

    from rpy2.robjects.packages import importr
    import numpy
    from cno import *

"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])
__all__ = ['RPackage']

import logging
import os
import rpy2
from rpy2 import robjects
from rpy2.robjects import rinterface
from rpy2.robjects.packages import importr
#from rpy2.robjects import r
from distutils.version import StrictVersion
 
from error import Rwarning, RRuntimeError


import_error = """RTOOLS: could not import R package %s. Try to install it. If you have the source file, you can try to type:

    R CMD INSTALL package_name.tar.gz

or if it is available on BioConductor, type:

    source("http://bioconductor.org/biocLite.R")
    biocLite("package_name.tar.gz")

 """ 


class RPackage(object):
    """simple class to import a R package and get metainfo

    from rtools.package import RPackage
    r = RPackage("CellNOptR")
    r.version()
    r.load()

    # no error returned but only info and error based on logging module.
    """
    def __init__(self, name, require="0.0"):
        self.name = name
        self.package = None
        self.require = require
        self.load()

    def load(self):
        Rwarning(False)
        try:
            package = importr(self.name)
            if StrictVersion(self.version) >= StrictVersion(self.require):
                self.package = package
                logging.info("R package %s loaded." % self.name)
            else:
                Rwarning(True)
                logging.error("could not import %s" % self.name)
                logging.info("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))
                logging.info(import_error % self.name)
                #raise ImportError("Found %s (version %s) but version %s required." % (self.name, self.version, self.require))
        except RRuntimeError:
            logging.error("could not import %s" % self.name)
            logging.info(import_error % self.name)
            #raise ImportError("Could not import R package (%s)." % self.name)
        Rwarning(True)

    def _get_version(self):
        v = robjects.r("""packageVersion("%s")""" % (self.name))[0]
        v = [str(x) for x in v]
        return ".".join(v)
    version = property(_get_version)



