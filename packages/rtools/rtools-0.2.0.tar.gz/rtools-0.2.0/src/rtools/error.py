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
"""error and warning messages from R

Created by Thomas Cokelaer <cokelaer@ebi.ac.uk>
Copyright (c) 2011. GPL

"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])

__all__ = ["Rwarning", "RRuntimeError"]

import rpy2.robjects
from rpy2.robjects import r
RRuntimeError = rpy2.robjects.rinterface.RRuntimeError

 
def Rwarning(state=True):
    """Set warning on/off"""

    if state==True:
        r("options(warn = (-1))")
        r("options(show.error.messages=TRUE)")
    else:
        r("options(warn = (-1))")
        r("options(show.error.messages=FALSE)")


