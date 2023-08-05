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
import pyutilib.misc
import mockmip
import os
import copy
import logging


class PICO(OptSolver):
    """The PICO LP/MIP solver
    """

    pyutilib.component.core.alias('pico', doc='The PICO MIP solver')

    def __new__(cls, *args, **kwds):
        try:
            mode = kwds['solver_io']
            if mode is None:
                mode = 'lp'
            del kwds['solver_io']
        except KeyError:
            mode = 'lp'
        #
        if mode  == 'lp':
            return SolverFactory('_pico_shell', **kwds)
        #
        if mode == 'nl':
            opt = SolverFactory('_asl', **kwds)
        elif mode == 'os':
            opt = SolverFactory('_ossolver', **kwds)
        else:
            logging.getLogger('coopr.plugins').error('Unknown IO type: %s' % mode)
            return
        opt.set_options('solver=PICO')
        return opt


class PICOSHELL(SystemCallSolver):
    """Shell interface to the PICO LP/MIP solver
    """

    pyutilib.component.core.alias('_pico_shell', doc='Shell interface to the PICO MIP solver')

    def __init__(self, **kwds):
        #
        # Call base constructor
        #
        kwds["type"] = "pico"
        SystemCallSolver.__init__(self, **kwds)
        #
        # Setup valid problem formats, and valid results for each problem format
        #
        self._valid_problem_formats=[ProblemFormat.cpxlp, ProblemFormat.nl, ProblemFormat.mps]
        self._valid_result_formats = {}
        self._valid_result_formats[ProblemFormat.cpxlp] = [ResultsFormat.soln]
        self._valid_result_formats[ProblemFormat.nl] = [ResultsFormat.sol]
        self._valid_result_formats[ProblemFormat.mps] = [ResultsFormat.soln]

        # Note: Undefined capabilities default to 'None'
        self._capabilities = pyutilib.misc.Options()
        self._capabilities.linear = True
        self._capabilities.integer = True
        #self._capabilities.sos1 = True
        #self._capabilities.sos2 = True

    def executable(self):
        executable = pyutilib.services.registered_executable("PICO")
        if executable is None:
            pyutilib.component.core.PluginGlobals.env().log.error("Could not locate the 'PICO' executable, which is required for solver %s" % self.name)
            self.enable = False
            return None
        return executable.get_path()

    def create_command_line(self,executable,problem_files):
        #
        # Define log file
        #
        if self.log_file is None:
            self.log_file = pyutilib.services.TempfileManager.create_tempfile(suffix="PICO.log")
        fname = problem_files[0].split(os.sep)[-1]
        if '.' in fname:
            tmp = fname.split('.')
            if len(tmp) > 2:
                fname = '.'.join(tmp[:-1])
            else:
                fname = tmp[0]
        if self.soln_file is None:
            self.soln_file = pyutilib.services.TempfileManager.create_tempfile(suffix=fname+".soln")
        self.sol_file = fname+".sol"
        #
        # Define results file
        #
        if self._results_format is None or self._results_format == ResultsFormat.soln:
            self.results_file = self.soln_file
        elif self._results_format == ResultsFormat.sol:
            self.results_file = self.sol_file
        #
        # Eventually, these formats will be added to PICO...
        #
        #elif self._results_format == ResultsFormat.osrl:
            #self.results_file = self.tmpDir+os.sep+"PICO.osrl.xml"
        #
        # Define command line
        #
        if (self.options.mipgap is not None):
            raise ValueError, "The mipgap parameter is currently not being processed by PICO solver plugin"
        env=copy.copy(os.environ)
        if self._problem_format is None or self._problem_format == ProblemFormat.nl:
            if "debug" in self.options:
                opts = []
            else:
                opts = ["debug=2"]
            for key in self.options:
                if key == 'mipgap':
                    continue
                if isinstance(self.options[key],basestring) and ' ' in self.options[key]:
                    opts.append(key+"=\""+str(self.options[key])+"\"")
                else:
                    opts.append(key+"="+str(self.options[key]))
            env["PICO_options"] = ' --allowInfiniteIntegerVarBounds=true '+" ".join(opts)
            proc = self._timer + " " + executable + " " + problem_files[0] + " -AMPL"
        elif self._problem_format == ProblemFormat.cpxlp or self._problem_format == ProblemFormat.mps:
            opt = ' --allowInfiniteIntegerVarBounds=true '
            if "debug" in self.options:
                opt += ""
            else:
                opt += " --debug 2"
            for key in self.options:
                if key == 'mipgap':
                    continue
                if isinstance(self.options[key],basestring) and ' ' in self.options[key]:
                    opt += " --"+key+"=\""+str(self.options[key])+"\""
                else:
                    opt += " --"+key+"="+str(self.options[key])
            proc = self._timer + " " + executable + opt + " --output " + self.soln_file + " " + problem_files[0]
        return pyutilib.misc.Bunch(cmd=proc, log_file=self.log_file, env=env)

    def process_logfile(self):
        """
        Process a logfile
        """
        results = SolverResults()
        #
        # Initial values
        #
        #results.solver.statistics.branch_and_bound.number_of_created_subproblems=0
        #results.solver.statistics.branch_and_bound.number_of_bounded_subproblems=0
        soln = Solution()
        soln.objective['__default_objective__'].value = None
        #
        # Process logfile
        #
        OUTPUT = open(self.log_file)
        output = "".join(OUTPUT.readlines())
        OUTPUT.close()
        #
        # Parse logfile lines
        #
        for line in output.split("\n"):
            tokens = re.split('[ \t]+',line.strip())
            if len(tokens) > 3 and tokens[0] == "ABORTED:":
                results.solver.status=SolverStatus.aborted
            elif len(tokens) > 1 and tokens[0].startswith("ERROR"):
                results.solver.status=SolverStatus.error
            elif len(tokens) == 3 and tokens[0] == 'Problem' and tokens[2].startswith('infeasible'):
                results.solver.termination_condition = TerminationCondition.infeasible
            elif len(tokens) == 2 and tokens[0] == 'Integer' and tokens[1] == 'Infeasible':
                results.solver.termination_condition = TerminationCondition.infeasible
            elif len(tokens) == 5 and tokens[0] == "Final" and tokens[1] == "Solution:":
                soln.objective['__default_objective__'].value = eval(tokens[4])
                soln.status = SolutionStatus.optimal
            elif len(tokens) == 3 and tokens[0] == "LP" and tokens[1] == "value=":
                soln.objective['__default_objective__'].value = eval(tokens[2])
                soln.status=SolutionStatus.optimal
                if results.problem.sense == ProblemSense.minimize:
                    results.problem.lower_bound = eval(tokens[2])
                else:
                    results.problem.upper_bound = eval(tokens[2])
            elif len(tokens) == 2 and tokens[0] == "Bound:":
                if results.problem.sense == ProblemSense.minimize:
                    results.problem.lower_bound = eval(tokens[1])
                else:
                    results.problem.upper_bound = eval(tokens[1])
            elif len(tokens) == 3 and tokens[0] == "Created":
                results.solver.statistics.branch_and_bound.number_of_created_subproblems = eval(tokens[1])
            elif len(tokens) == 3 and tokens[0] == "Bounded":
                results.solver.statistics.branch_and_bound.number_of_bounded_subproblems = eval(tokens[1])
            elif len(tokens) == 2 and tokens[0] == "sys":
                results.solver.system_time=eval(tokens[1])
            elif len(tokens) == 2 and tokens[0] == "user":
                results.solver.user_time=eval(tokens[1])
            elif len(tokens) == 3 and tokens[0] == "Solving" and tokens[1] == "problem:":
                results.problem.name = tokens[2]
            elif len(tokens) == 4 and tokens[2] == "constraints:":
                results.problem.number_of_constraints = eval(tokens[3])
            elif len(tokens) == 4 and tokens[2] == "variables:":
                results.problem.number_of_variables = eval(tokens[3])
            elif len(tokens) == 4 and tokens[2] == "nonzeros:":
                results.problem.number_of_nonzeros = eval(tokens[3])
            elif len(tokens) == 3 and tokens[1] == "Sense:":
                if tokens[2] == "minimization":
                    results.problem.sense = ProblemSense.minimize
                else:
                    results.problem.sense = ProblemSense.maximize

        if results.solver.status is SolverStatus.aborted:
            soln.optimality=SolutionStatus.unsure
        if soln.status is SolutionStatus.optimal:
            soln.gap=0.0
            results.problem.lower_bound = soln.objective['__default_objective__'].value
            results.problem.upper_bound = soln.objective['__default_objective__'].value

        if soln.status == SolutionStatus.optimal:
            results.solver.termination_condition = TerminationCondition.optimal

        if not results.solver.status is SolverStatus.error and \
            results.solver.termination_condition in [TerminationCondition.unknown,
                        #TerminationCondition.maxIterations,
                        #TerminationCondition.minFunctionValue,
                        #TerminationCondition.minStepLength,
                        TerminationCondition.globallyOptimal,
                        TerminationCondition.locallyOptimal,
                        TerminationCondition.optimal,
                        #TerminationCondition.maxEvaluations,
                        TerminationCondition.other]:
                results.solution.insert(soln)
        return results


    def process_soln_file(self,results):

        if self._results_format is ResultsFormat.sol:
            return

        # the only suffixes that we extract from PICO are
        # constraint duals. scan through the solver suffix
        # list and throw an exception if the user has
        # specified any others.
        extract_duals = False
        for suffix in self.suffixes:
            if re.match(suffix,"dual"):
                extract_duals = True
            else:
                raise RuntimeError,"***PICO solver plugin cannot extract solution suffix="+suffix

        #if os.path.exists(self.sol_file):
            #results_reader = ReaderFactory(ResultsFormat.sol)
            #results = results_reader(self.sol_file, results, results.solution(0))
            #return

        if not os.path.exists(self.soln_file):
            return
        if len(results.solution) == 0:
            return
        soln = results.solution(0)
        results.problem.num_objectives=1
        tmp=[]
        flag=False
        INPUT = open(self.soln_file,"r")
        lp_flag=None
        var_flag=True
        for line in INPUT:
            tokens = re.split('[ \t]+',line.strip())
            if len(tokens) == 0 or (len(tokens) == 1 and tokens[0]==''):
                continue
            if tokens[0] == "Objective":
                continue
            #print "LINE",tokens
            if lp_flag is None:
                lp_flag = (tokens[0] == "LP")
                continue
            if tokens[0] == "Dual" and tokens[1] == "solution:":
                var_flag=False
                # It looks like we've just been processing primal
                # variables.
                for (var,val) in tmp:
                    if var == 'ONE_VAR_CONSTANT':
                        continue
                    soln.variable[var] = {"Value" : val, "Id" : len(soln.variable)}
                tmp=[]
                continue
            if len(tokens) < 3:
                print "ERROR", line,tokens
            tmp.append( (tokens[0],eval(tokens[2])) )
        if var_flag:
            for (var,val) in tmp:
                if var == 'ONE_VAR_CONSTANT':
                    continue
                soln.variable[var] = {"Value" : val, "Id" : len(soln.variable)}
        else:
            if (lp_flag is True) and (extract_duals is True):
                for (var,val) in tmp:
                    soln.constraint[var].dual = val
            else:
                for (var,val) in tmp:
                    soln.constraint[var] = val
        INPUT.close()
        #print soln


class MockPICO(PICOSHELL,mockmip.MockMIP):
    """A Mock PICO solver used for testing
    """

    pyutilib.component.core.alias('_mock_pico')

    def __init__(self, **kwds):
        try:
            PICOSHELL.__init__(self,**kwds)
        except pyutilib.common.ApplicationError: #pragma:nocover
            pass                        #pragma:nocover
        mockmip.MockMIP.__init__(self,"pico")

    def available(self, exception_flag=True):
        return PICOSHELL.available(self,exception_flag)

    def create_command_line(self,executable,problem_files):
        command = PICOSHELL.create_command_line(self,executable,problem_files)
        mockmip.MockMIP.create_command_line(self,executable,problem_files)
        return command

    def executable(self):
        return mockmip.MockMIP.executable(self)

    def _execute_command(self,cmd):
        return mockmip.MockMIP._execute_command(self,cmd)
