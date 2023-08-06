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
from coopr.opt.base import *
from coopr.opt.results import *
from coopr.opt.solver import *
import pyutilib.services
import pyutilib.common
import pyutilib.common
import pyutilib.component.core
import pyutilib.component.config
import pyutilib.misc
import mockmip
import os
import copy


class ASL(SystemCallSolver):
    """A generic optimizer that uses the AMPL Solver Library to interface with applications.
    """

    pyutilib.component.core.alias('_asl', doc='Shell interface to a generic optimizer that uses the AMPL Solver Library to interface with application')

    def __init__(self, **kwds):
        #
        # Call base constructor
        #
        kwds["type"] = "asl"
        SystemCallSolver.__init__(self, **kwds)
        #
        # Setup valid problem formats, and valid results for each problem format
        #
        self._valid_problem_formats=[ProblemFormat.nl]
        self._valid_result_formats = {}
        self._valid_result_formats[ProblemFormat.nl] = [ResultsFormat.sol]

        # Note: Undefined capabilities default to 'None'
        self._capabilities = pyutilib.misc.Options()
        self._capabilities.linear = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True
        self._capabilities.sosn = True

    def executable(self):
        #
        # We register the ASL executables dynamically, since _any_ ASL solver could be
        # executed by this solver.
        #
        try:
            if self.options.solver is None:
                raise pyutilib.component.config.OptionError('ERROR')
            pyutilib.services.register_executable(self.options.solver)
        except pyutilib.component.config.OptionError:
            raise ValueError, "No solver option specified for ASL solver interface"
        executable = pyutilib.services.registered_executable(self.options.solver)
        if executable is None:
            pyutilib.component.core.PluginGlobals.env().log.error("Could not locate the '%s' executable, which is required for solver %s" % (self.options.solver, self.name))
            self.enable = False
            return None
        return executable.get_path()

    def create_command_line(self, executable, problem_files):
        #
        # Define log file
        #
        if self.log_file is None:
            self.log_file = pyutilib.services.TempfileManager.create_tempfile(suffix="_asl.log")
        fname = problem_files[0]
        if '.' in fname:
            tmp = fname.split('.')
            if len(tmp) > 2:
                fname = '.'.join(tmp[:-1])
            else:
                fname = tmp[0]
        self.soln_file = fname+".sol"
        #
        # Define results file
        #
        if self._results_format is None or self._results_format == ResultsFormat.sol:
            self.results_file = self.soln_file
        #
        # Define command line
        #
        env=copy.copy(os.environ)

        # JDS: I am not sure why we did this test... mostly because if
        # it ever returned false, 'proc' (now cmd) was never
        # initialized, resulting in an exception.
        #if self._problem_format is None or self._problem_format == ProblemFormat.nl:
        #   ...

        cmd = [executable, problem_files[0], '-AMPL']
        if self._timer:
            cmd.insert(0, self._timer)
            
        opt=[]
        for key in self.options:
            if key is 'solver':
                continue
            if isinstance(self.options[key],basestring) and ' ' in self.options[key]:
                opt.append(key+"=\""+str(self.options[key])+"\"")
            elif key == 'subsolver':
                opt.append("solver="+str(self.options[key]))
            else:
                opt.append(key+"="+str(self.options[key]))

        envstr = "%s_options" % self.options.solver
        # Merge with any options coming in through the environment
        env[envstr] = " ".join(opt)
            
        return pyutilib.misc.Bunch(cmd=cmd, log_file=self.log_file, env=env)

    def _default_results_format(self, prob_format):
        return ResultsFormat.sol

    def Xprocess_soln_file(self,results):
        """
        Process the SOL file
        """
        if os.path.exists(self.soln_file):
            results_reader = ReaderFactory(ResultsFormat.sol)
            results = results_reader(self.soln_file, results, results.solution(0))
            return


class MockASL(ASL,mockmip.MockMIP):
    """A Mock ASL solver used for testing
    """

    pyutilib.component.core.alias('_mock_asl')

    def __init__(self, **kwds):
        try:
            ASL.__init__(self,**kwds)
        except pyutilib.common.ApplicationError: #pragma:nocover
            pass                        #pragma:nocover
        mockmip.MockMIP.__init__(self,"asl")

    def available(self, exception_flag=True):
        return ASL.available(self,exception_flag)

    def create_command_line(self,executable,problem_files):
        command = ASL.create_command_line(self,executable,problem_files)
        mockmip.MockMIP.create_command_line(self,executable,problem_files)
        return command

    def executable(self):
        return mockmip.MockMIP.executable(self)

    def _execute_command(self,cmd):
        return mockmip.MockMIP._execute_command(self,cmd)
