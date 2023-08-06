#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import os
import re
from coopr.opt.base import *
from coopr.opt.results import *
from coopr.opt.solver import *
import mockmip
import pyutilib.services
import pyutilib.common
import pyutilib.misc
import pyutilib.component.core
import string
import re
import xml.dom.minidom
import time
import logging


class CPLEX(OptSolver):
    """The CPLEX LP/MIP solver
    """

    pyutilib.component.core.alias('cplex', doc='The CPLEX MIP solver')

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
            return SolverFactory('_cplex_shell', **kwds)
        if mode == 'python':
            opt = SolverFactory('_cplex_direct', **kwds)
            if opt is None:
                logging.getLogger('coopr.plugins').error('Python API for CPLEX is not installed')
                return
            return opt
        #
        if mode == 'os':
            opt = SolverFactory('_ossolver', **kwds)
        elif mode == 'nl':
            opt = SolverFactory('_asl', **kwds)
        else:
            logging.getLogger('coopr.plugins').error('Unknown IO type: %s' % mode)
            return
        opt.set_options('solver=cplexamp')
        return opt


class CPLEXSHELL(ILMLicensedSystemCallSolver):
    """Shell interface to the CPLEX LP/MIP solver
    """

    pyutilib.component.core.alias('_cplex_shell', doc='Shell interface to the CPLEX LP/MIP solver')

    def __init__(self, **kwds):
        #
        # Call base class constructor
        #
        kwds['type'] = 'cplex'
        ILMLicensedSystemCallSolver.__init__(self, **kwds)

        # NOTE: eventually both of the following attributes should be migrated to a common base class.
        # is the current solve warm-started? a transient data member to communicate state information
        # across the _presolve, _apply_solver, and _postsolve methods.
        self.warm_start_solve = False
        # related to the above, the temporary name of the MST warm-start file (if any).
        self.warm_start_file_name = None

        #
        # Define valid problem formats and associated results formats
        #
        self._valid_problem_formats=[ProblemFormat.cpxlp, ProblemFormat.mps]
        self._valid_result_formats={}
        self._valid_result_formats[ProblemFormat.cpxlp] = [ResultsFormat.soln]
        self._valid_result_formats[ProblemFormat.mps] = [ResultsFormat.soln]

        # Note: Undefined capabilities default to 'None'
        self._capabilities = pyutilib.misc.Options()
        self._capabilities.linear = True
        self._capabilities.quadratic = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True

    #
    # CPLEX has a simple, easy-to-use warm-start capability.
    #
    def warm_start_capable(self):
        return True

    #
    # write a warm-start file in the CPLEX MST format.
    #
    def warm_start(self, instance):

        def _error_labeler(obj):
            raise KeyError(
                "CPLEX Warm Start Error: instance contains an object, %s, "
                "that is not found in the symbol map.  Does the instance "
                "match the provided symbol map?" % ( obj.name, ))

        from coopr.pyomo.base import Var, VarStatus

        doc = xml.dom.minidom.Document()
        root_element = doc.createElement("CPLEXSolution")
        root_element.setAttribute("version","1.0")
        doc.appendChild(root_element)

        # currently not populated.
        header_element = doc.createElement("header")
        # currently not populated.
        quality_element = doc.createElement("quality")
        # definitely populated!
        variables_element = doc.createElement("variables")

        root_element.appendChild(header_element)
        root_element.appendChild(quality_element)
        root_element.appendChild(variables_element)

        # for each variable in the symbol_map, add a child to the
        # variables element.  Both continuous and discrete are accepted
        # (and required, depending on other options), according to the
        # CPLEX manual.  Note, this assumes that the symbol_map matches
        # the instance...
        output_index = 0
        for block in instance.all_blocks():
            for variable in block.active_components(Var).itervalues():
                for index in variable:
                    var = variable[index]
                    if var.status == VarStatus.unused or var.value is None \
                            or var.fixed:
                        continue
                    name = self._symbol_map.getSymbol(var, _error_labeler)

                    variable_element = doc.createElement("variable")
                    variable_element.setAttribute("name", name)
                    variable_element.setAttribute("index", str(output_index))
                    variable_element.setAttribute("value", str(var.value))
                    variables_element.appendChild(variable_element)
                    output_index = output_index + 1

        mst_file = open(self.warm_start_file_name,'w')
        doc.writexml(mst_file, indent="    ", newl="\n")
        mst_file.close()

    # over-ride presolve to extract the warm-start keyword, if specified.
    def _presolve(self, *args, **kwds):

        # if the first argument is a string (representing a filename),
        # then we don't have an instance => the solver is being applied
        # to a file.
        self.warm_start_solve = kwds.pop( 'warmstart', False )

        # the input argument can currently be one of two things: an instance or a filename.
        # if a filename is provided and a warm-start is indicated, we go ahead and
        # create the temporary file - assuming that the user has already, via some external
        # mechanism, invoked warm_start() with a instance to create the warm start file.
        if (self.warm_start_solve is True) and (isinstance(args[0],basestring) is True):
            pass # we assume the user knows what they are doing...
        elif (self.warm_start_solve is True) and (isinstance(args[0],basestring) is False) and (args[0].has_discrete_variables() is True):
           # assign the name of the warm start file *before* calling the base class
           # presolve - the base class method ends up creating the command line,
           # and the warm start file-name is (obviously) needed there.
           self.warm_start_file_name = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.mst')
        else:
           self.warm_start_file_name = None

        # let the base class handle any remaining keywords/actions.
        ILMLicensedSystemCallSolver._presolve(self, *args, **kwds)

        # NB: we must let the base class presolve run first so that the
        # symbol_map is actually constructed!

        if (len(args) > 0) and (isinstance(args[0],basestring) is False):

            # write the warm-start file - currently only supports MIPs.
            # we only know how to deal with a single problem instance.
            if self.warm_start_solve is True:

                if len(args) != 1:
                    raise ValueError(
                        "CPLEX _presolve method can only handle a single "
                        "problem instance - %s were supplied" % (len(args),))

                if args[0].has_discrete_variables() is True:
                    start_time = time.time()
                    self.warm_start(args[0])
                    end_time = time.time()
                    if self._report_timing is True:
                        print "Warm start write time= %.2f seconds" % (end_time-start_time)

    def executable(self):
        executable = pyutilib.services.registered_executable("cplex")
        if executable is None:
            pyutilib.component.core.PluginGlobals.env().log.error("Could not locate the 'cplex' executable, which is required for solver %s" % self.name)
            self.enable = False
            return None
        return executable.get_path()

    def create_command_line(self,executable,problem_files):

        #
        # Define log file
        # The log file in CPLEX contains the solution trace, but the solver status can be found in the solution file.
        #
        self.log_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.log')

        #
        # Define solution file
        # As indicated above, contains (in XML) both the solution and solver status.
        #
        self.soln_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.sol')

        #
        # Define results file
        #
        if self._results_format is None or self._results_format == ResultsFormat.soln:
            self.results_file = self.soln_file
        elif self._results_format == ResultsFormat.sol:
            self.results_file = self.sol_file

        #
        # Write the CPLEX execution script
        #
        script = "set logfile %s\n" % ( self.log_file, )
        if self._timelimit is not None and self._timelimit > 0.0:
            script += "set timelimit %s\n" % ( self._timelimit, )
        if (self.options.mipgap is not None) and (self.options.mipgap > 0.0):
            script += "set mip tolerances mipgap %s\n" % ( self.options.mipgap, )
        for key in self.options:
            if key == 'relax_integrality' or key == 'mipgap':
                continue
            elif isinstance(self.options[key],basestring) and ' ' in self.options[key]:
                opt = " ".join(key.split('_'))+" "+str(self.options[key])
            else:
                opt = " ".join(key.split('_'))+" "+str(self.options[key])
            script += "set %s\n" % ( opt, )
        script += "read %s\n" % ( problem_files[0], )

        # if we're dealing with an LP, the MST file will be empty.
        if (self.warm_start_solve is True) and (self.warm_start_file_name is not None):
            script += "read %s\n" % ( self.warm_start_file_name, )

        if 'relax_integrality' in self.options:
            script += "change problem lp\n"

        script += "display problem stats\n"
        script += "optimize\n"
        script += "write %s\n" % ( self.soln_file, )
        script += "quit\n"

        # dump the script and warm-start file names for the
        # user if we're keeping files around.
        if self.keepFiles:
            script_fname = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.script')
            tmp = open(script_fname,'w')
            tmp.write(script)
            tmp.close()
            
            print "Solver script file=" + script_fname
            if (self.warm_start_solve is True) and (self.warm_start_file_name is not None):
                print "Solver warm-start file=" + self.warm_start_file_name

        #
        # Define command line
        #
        # JDS: I am not sure why we did this test... mostly because if
        # it ever returned false, 'proc' was never initialized, resulting
        # in an exception.
        #if self._problem_format in [ProblemFormat.cpxlp, ProblemFormat.mps]:
        #    proc = self._timer + " " + self.executable()
        cmd = [self.executable()]
        if self._timer:
            cmd.insert(0, self._timer)
        return pyutilib.misc.Bunch( cmd=cmd, script=script, 
                                    log_file=self.log_file, env=None )

    def process_logfile(self):
        """
        Process logfile
        """
        results = SolverResults()
        results.problem.number_of_variables = None
        results.problem.number_of_nonzeros = None
        #
        # Process logfile
        #
        OUTPUT = open(self.log_file)
        output = "".join(OUTPUT.readlines())
        OUTPUT.close()
        #
        # It is generally useful to know the CPLEX version number for logfile parsing.
        #
        cplex_version = None

        #
        # Parse logfile lines
        #
        for line in output.split("\n"):
            tokens = re.split('[ \t]+',line.strip())
            if len(tokens) > 3 and tokens[0] == "CPLEX" and tokens[1] == "Error":
            # IMPT: See below - cplex can generate an error line and then terminate fine, e.g., in CPLEX 12.1.
            #       To handle these cases, we should be specifying some kind of termination criterion always
            #       in the course of parsing a log file (we aren't doing so currently - just in some conditions).
                results.solver.status=SolverStatus.error
                results.solver.error = " ".join(tokens)
            elif len(tokens) >= 3 and tokens[0] == "ILOG" and tokens[1] == "CPLEX":
                cplex_version = tokens[2].rstrip(',')
            elif len(tokens) >= 3 and tokens[0] == "Variables":
                if results.problem.number_of_variables is None: # CPLEX 11.2 and subsequent versions have two Variables sections in the log file output.
                    results.problem.number_of_variables = int(tokens[2])
            # In CPLEX 11 (and presumably before), there was only a single line output to
            # indicate the constriant count, e.g., "Linear constraints : 16 [Less: 7, Greater: 6, Equal: 3]".
            # In CPLEX 11.2 (or somewhere in between 11 and 11.2 - I haven't bothered to track it down
            # in that detail), there is another instance of this line prefix in the min/max problem statistics
            # block - which we don't care about. In this case, the line looks like: "Linear constraints :" and
            # that's all.
            elif len(tokens) >= 4 and tokens[0] == "Linear" and tokens[1] == "constraints":
                results.problem.number_of_constraints = int(tokens[3])
            elif len(tokens) >= 3 and tokens[0] == "Nonzeros":
                if results.problem.number_of_nonzeros is None: # CPLEX 11.2 and subsequent has two Nonzeros sections.
                    results.problem.number_of_nonzeros = int(tokens[2])
            elif len(tokens) >= 5 and tokens[4] == "MINIMIZE":
                results.problem.sense = ProblemSense.minimize
            elif len(tokens) >= 5 and tokens[4] == "MAXIMIZE":
                results.problem.sense = ProblemSense.maximize
            elif len(tokens) >= 4 and tokens[0] == "Solution" and tokens[1] == "time" and tokens[2] == "=":
                # technically, I'm not sure if this is CPLEX user time or user+system - CPLEX doesn't appear
                # to differentiate, and I'm not sure we can always provide a break-down.
                results.solver.user_time = float(tokens[3])
            elif len(tokens) >= 4 and tokens[0] == "Dual" and tokens[1] == "simplex" and tokens[3] == "Optimal:":
                results.solver.termination_condition = TerminationCondition.optimal
                results.solver.termination_message = ' '.join(tokens)
            elif len(tokens) >= 4 and tokens[0] == "Barrier" and tokens[2] == "Optimal:":
                results.solver.termination_condition = TerminationCondition.optimal
                results.solver.termination_message = ' '.join(tokens)
            elif len(tokens) >= 4 and tokens[0] == "Dual" and tokens[3] == "Infeasible:":
                results.solver.termination_condition = TerminationCondition.infeasible
                results.solver.termination_message = ' '.join(tokens)                
            elif len(tokens) >= 4 and tokens[0] == "MIP" and tokens[2] == "Integer" and tokens[3] == "infeasible.":
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                    results.solver.status = SolverStatus.warning
                else:
                    results.solver.status = SolverStatus.ok
                results.solver.termination_condition = TerminationCondition.infeasible
                results.solver.termination_message = ' '.join(tokens)
            # for the case below, CPLEX sometimes reports "true" optimal (the first case)
            # and other times within-tolerance optimal (the second case).
            elif (len(tokens) >= 4 and tokens[0] == "MIP" and tokens[2] == "Integer" and tokens[3] == "optimal") or \
                 (len(tokens) >= 4 and tokens[0] == "MIP" and tokens[2] == "Integer" and tokens[3] == "optimal,"):
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                    results.solver.status = SolverStatus.warning
                else:
                    results.solver.status = SolverStatus.ok
                results.solver.termination_condition = TerminationCondition.optimal
                results.solver.termination_message = ' '.join(tokens)
            elif len(tokens) >= 3 and tokens[0] == "Presolve" and tokens[2] == "Infeasible.":
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                    results.solver.status = SolverStatus.warning
                else:
                    results.solver.status = SolverStatus.ok
                results.solver.termination_condition = TerminationCondition.infeasible
                results.solver.termination_message = ' '.join(tokens)
            elif (len(tokens) == 6 and tokens[2] == "Integer" and tokens[3] == "infeasible" and tokens[5] == "unbounded.") or (len(tokens) >= 5 and tokens[0] == "Presolve" and tokens[2] == "Unbounded" and tokens[4] == "infeasible."):
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                    results.solver.status = SolverStatus.warning
                else:
                    results.solver.status = SolverStatus.ok
                # It isn't clear whether we can determine if the problem is unbounded from
                # CPLEX's output.
                results.solver.termination_condition = TerminationCondition.unbounded
                results.solver.termination_message = ' '.join(tokens)

        try:
            results.solver.termination_message = pyutilib.misc.yaml_fix(results.solver.termination_message)
        except:
            pass
        return results

    def process_soln_file(self,results):

        # the only suffixes that we extract from CPLEX are
        # constraint duals, constraint slacks, and variable
        # reduced-costs. scan through the solver suffix list
        # and throw an exception if the user has specified
        # any others.
        extract_duals = False
        extract_slacks = False
        extract_reduced_costs = False
        for suffix in self.suffixes:
            flag=False
            if re.match(suffix,"dual"):
                extract_duals = True
                flag=True
            if re.match(suffix,"slack"):
                extract_slacks = True
                flag=True
            if re.match(suffix,"rc"):
                extract_reduced_costs = True
                flag=True
            if not flag:
                raise RuntimeError,"***The CPLEX solver plugin cannot extract solution suffix="+suffix

        lp_solution = False
        if not os.path.exists(self.soln_file):
            return

        soln = Solution()
        soln.objective['__default_objective__'].value=None
        soln_variable = soln.variable # caching for efficiency
        INPUT = open(self.soln_file,"r")
        results.problem.number_of_objectives=1
        mip_problem=False
        for line in INPUT:
            line = line.strip()
            line = line.lstrip('<?/')
            line = line.rstrip('/>?')
            tokens=line.split(' ')

            if tokens[0] == "variable":
                variable_name = None
                variable_value = None
                variable_reduced_cost = None
                variable_status = None
                for i in xrange(1,len(tokens)):
                    field_name =  tokens[i].split('=')[0]
                    field_value = tokens[i].split('=')[1].lstrip("\"").rstrip("\"")
                    if field_name == "name":
                        variable_name = field_value
                    elif field_name == "value":
                        variable_value = field_value
                    elif (extract_reduced_costs is True) and (field_name == "reducedCost"):
                        variable_reduced_cost = field_value
                    elif (extract_reduced_costs is True) and (field_name == "status"):
                        variable_status = field_value

                # skip the "constant-one" variable, used to capture/retain objective offsets in the CPLEX LP format.
                if variable_name != "ONE_VAR_CONSTANT":
                    variable = soln_variable[variable_name] = {"Value" : float(variable_value), "Id" : len(soln_variable)}
                    if (variable_reduced_cost is not None) and (extract_reduced_costs is True):
                        try:
                            variable["Rc"] = float(variable_reduced_cost)
                            if variable_status is not None:
                                if variable_status == "LL":
                                    variable["Lrc"] = float(variable_reduced_cost)
                                else:
                                    variable["Lrc"] = 0.0
                                if variable_status == "UL":
                                    variable["Urc"] = float(variable_reduced_cost)
                                else:
                                    variable["Urc"] = 0.0
                        except:
                            raise ValueError, "Unexpected reduced-cost value="+str(variable_reduced_cost)+" encountered for variable="+variable_name
            elif (tokens[0] == "constraint") and ((extract_duals is True) or (extract_slacks is True)):
                constraint_name = None
                constraint_dual = None
                constaint = None # cache the solution constraint reference, as the getattr is expensive.
                for i in xrange(1,len(tokens)):
                    field_name =  tokens[i].split('=')[0]
                    field_value = tokens[i].split('=')[1].lstrip("\"").rstrip("\"")
                    if field_name == "name":
                        constraint_name = field_value
                        constraint = soln.constraint[constraint_name]
                    elif (extract_duals is True) and (field_name == "dual"): # for LPs
                        # assumes the name field is first.
                        if float(field_value) != 0.0:
                            constraint.dual = float(field_value)
                    elif (extract_slacks is True) and (field_name == "slack"): # for MIPs
                        # assumes the name field is first.
                        if float(field_value) != 0.0:
                            constraint.slack = float(field_value)
            elif tokens[0].startswith("problemName"):
                filename = (string.strip(tokens[0].split('=')[1])).lstrip("\"").rstrip("\"")
                #print "HERE",filename
                results.problem.name = os.path.basename(filename)
                if '.' in results.problem.name:
                    results.problem.name = results.problem.name.split('.')[0]
                tINPUT=open(filename,"r")
                for tline in tINPUT:
                    tline = tline.strip()
                    if tline == "":
                        continue
                    tokens = re.split('[\t ]+',tline)
                    if tokens[0][0] in ['\\', '*']:
                        continue
                    elif tokens[0] == "NAME":
                        results.problem.name = tokens[1]
                    else:
                        sense = tokens[0].lower()
                        if sense in ['max','maximize']:
                            results.problem.sense = ProblemSense.maximize
                        if sense in ['min','minimize']:
                            results.problem.sense = ProblemSense.minimize
                    break
                tINPUT.close()

            elif tokens[0].startswith("objectiveValue"):
                objective_value = (string.strip(tokens[0].split('=')[1])).lstrip("\"").rstrip("\"")
                soln.objective['__default_objective__'].value = float(objective_value)
            elif tokens[0].startswith("solutionStatusValue"):
               pieces = string.split(tokens[0],"=")
               solution_status = eval(pieces[1])
               # solution status = 1 => optimal
               # solution status = 3 => infeasible
               if soln.status == SolutionStatus.unknown:
                  if solution_status == 1:
                    soln.status = SolutionStatus.optimal
                  elif solution_status == 3:
                    soln.status = SolutionStatus.infeasible
                    soln.gap = None                  
                  elif solution_status >= 4: # we are flagging these as "error".
                    soln.status = SolutionStatus.error
                    soln.gap = None
            elif tokens[0].startswith("solutionStatusString"):
                solution_status = (string.strip(" ".join(tokens).split('=')[1])).lstrip("\"").rstrip("\"")
                if solution_status in ["optimal", "integer optimal solution", "integer optimal, tolerance"]:
                    soln.status = SolutionStatus.optimal
                    soln.gap = 0.0
                    results.problem.lower_bound = soln.objective['__default_objective__'].value
                    results.problem.upper_bound = soln.objective['__default_objective__'].value
                    mip_problem=True
                elif solution_status in ["infeasible"]:
                    soln.status = SolutionStatus.infeasible
                    soln.gap = None
            elif tokens[0].startswith("MIPNodes"):
                if mip_problem:
                    n = eval(eval(string.strip(" ".join(tokens).split('=')[1])).lstrip("\"").rstrip("\""))
                    results.solver.statistics.branch_and_bound.number_of_created_subproblems=n
                    results.solver.statistics.branch_and_bound.number_of_bounded_subproblems=n


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
        INPUT.close()

    def _postsolve(self):

        # take care of the annoying (and empty) CPLEX temporary files in the current directory.
        # this approach doesn't seem overly efficient, but python os module functions don't
        # accept regular expression directly.
        filename_list = os.listdir(".")
        for filename in filename_list:
            # CPLEX temporary files come in two flavors - cplex.log and clone*.log.
            # the latter is the case for multi-processor environments.
            # IMPT: trap the possible exception raised by the file not existing.
            #       this can occur in pyro environments where > 1 workers are
            #       running CPLEX, and were started from the same directory.
            #       these logs don't matter anyway (we redirect everything),
            #       and are largely an annoyance.
            try:
                if  re.match('cplex\.log', filename) != None:
                    os.remove(filename)
                elif re.match('clone\d+\.log', filename) != None:
                    os.remove(filename)
            except OSError:
                pass

        # let the base class deal with returning results.
        return ILMLicensedSystemCallSolver._postsolve(self)


class MockCPLEX(CPLEXSHELL,mockmip.MockMIP):
    """A Mock CPLEX solver used for testing
    """

    pyutilib.component.core.alias('_mock_cplex')

    def __init__(self, **kwds):
        try:
            CPLEXSHELL.__init__(self, **kwds)
        except pyutilib.common.ApplicationError: #pragma:nocover
            pass                        #pragma:nocover
        mockmip.MockMIP.__init__(self,"cplex")

    def available(self, exception_flag=True):
        return CPLEXSHELL.available(self,exception_flag)

    def create_command_line(self,executable,problem_files):
        command = CPLEXSHELL.create_command_line(self,executable,problem_files)
        mockmip.MockMIP.create_command_line(self,executable,problem_files)
        return command

    def executable(self):
        return mockmip.MockMIP.executable(self)

    def _execute_command(self,cmd):
        return mockmip.MockMIP._execute_command(self,cmd)


pyutilib.services.register_executable(name="cplex")
pyutilib.services.register_executable(name="cplexamp")

