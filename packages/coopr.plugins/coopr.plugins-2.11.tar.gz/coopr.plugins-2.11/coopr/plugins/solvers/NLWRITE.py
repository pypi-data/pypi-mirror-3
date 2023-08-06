#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import re
import pyutilib.misc
from coopr.opt.base import *
from coopr.opt.results import *
from coopr.opt.solver import *


class NLWRITE(SystemCallSolver):
    """The NLWRITE .nl file writer (as a solver)
    """

    def __init__(self, **kwds):
        kwds['type'] = 'nlwrite'
        SystemCallSolver.__init__(self, **kwds)
        self._valid_problem_formats=[ProblemFormat.nl]
        self._valid_result_formats=[ResultsFormat.soln]

    def defaultPath(self):
        return "/bin/true"

    def create_command_line(self,executable,problem_files):
        return pyutilib.misc.Bunch(cmd="/bin/true", log_file=None, env=None)
