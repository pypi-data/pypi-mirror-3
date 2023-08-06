# -* python -*-
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
# $Id: meigo.py 2060 2012-08-12 17:59:38Z cokelaer $
"""Provide a class to run MEIGO optiisation


"""
import os
import copy
import time
from os.path import join as pj

from rpy2 import robjects

from wrapper_meigo import essR
from pylab import *
__all__ = ["MEIGO"]



class MEIGO(object):
    """class MEIGO around :mod:`pymeigo.wrapper_meigo`


    .. plot::
        :include-source:

        from pymeigo import MEIGO, rosen_for_r
        m = MEIGO(f=rosen_for_r)
        m.run(x_U=[2,2], x_L=[-1,-1])
        m.plot()

    """
    def __init__(self, f):
        """
        :param f: a R version of a python function. See :mod:`~pymeigo.funcs.pyfunc2R`.
        """
        self.func = f

    def run(self, x_U=[2,2], x_L=[-1,-1], **kargs):
        """


        :param x_U: upper limit of the parameter
        :param x_U: lower limit of the parameter

        see :func:`~pymeigo.wrapper_meigo.essR` for arguments.

        """
        self.res =  essR(f=self.func, x_U=x_U, x_L=x_L, **kargs)

    def plot(self):
        """plotting the evolution of the cost function"""

        plot(self.res.f)
        xlabel("Evaluation")
        ylabel("Cost function")


        semilogy(self.res.f)
        xlabel("Evaluation")
