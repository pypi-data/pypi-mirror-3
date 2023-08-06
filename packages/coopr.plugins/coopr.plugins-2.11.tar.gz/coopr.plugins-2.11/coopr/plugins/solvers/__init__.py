#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import pyutilib.component.core
pyutilib.component.core.PluginGlobals.push_env( 'coopr.opt' )

from ps import PatternSearch
from PICO import PICO, MockPICO
from CBCplugin import CBC, MockCBC
from GLPK import GLPK, configure_glpk
import GLPK_old
from glpk_direct import GLPKDirect
from CPLEX import CPLEX, MockCPLEX
from CPLEXDirect import CPLEXDirect
from GUROBI import GUROBI
from gurobi_direct import gurobi_direct
from ASL import ASL, MockASL
from XPRESS import XPRESS, MockXPRESS

#
# Interrogate the CBC executable to see if it recognizes the -AMPL flag
#
import CBCplugin
CBCplugin.configure()

#
# Interrogate the glpsol executable to see if it is new enough to allow the new parser logic
#
configure_glpk()

pyutilib.component.core.PluginGlobals.pop_env()
