#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import logging

from coopr.opt.base import *
from coopr.opt.results import *
from coopr.opt.solver import *

import mockmip
from pyutilib.misc import Options
from pyutilib.component.core import alias
from pyutilib.services import TempfileManager

logger = logging.getLogger('coopr.plugins')

try:
    # import all the glp_* functions
    from gurobipy import *
    gurobi_python_api_exists = True
except ImportError:
    gurobi_python_api_exists = False

GRB_MAX = -1
GRB_MIN = 1

class ModelSOS(object):
    def __init__(self):
        self.sosType = {}
        self.sosName = {}
        self.varnames = {}
        self.weights = {}
        self.block_cntr = 0

    def count_constraint(self,symbol_map,labeler,gurobi_var_map,con,name,level,index=None):

        self.block_cntr += 1
        self.varnames[self.block_cntr] = []
        self.weights[self.block_cntr] = []
        if level == 1:
            self.sosType[self.block_cntr] = GRB.SOS_TYPE1
        elif level == 2:
            self.sosType[self.block_cntr] = GRB.SOS_TYPE2

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
            self.varnames[self.block_cntr].append(gurobi_var_map[symbol_map.getSymbol(var[idx],labeler)])
            # We need to weight each variable
            # For now we just increment a counter
            self.weights[self.block_cntr].append(cntr)
            cntr += 1.0

class gurobi_direct ( OptSolver ):
    """The Gurobi optimization solver (direct API plugin)

 The gurobi_direct plugin offers an API interface to Gurobi.  It requires the
 Python Gurobi API interface (gurobipy) be in Coopr's lib/ directory.  Generally, if you can run Coopr's Python instance, and execute

 >>> import gurobipy
 >>>

 with no errors, then this plugin will be enabled.

 Because of the direct connection with the Gurobi, no temporary files need be
 written or read.  That ostensibly makes this a faster plugin than the file-based
 Gurobi plugin.  However, you will likely not notice any speed up unless you are
 using the GLPK solver with PySP problems (due to the rapid re-solves).

 One downside to the lack of temporary files, is that there is no LP file to
 inspect for clues while debugging a model.  For that, use the 'write' solver
 option:

 $ pyomo model.{py,dat} \
   --solver=gurobi_direct \
   --solver-options  write=/path/to/some/file.lp

 This is a direct interface to Gurobi's Model.write function, the extension of the file is important.  You could, for example, write the file in MPS format:

 $ pyomo model.{py,dat} \
   --solver=gurobi_direct \
   --solver-options  write=/path/to/some/file.mps

    """

    alias('_gurobi_direct', doc='Direct Python interface to the Gurobi optimization solver.')

    def __init__(self, **kwds):
        #
        # Call base class constructor
        #
        kwds['type'] = 'gurobi_direct'
        OptSolver.__init__(self, **kwds)

        self._model = None

        # NOTE: eventually both of the following attributes should be migrated
        # to a common base class.  Is the current solve warm-started?  A
        # transient data member to communicate state information across the
        # _presolve, _apply_solver, and _postsolve methods.
        self.warm_start_solve = False

        # Note: Undefined capabilities default to 'None'
        self._capabilities = Options()
        self._capabilities.linear = True
        self._capabilities.quadratic = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True

    def available(self, exception_flag=True):
        """ True if the solver is available """

        if exception_flag is False:
            return gurobi_python_api_exists
        else:
            if gurobi_python_api_exists is False:
                raise ApplicationError, "No Gurobi <-> Python bindings available - Gurobi direct solver functionality is not available"
            else:
                return True        

    class _numeric_labeler(object):
        def __init__(self):
            self.id = 0
        def __call__(self, obj):
            self.id += 1
            return str(self.id)

    def _populate_gurobi_instance ( self, model ):

        from coopr.pyomo.base import Var, VarStatus, Objective, Constraint, IntegerSet, BooleanSet, SOSConstraint
        from coopr.pyomo.expr import canonical_is_constant

        try:
            grbmodel = Model( name=model.name )
        except Exception, e:
            msg = 'Unable to create Gurobi model.  Have you installed the Python'\
            '\n       bindings for Gurobi?\n\n\tError message: %s'
            raise Exception, msg % e

        labeler = gurobi_direct._numeric_labeler()
        self._symbol_map = SymbolMap(model)

        pyomo_gurobi_variable_map = {} # maps labels to the corresponding Gurobi variable object
        
        all_blocks = model.all_blocks()
        for block in all_blocks:
            for variable_name, variable in block.active_components(Var).iteritems():
                for var_value in variable.itervalues():
                    if (not var_value.active) or (var_value.status is VarStatus.unused) or (var_value.fixed is True):
                        continue
    
                    lb = -GRB.INFINITY
                    ub = GRB.INFINITY
    
                    if var_value.lb is not None:
                        lb = var_value.lb()
                    if var_value.ub is not None:
                        ub = var_value.ub()
    
                    var_value_label = self._symbol_map.getSymbol(var_value, labeler)
    
                    # be sure to impart the integer and binary nature of any variables
                    if isinstance(var_value.domain, IntegerSet):
                        var_type = GRB.INTEGER
                    elif isinstance(var_value.domain, BooleanSet):
                        var_type = GRB.BINARY
                    else:
                        var_type = GRB.CONTINUOUS
    
                    pyomo_gurobi_variable_map[var_value_label] = grbmodel.addVar(lb=lb, \
                                                                                 ub=ub, \
                                                                                 vtype=var_type, \
                                                                                 name=var_value_label)

        grbmodel.update() 

        objective = sorted( model.active_components( Objective ).values() )[0]
        sense = GRB_MAX
        if objective.is_minimizing(): sense = GRB_MIN
        grbmodel.ModelSense = sense
        obj_expr = LinExpr()

        for key in objective:
            expression = objective[ key ].repn
            if canonical_is_constant( expression ):
                msg = "Ignoring objective '%s[%s]' which is constant"
                logger.warning( msg % (str(objective), str(key)) )
                continue

            if 0 in expression: # constant term
                obj_expr.addConstant(expression[0][None])

            if 1 in expression: # first-order terms
                hash_to_variable_map = expression[-1]
                for var_hash, var_coefficient in expression[1].iteritems():
                    label = self._symbol_map.getSymbol(hash_to_variable_map[var_hash], labeler)
                    obj_expr.addTerms(var_coefficient, pyomo_gurobi_variable_map[label])
                    # the coefficients are attached to the model when creating the
                    # variables, below

            if 2 in expression:
                obj_expr = QuadExpr(obj_expr)
                keys = expression[2].keys()
                for var_key in keys:
                    if len(var_key) == 1:
                        index = var_key.keys()[0]
                        label = self._symbol_map.getSymbol(expression[-1][ index ], labeler)
                        coef  = expression[ 2][ var_key ]
                        obj_expr.addTerms(coef, pyomo_gurobi_variable_map[label], pyomo_gurobi_variable_map[label])
                    else:
                        index   = var_key.keys()[0]
                        label_1 = self._symbol_map.getSymbol(expression[-1][ index ], labeler)
                        index   = var_key.keys()[1]
                        label_2 = self._symbol_map.getSymbol(expression[-1][ index ], labeler)
                        coef    = expression[2][ var_key ]
                        obj_expr.addTerms(coeff, pyomo_gurobi_variable_map[label_1], pyomo_gurobi_variable_map[label_2])

        grbmodel.setObjective(obj_expr,sense=sense)       
 
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
                    modelSOS.count_constraint(self._symbol_map,labeler,pyomo_gurobi_variable_map,con, name, level)
                else:
                    # A series of indexed constraints
                    for index in masterIndex:
                        modelSOS.count_constraint(self._symbol_map,labeler,pyomo_gurobi_variable_map,con, name, level, index)
        
        if modelSOS.sosType:
            for key in modelSOS.sosType.iterkeys():
                grbmodel.addSOS(modelSOS.sosType[key], \
                                modelSOS.varnames[key], \
                                modelSOS.weights[key] )
        
        grbmodel.update()
        
        for block in all_blocks:
            for constraint_name, constraint in block.active_components(Constraint).iteritems():
                if constraint.trivial: 
                    continue
    
                for index, constraint_data in constraint.iteritems():
    
                    if not constraint_data.active: 
                        continue
                    elif constraint_data.lower is None and constraint_data.upper is None:
                        continue  # not binding at all, don't bother
    
                    expression = constraint_data.repn
                    if 1 in expression: # first-order terms
    
                        linear_coefs = list()
                        linear_vars = list()
    
                        hash_to_variable_map = expression[-1]
                        for var_hash, var_coefficient in expression[1].iteritems():
                            var = hash_to_variable_map[var_hash]
                            label = self._symbol_map.getSymbol(var, labeler)
                            linear_coefs.append( var_coefficient )
                            linear_vars.append( pyomo_gurobi_variable_map[label] )
    
                        expr = LinExpr( coeffs=linear_coefs, vars=linear_vars )
    
                    constraint_label = self._symbol_map.getSymbol(constraint, labeler)
    
                    offset = 0.0
                    if 0 in constraint_data.repn:
                        offset = constraint_data.repn[0][None]
                    bound = -offset
    
                    if constraint_data._equality:
                        sense = GRB.EQUAL    # Fixed
                        bound = constraint_data.lower() - offset
                        grbmodel.addConstr(
                           lhs=expr, sense=sense, rhs=bound, name=constraint_label )
                    else:
                        sense = GRB.LESS_EQUAL
                        if constraint_data.upper is not None:
                            bound = constraint_data.upper() - offset
                            if bound < float('inf'):
                                grbmodel.addConstr(
                                  lhs=expr,
                                  sense=sense,
                                  rhs=bound,
                                  name='%s_Upper' % constraint_label
                                )
    
                        if constraint_data.lower is not None:
                            bound = constraint_data.lower() - offset
                            if bound > -float('inf'):
                                grbmodel.addConstr(
                                  lhs=bound,
                                  sense=sense,
                                  rhs=expr,
                                  name=constraint_label
                                )

        grbmodel.update()

        self._gurobi_instance = grbmodel
        
        # need to cache the objective label, because the GUROBI python interface doesn't track this.
        self._objective_label = self._symbol_map.getSymbol(objective[None], labeler)

    def warm_start_capable(self):
        msg = "Gurobi has the ability to use warmstart solutions.  However, it "\
              "has not yet been implemented into the Coopr gurobi_direct plugin."
        logger.info( msg )
        return False


    def warm_start(self, instance):
        pass


    def _presolve(self, *args, **kwargs):
        from coopr.pyomo.base.PyomoModel import Model

        self.warm_start_solve = kwargs.pop( 'warmstart', False )
        self.keepFiles = kwargs.pop( 'keepFiles' , False )
        self.tee = kwargs.pop( 'tee', False )

        model = args[0]
        if len(args) != 1:
            msg = "The gurobi_direct plugin method '_presolve' must be supplied "\
                  "a single problem instance - %s were supplied"
            raise ValueError, msg % len(args)
        elif not isinstance(model, Model):
            raise ValueError, "The problem instance supplied to the "            \
                 "gurobi_direct plugin '_presolve' method must be of type 'Model'"

        self._populate_gurobi_instance( model )
        grbmodel = self._gurobi_instance

        if 'write' in self.options:
            fname = self.options.write
            grbmodel.write( fname )

        # Scaffolding in place
        if self.warm_start_solve is True:

            if len(args) != 1:
                msg = "The gurobi_direct _presolve method can only handle a single"\
                      "problem instance - %s were supplied"
                raise ValueError, msg % len(args)

            self.warm_start( model )


    def _apply_solver(self):
        # TODO apply appropriate user-specified parameters

        prob = self._gurobi_instance
        
        if self.tee:
            prob.setParam( 'OutputFlag', self.tee )
        else:
            prob.setParam( 'OutputFlag', 0)
        if self.keepFiles == True:
            log_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.gurobi.log')
            print "Solver log file: " + log_file
            prob.setParam('LogFile', log_file)

        #Options accepted by gurobi (case insensitive):
        #['Cutoff', 'IterationLimit', 'NodeLimit', 'SolutionLimit', 'TimeLimit',
        # 'FeasibilityTol', 'IntFeasTol', 'MarkowitzTol', 'MIPGap', 'MIPGapAbs',
        # 'OptimalityTol', 'PSDTol', 'Method', 'PerturbValue', 'ObjScale', 'ScaleFlag',
        # 'SimplexPricing', 'Quad', 'NormAdjust', 'BarIterLimit', 'BarConvTol',
        # 'BarCorrectors', 'BarOrder', 'Crossover', 'CrossoverBasis', 'BranchDir',
        # 'Heuristics', 'MinRelNodes', 'MIPFocus', 'NodefileStart', 'NodefileDir',
        # 'NodeMethod', 'PumpPasses', 'RINS', 'SolutionNumber', 'SubMIPNodes', 'Symmetry',
        # 'VarBranch', 'Cuts', 'CutPasses', 'CliqueCuts', 'CoverCuts', 'CutAggPasses',
        # 'FlowCoverCuts', 'FlowPathCuts', 'GomoryPasses', 'GUBCoverCuts', 'ImpliedCuts',
        # 'MIPSepCuts', 'MIRCuts', 'NetworkCuts', 'SubMIPCuts', 'ZeroHalfCuts', 'ModKCuts',
        # 'Aggregate', 'AggFill', 'PreDual', 'DisplayInterval', 'IISMethod', 'InfUnbdInfo',
        # 'LogFile', 'PreCrush', 'PreDepRow', 'PreMIQPMethod', 'PrePasses', 'Presolve',
        # 'ResultFile', 'ImproveStartTime', 'ImproveStartGap', 'Threads', 'Dummy', 'OutputFlag']
        for key in self.options:
            prob.setParam( key, self.options[key] )
            
        if 'relax_integrality' in self.options:
            for v in prob.getVars():
                if v.vType != GRB.CONTINUOUS:
                    v.vType = GRB.CONTINUOUS
            prob.update()

        
        # Actually solve the problem.
        prob.optimize()


    def _gurobi_get_solution_status ( self ):
        status = self._gurobi_instance.Status
        if   GRB.OPTIMAL         == status: return SolutionStatus.optimal
        elif GRB.INFEASIBLE      == status: return SolutionStatus.infeasible
        elif GRB.CUTOFF          == status: return SolutionStatus.other
        elif GRB.INF_OR_UNBD     == status: return SolutionStatus.other
        elif GRB.INTERRUPTED     == status: return SolutionStatus.other
        elif GRB.LOADED          == status: return SolutionStatus.other
        elif GRB.SUBOPTIMAL      == status: return SolutionStatus.other
        elif GRB.UNBOUNDED       == status: return SolutionStatus.other
        elif GRB.ITERATION_LIMIT == status: return SolutionStatus.stoppedByLimit
        elif GRB.NODE_LIMIT      == status: return SolutionStatus.stoppedByLimit
        elif GRB.SOLUTION_LIMIT  == status: return SolutionStatus.stoppedByLimit
        elif GRB.TIME_LIMIT      == status: return SolutionStatus.stoppedByLimit
        elif GRB.NUMERIC         == status: return SolutionStatus.error
        raise RuntimeError, 'Unknown solution status returned by Gurobi solver'


    def _postsolve(self):
        gprob = self._gurobi_instance
        pvars = gprob.getVars()
        pcons = gprob.getConstrs()

        results = SolverResults()
        soln = Solution()
        problem = results.problem
        solver  = results.solver

        solver.name = "Gurobi %s.%s%s" % gurobi.version()
        # solver.memory_used =
        # solver.user_time = None
        # solver.system_time = None
        solver.wallclock_time = gprob.Runtime
        # solver.termination_condition = None
        # solver.termination_message = None

        problem.name = gprob.ModelName
        problem.lower_bound = None
        problem.upper_bound = None
        problem.number_of_constraints          = gprob.NumConstrs
        problem.number_of_nonzeros             = gprob.NumNZs
        problem.number_of_variables            = gprob.NumVars
        problem.number_of_binary_variables     = gprob.NumBinVars
        problem.number_of_integer_variables    = gprob.NumIntVars
        problem.number_of_continuous_variables = gprob.NumVars \
                                                - gprob.NumIntVars \
                                                - gprob.NumBinVars
        problem.number_of_objectives = 1
        problem.number_of_solutions = gprob.SolCount

        problem.sense = ProblemSense.minimize
        if problem.sense == GRB_MAX: problem.sense = ProblemSense.maximize

        soln.status = self._gurobi_get_solution_status()

        if soln.status in (SolutionStatus.optimal, SolutionStatus.stoppedByLimit):
            obj_val = gprob.ObjVal
            if problem.sense == ProblemSense.minimize:
                problem.lower_bound = obj_val
                if problem.number_of_binary_variables + problem.number_of_integer_variables == 0:
                    problem.upper_bound = obj_val
            else:
                problem.upper_bound = obj_val
                if problem.number_of_binary_variables + problem.number_of_integer_variables == 0:
                    problem.lower_bound = obj_val

            soln.objective[self._objective_label].value = obj_val

            for var in pvars:
                soln.variable[ var.VarName ] = {"Value" : var.X, "Id" : len(soln.variable) - 1}

            # for con in pcons:
                     # Having an issue correctly getting the constraints
                     # so punting for now
                # soln.constraint[ con.ConstrName ] = con.


        results.solution.insert(soln)

        self.results = results

        # Done with the model object; free up some memory.
        del gprob, self._gurobi_instance

        # let the base class deal with returning results.
        return OptSolver._postsolve(self)


if not gurobi_python_api_exists:
    SolverFactory().deactivate('_gurobi_direct')
    SolverFactory().deactivate('_mock_gurobi_direct')
