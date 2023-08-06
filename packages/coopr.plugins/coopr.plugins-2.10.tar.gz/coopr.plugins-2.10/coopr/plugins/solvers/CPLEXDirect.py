#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
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

import xml.dom.minidom

import time

try:
    import cplex
    from cplex.exceptions import CplexError
    cplex_import_available=True
except ImportError:
    cplex_import_available=False
    
    
class ModelSOS(object):
    def __init__(self):
        self.sosType = {}
        self.sosName = {}
        self.varnames = {}
        self.weights = {}
        self.block_cntr = 0

    def count_constraint(self,symbol_map,labeler,con,name,level,index=None):

        self.block_cntr += 1
        self.varnames[self.block_cntr] = []
        self.weights[self.block_cntr] = []
        if level == 1:
            self.sosType[self.block_cntr] = cplex.Cplex.SOS.type.SOS1
        elif level == 2:
            self.sosType[self.block_cntr] = cplex.Cplex.SOS.type.SOS2

        # The variable being indexed
        var = con.sos_vars()
        
        if index is None:
            tmpSet = con.sos_set()
            self.sosName[self.block_cntr] = name
        else:
            tmpSet = con.sos_set()[index]
            self.sosName[self.block_cntr] = name+str(index)

        # Get all the variables
        cntr = 1.0
        for idx in tmpSet:
            self.varnames[self.block_cntr].append(symbol_map.getSymbol(var[idx],labeler))
            # We need to weight each variable
            # For now we just increment a counter
            self.weights[self.block_cntr].append(cntr)
            cntr += 1.0


class CPLEXDirect(OptSolver):
    """The CPLEX LP/MIP solver
    """

    pyutilib.component.core.alias('_cplex_direct',  doc='Direct Python interface to the CPLEX LP/MIP solver')

    def __init__(self, **kwds):

        #
        # Call base class constructor
        #
        kwds['type'] = 'cplexdirect'
        OptSolver.__init__(self, **kwds)

        # NOTE: eventually both of the following attributes should be migrated to a common base class.
        # is the current solve warm-started? a transient data member to communicate state information
        # across the _presolve, _apply_solver, and _postsolve methods.
        self.warm_start_solve = False

        # the working problem instance, via CPLEX python constructs.
        self._active_cplex_instance = None

        # Note: Undefined capabilities default to 'None'
        self._capabilities = pyutilib.misc.Options()
        self._capabilities.linear = True
        self._capabilities.quadratic = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True

    def available(self, exception_flag=True):
        """ True if the solver is available """

        if exception_flag is False:
            return cplex_import_available
        else:
            if cplex_import_available is False:
                raise ApplicationError, "No CPLEX <-> Python bindings available - CPLEX direct solver functionality is not available"
            else:
                return True

    class _numeric_labeler(object):
        def __init__(self):
            self.id = 0
        def __call__(self, obj):
            self.id += 1
            return str(self.id)


    #
    # ultimately, this utility should go elsewhere - perhaps on the PyomoModel itself.
    # in the mean time, it is staying here.
    #
    def _hasIntegerVariables(self, instance):

        from coopr.pyomo.base import Var
        from coopr.pyomo.base.set_types import IntegerSet, BooleanSet

        for variable in instance.active_components(Var).values():

            if (isinstance(variable.domain, IntegerSet) is True) or (isinstance(variable.domain, BooleanSet) is True):

                return True

        return False

    #
    # TBD
    #
    def _evaluate_bound(self, exp):

        from coopr.pyomo.base import expr

        if isinstance(exp, expr._IdentityExpression):
            return self._evaluate_bound(exp._args[0])
        elif exp.is_constant():
            return exp()
        else:
            raise ValueError, "ERROR: nonconstant bound: " + str(exp)

    #
    # CPLEX requires objective expressions to be specified via something other than a sparse pair!
    # NOTE: The returned offset is guaranteed to be a float.
    #
    def _encode_constraint_body_linear(self, expression, labeler, as_pairs=False):

        variables = [] # string names of variables
        coefficients = [] # variable coefficients

        pairs = []

        hash_to_variable_map = expression[-1]

        for var_hash, var_coefficient in expression[1].iteritems():

            variable_name = self._symbol_map.getSymbol(hash_to_variable_map[var_hash], labeler)

            if as_pairs is True:
                pairs.append((variable_name, var_coefficient))
            else:
                variables.append(variable_name)
                coefficients.append(var_coefficient)

        offset=0.0
        if 0 in expression:
            offset = expression[0][None]

        if as_pairs is True:
            return pairs, offset
        else:
            expr = cplex.SparsePair(ind=variables, val=coefficients)
            return expr, offset

    #
    #Handle quadratic constraints and objectives
    #
    def _encode_constraint_body_quadratic(self, expression, labeler, as_triples=False, is_obj=1.0):

        variables1 = [] # string names of variables
        variables2 = [] # string names of variables
        coefficients = [] # variable coefficients

        triples = []

        hash_to_variable_map = expression[-1]

        for vars, coeff in expression[2].iteritems():

            if len(vars)==2:
                var1 = self._symbol_map.getSymbol(hash_to_variable_map[vars.keys()[0]], labeler)
                var2 = self._symbol_map.getSymbol(hash_to_variable_map[vars.keys()[1]], labeler)
            else:
                variable_hash_iter = vars.iterkeys()
                var1 = var2  = self._symbol_map.getSymbol(hash_to_variable_map[variable_hash_iter.next()], labeler)

            if as_triples is True:
                triples.append((var1, var2, is_obj*coeff))
            else:
                variables1.append(var1)
                variables2.append(var2)
                coefficients.append(coeff)

        if as_triples is True:
            return triples 
        else:
            expr = cplex.SparseTriple(ind1=variables1,ind2=variables2,val=coefficients)
            return expr


    #
    # method to populate the CPLEX problem instance (interface) from the supplied Pyomo problem instance.
    #
    def _populate_cplex_instance(self, pyomo_instance):

        labeler = CPLEXDirect._numeric_labeler()
        self._symbol_map = SymbolMap(pyomo_instance)

        from coopr.pyomo.base import Var, VarStatus, Objective, Constraint, IntegerSet, BooleanSet, SOSConstraint
        from coopr.pyomo.base.objective import minimize, maximize
        from coopr.pyomo.expr import canonical_is_constant

        # TBD
        quadratic = False
        used_sos_constraints = False
        cplex_instance = None
        try:
            cplex_instance = cplex.Cplex()
        except CplexError, exc:
            print exc
            raise ValueError, "TBD - FAILED TO CREATE CPLEX INSTANCE!"

        # cplex wants the caller to set the problem type, which is (for current
        # purposes) strictly based on variable type counts.
        num_binary_variables = 0
        num_integer_variables = 0
        num_continuous_variables = 0

        # transfer the variables from pyomo to cplex.
        var_names = []
        var_lbs = []
        var_ubs = []
        var_types = []

        all_blocks = pyomo_instance.all_blocks()
        for block in all_blocks:
            for variable in block.active_components(Var).itervalues():
                for ndx in variable:
                    var = variable[ndx]
                    if (not var.active) or (var.status == VarStatus.unused) or var.fixed:
                        continue
                    var_names.append(self._symbol_map.getSymbol( var, labeler ))
                    if var.lb is None:
                        var_lbs.append(-cplex.infinity)
                    else:
                        var_lbs.append(var.lb())
                    if var.ub is None:
                        var_ubs.append(cplex.infinity)
                    else:
                        var_ubs.append(var.ub())
                    if isinstance(variable.domain, IntegerSet):
                        var_types.append(cplex_instance.variables.type.integer)
                        num_integer_variables += 1
                    elif isinstance(variable.domain, BooleanSet):
                        var_types.append(cplex_instance.variables.type.binary)
                        num_binary_variables += 1
                    else:
                        var_types.append(cplex_instance.variables.type.continuous)
                        num_continuous_variables += 1

        cplex_instance.variables.add(names=var_names, lb=var_lbs, ub=var_ubs, types=var_types)
        
        # transfer the constraints.
        expressions = []
        senses = []
        rhss = []
        range_values = []
        names = []

        qexpressions = []
        qlinears = []
        qsenses = []
        qrhss = []
        qnames = []

        for block in all_blocks:
            for constraint in block.active_components(Constraint).itervalues():
                if constraint.trivial:
                    continue

                for cndx in constraint: # TBD: more efficient looping here.
                    con = constraint[cndx]
                    if not con.active:
                        continue

                    # There are conditions, e.g., when fixing variables, under which
                    # a constraint block might be empty.  Ignore these, for both
                    # practical reasons and the fact that the CPLEX LP format
                    # requires a variable in the constraint body.  It is also
                    # possible that the body of the constraint consists of only a
                    # constant, in which case the "variable" of
                    if canonical_is_constant(con.repn):
                        continue

                    name=self._symbol_map.getSymbol(con,labeler)
                    expr=None
                    qexpr=None
                    #Linear constraints
                    if 1 in con.repn:
                        expr, offset = self._encode_constraint_body_linear(con.repn,labeler)

                    #Quadratic constraints
                    if 2 in con.repn:
                        if expr is None:
                            expr = cplex.SparsePair(ind=[0],val=[0.0])
                        quadratic = True

                        qexpr = self._encode_constraint_body_quadratic(con.repn,labeler)
                        qnames.append(name)

                        if con._equality:
                            # equality constraint.
                            qsenses.append('E')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr)
                            qrhss.append(bound)

                        elif con.lower is not None:
                            qsenses.append('G')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr)
                            qrhss.append(bound)

                        else:
                            qsenses.append('L')
                            bound_expr = con.upper
                            bound = self._evaluate_bound(bound_expr)
                            qrhss.append(bound)

                        qlinears.append(expr)
                        qexpressions.append(qexpr)

                    else:
                        names.append(name)
                        expressions.append(expr)

                        if constraint[cndx]._equality:
                            # equality constraint.
                            senses.append('E')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr) - offset
                            rhss.append(bound)
                            range_values.append(0.0)

                        elif (con.lower is not None) and (con.upper is not None):
                            # ranged constraint.
                            senses.append('R')
                            lower_bound_expr = con.lower # TBD - watch the offset - why not subtract?
                            lower_bound = self._evaluate_bound(lower_bound_expr)
                            upper_bound_expr = con.upper # TBD - watch the offset - why not subtract?
                            upper_bound = self._evaluate_bound(upper_bound_expr)
                            rhss.append(lower_bound)
                            range_values.append(upper_bound-lower_bound)

                        elif con.lower is not None:
                            senses.append('G')
                            bound_expr = con.lower
                            bound = self._evaluate_bound(bound_expr) - offset
                            rhss.append(bound)
                            range_values.append(0.0)

                        else:
                            senses.append('L')
                            bound_expr = con.upper
                            bound = self._evaluate_bound(bound_expr) - offset
                            rhss.append(bound)
                            range_values.append(0.0)

        # SOS constraints - largely taken from cpxlp.py so updates there,
        # should be applied here
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders - refer to cpxlp.py
        sosn = self._capabilities.sosn
        sos1 = self._capabilities.sos1
        sos2 = self._capabilities.sos2
        modelSOS = ModelSOS()
        for block in all_blocks:
            sos_con_list = block.active_components(SOSConstraint)
        
            if len(sos_con_list) > 0:
                if not(sos1 or sos2 or sosn):
                    raise Exception, "Solver does not support SOSConstraint declarations"

            for con in sos_con_list.itervalues():
                level = con.sos_level()
                if (level == 1 and not sos1) or (level == 2 and not sos2) or (level > 2 and not sosn):
                    raise Exception, "Solver does not support SOS level %s constraints" % (level,)
                name = self._symbol_map.getSymbol( con, labeler ) 
                masterIndex = con.sos_set_set()
                if None in masterIndex:
                    # A single constraint
                    modelSOS.count_constraint(self._symbol_map,labeler,con, name, level)
                else:
                    # A series of indexed constraints
                    for index in masterIndex:
                        modelSOS.count_constraint(self._symbol_map,labeler,con, name, level, index)
        
        if modelSOS.sosType:
            for key in modelSOS.sosType.iterkeys():
                cplex_instance.SOS.add(type = modelSOS.sosType[key], \
                                       name = modelSOS.sosName[key], \
                                       SOS = [modelSOS.varnames[key], modelSOS.weights[key]] )
            used_sos_constraints = True
        

        # set the problem type based on the variable counts.
        if (quadratic is True):
            if (num_integer_variables > 0) or (num_binary_variables > 0) or (used_sos_constraints):
                cplex_instance.set_problem_type(cplex_instance.problem_type.MIQP)
            else:
                cplex_instance.set_problem_type(cplex_instance.problem_type.QP)
        elif (num_integer_variables > 0) or (num_binary_variables > 0) or (used_sos_constraints):
            cplex_instance.set_problem_type(cplex_instance.problem_type.MILP)
        else:
            cplex_instance.set_problem_type(cplex_instance.problem_type.LP)


        cplex_instance.linear_constraints.add(lin_expr=expressions, senses=senses, rhs=rhss, range_values=range_values, names=names)

        for index in xrange(len(qexpressions)):
            cplex_instance.quadratic_constraints.add(lin_expr=qlinears[index], quad_expr=qexpressions[index], sense=qsenses[index], rhs=qrhss[index], name=qnames[index])
        

        # transfer the objective.
        active_objectives = pyomo_instance.active_components(Objective)
        the_objective = active_objectives[active_objectives.keys()[0]]
        if the_objective.sense == maximize:
            cplex_instance.objective.set_sense(cplex_instance.objective.sense.maximize)
        else:
            cplex_instance.objective.set_sense(cplex_instance.objective.sense.minimize)

        cplex_instance.objective.set_name(the_objective.name)

        self._symbol_map.getSymbol(the_objective[None], labeler)
        self._symbol_map.alias(the_objective[None],'__default_objective__')


        if canonical_is_constant(the_objective[None].repn):
            print ("Warning: Constant objective detected, replacing " + \
                    "with a placeholder to prevent solver failure.")

            cplex_instance.variables.add(lb=[1],ub=[1],names=["ONE_VAR_CONSTANT"])
            objective_expression = [("ONE_VAR_CONSTANT",offset)]
            cplex_instance.objective.set_linear(objective_expression)

        else:
            #Linear terms
            if 1 in the_objective[None].repn:
                objective_expression, offset = self._encode_constraint_body_linear(the_objective[None].repn, labeler, as_pairs=True) # how to deal with indexed objectives?
                if offset != 0:
                    cplex_instance.variables.add(lb=[1],ub=[1],names=["ONE_VAR_CONSTANT"])
                    objective_expression.append(("ONE_VAR_CONSTANT",offset))
                cplex_instance.objective.set_linear(objective_expression)

            if 2 in the_objective[None].repn:
                #Quadratic terms 
                quadratic = True
                objective_expression = self._encode_constraint_body_quadratic(the_objective[None].repn, labeler, as_triples=True, is_obj=2.0) # how to deal with indexed objectives?
                cplex_instance.objective.set_quadratic_coefficients(objective_expression)


        #cplex_instance.write("new.lp")
        self._active_cplex_instance = cplex_instance

    #
    # cplex has a simple, easy-to-use warm-start capability.
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

        labeler = CPLEXDirect._numeric_labeler()
        # the iteration order is identical to that used in generating
        # the cplex instance, so all should be well.
        variable_names = []
        variable_values = []
        for variable in instance.active_components(Var).values():
            for index in variable: # TBD - change iteration style.
                var = variable[index]
                if (var.status == VarStatus.unused) or (var.value is None) \
                        or var.fixed:
                    continue
                name = self._symbol_map.getSymbol(var, _error_labeler)
                variable_names.append(name)
                variable_values.append(var.value)

        self._active_cplex_instance.MIP_starts.add([variable_names, variable_values],
                                                   self._active_cplex_instance.MIP_starts.effort_level.auto)


    # over-ride presolve to extract the warm-start keyword, if specified.
    def _presolve(self, *args, **kwds):
        from coopr.pyomo.base.PyomoModel import Model

        self.tee = kwds.pop( 'tee', False )
        self.keepFiles = kwds.pop( 'keepFiles', False )
        self.warm_start_solve = kwds.pop( 'warmstart', False )

        # Step 1: extract the pyomo instance from the input arguments,
        #         cache it, and create the corresponding (as of now empty)
        #         CPLEX problem instance.
        if len(args) != 1:
            msg = "The CPLEXDirect plugin method '_presolve' must be supplied "\
                  "a single problem instance - %s were supplied"
            raise ValueError, msg % len(args)

        model = args[ 0 ]
        if not isinstance(model, Model):
            msg = "The problem instance supplied to the CPLEXDirect plugin " \
                  "method '_presolve' must be of type 'Model' - "\
                  "interface does not currently support file names"
            raise ValueError, msg

        # TBD-document.
        self._populate_cplex_instance(model)

        if 'write' in self.options:
            fname = self.options.write
            self._active_cplex_instance.write(fname)
        
        # if the first argument is a string (representing a filename),
        # then we don't have an instance => the solver is being applied
        # to a file.

        # FIXME: This appears to be a bogus test: we raise an exception
        # above if len(args) != 1 or type(args[0]) != Model
        if (len(args) > 0) and not isinstance(model,basestring):

            # write the warm-start file - currently only supports MIPs.
            # we only know how to deal with a single problem instance.
            if self.warm_start_solve is True:

                if len(args) != 1:
                    msg = "CPLEX _presolve method can only handle a single " \
                          "problem instance - %s were supplied"
                    raise ValueError, msg % len(args)

                if self._hasIntegerVariables(model) is True:
                    start_time = time.time()
                    self.warm_start(model)
                    end_time = time.time()
                    if self._report_timing is True:
                        print "Warm start write time=%.2f seconds" % (end_time-start_time)

    #
    # TBD
    #
    def _apply_solver(self):

        # set up all user-specified parameters.
        if (self.options.mipgap is not None) and (self.options.mipgap > 0.0):
            self._active_cplex_instance.parameters.mip.tolerances.mipgap.set(self.options.mipgap)

        for key in self.options:
            if key == 'relax_integrality' or key == 'mipgap' or key == 'write':
                continue
            else:
                opt_cmd = self._active_cplex_instance.parameters
                key_pieces = key.split('_')
                for key_piece in key_pieces:
                    opt_cmd = getattr(opt_cmd,key_piece)
                opt_cmd.set(self.options[key])
                
        if 'relax_integrality' in self.options:
            self._active_cplex_instance.set_problem_type(self._active_cplex_instance.problem_type.LP)
        
        # and kick off the solve.
        if self.tee == True:
            #Should this use pyutilib's tee_io? I couldn't find where
            #other solvers set output using tee=True/False
            from sys import stdout
            self._active_cplex_instance.set_results_stream(stdout)
        elif self.keepFiles == True:
            log_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.log')
            print "Solver log file: " + log_file
            self._active_cplex_instance.set_results_stream(log_file)
            #Not sure why the following doesn't work. As a result, it's either stream output
            #or write a logfile, but not both.
            #self._active_cplex_instance.set_log_stream(log_file)
        else:
            self._active_cplex_instance.set_results_stream(None)
        self._active_cplex_instance.solve()

    def _postsolve(self):

        instance = self._active_cplex_instance

        results = SolverResults()
        results.problem.name = instance.get_problem_name()
        results.problem.lower_bound = None
        results.problem.upper_bound = None
        results.problem.number_of_variables = None
        results.problem.number_of_constraints = None
        results.problem.number_of_nonzeros = None
        results.problem.number_of_binary_variables = None
        results.problem.number_of_integer_variables = None
        results.problem.number_of_continuous_variables = None
        results.problem.number_of_objectives = 1

        results.solver.name = "CPLEX "+instance.get_version()
#        results.solver.status = None
        results.solver.return_code = None
        results.solver.message = None
        results.solver.user_time = None
        results.solver.system_time = None
        results.solver.wallclock_time = None
        results.solver.termination_condition = None
        results.solver.termination_message = None

        soln = Solution()

        #Get solution status -- for now, if CPLEX returns > 4, mark as an error
        soln_status = instance.solution.get_status()
        if soln_status == 1:
            soln.status = SolutionStatus.optimal
        elif soln_status == 2:
            soln.status = SolutionStatus.unbounded
        elif soln_status == 3:
            soln.status = SolutionStatus.infeasible
        else:
            soln.status = SolutionStatus.error

        #Only try to get objective and variable values if a solution exists
        soln_type = instance.solution.get_solution_type()
        if soln_type > 0:
            soln.objective['__default_objective__'].value = instance.solution.get_objective_value()
            num_variables = instance.variables.get_num()
            variable_names = instance.variables.get_names()
            variable_values = instance.solution.get_values()
            for i in range(0,num_variables):
                variable_name = variable_names[i]
                soln.variable[variable_name] = {"Value" : variable_values[i], "Id" : len(soln.variable)}

        results.solution.insert(soln)
        #print type(instance),dir(instance.objective)

        self.results = results

        # don't know if any of this is necessary!

        # take care of the annoying (and empty) CPLEX temporary files in
        # the current directory.  this approach doesn't seem overly
        # efficient, but python os module functions don't accept regular
        # expression directly.
        filename_list = os.listdir(".")
        clone_re = re.compile('clone\d+\.log')
        for filename in filename_list:
            # CPLEX temporary files come in two flavors - cplex.log and
            # clone*.log.  the latter is the case for multi-processor
            # environments.
            #
            # IMPT: trap the possible exception raised by the file not existing.
            #       this can occur in pyro environments where > 1 workers are
            #       running CPLEX, and were started from the same directory.
            #       these logs don't matter anyway (we redirect everything),
            #       and are largely an annoyance.
            try:
                if filename == 'cplex.log':
                    os.remove(filename)
                elif clone_re.match(filename):
                    os.remove(filename)
            except OSError:
                pass

        # let the base class deal with returning results.
        return OptSolver._postsolve(self)


if cplex_import_available is False:
    SolverFactory().deactivate('_cplex_direct')
    SolverFactory().deactivate('_mock_cplexdirect')
