#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


from gurobipy import *
import re
import string

# NOTE: this function / module is independent of Coopr, and only relies on the
#       GUROBI python bindings. consequently, nothing in this function should
#       throw an exception that is expected to be handled by Coopr - it won't be.
#       rather, print an error message and return - the caller will know to look
#       in the logs in case of a failure.

def gurobi_run(model_file, warmstart_file, soln_file, mipgap, options, suffixes):

    # figure out what suffixes we need to extract.
    extract_duals = False
    extract_slacks = False
    extract_reduced_costs = False
    for suffix in suffixes:
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
            print "***The GUROBI solver plugin cannot extract solution suffix="+suffix
            return

    # Load the lp model
    model = read(model_file)

    if model is None:
        print "***The GUROBI solver plugin failed to load the input LP file="+soln_file
        return

    if warmstart_file is not None:
        model.read(warmstart_file)

    # set the mipgap if specified.
    if mipgap is not None:
        model.setParam("MIPGap", mipgap)

    # set all other solver parameters, if specified.
    # GUROBI doesn't throw an exception if an unknown
    # key is specified, so you have to stare at the
    # output to see if it was accepted.
    for key, value in options.iteritems():
        model.setParam(key, value)

    # optimize the model
    model.optimize()

    solver_status = model.getAttr(GRB.Attr.Status)
    return_code = 0
    if (solver_status == GRB.LOADED):
        status = 'aborted'
        message = 'Model is loaded, but no solution information is availale.'
        term_cond = 'unsure'
    elif (solver_status == GRB.OPTIMAL):
        status = 'ok'
        message = 'Model was solved to optimality (subject to tolerances), and an optimal solution is available.'
        term_cond = 'optimal'
    elif (solver_status == GRB.INFEASIBLE):
        status = 'warning'
        message = 'Model was proven to be infeasible.'
        term_cond = 'infeasible'
    elif (solver_status == GRB.INF_OR_UNBD):
        status = 'warning'
        message = 'Problem proven to be infeasible or unbounded.'
        term_cond = 'infeasible' # Coopr doesn't have an analog to "infeasible or unbounded", which is a weird concept anyway.
    elif (solver_status == GRB.UNBOUNDED):
        status = 'warning'
        message = 'Model was proven to be unbounded.'
        term_cond = 'unbounded'
    elif (solver_status == GRB.CUTOFF):
        status = 'aborted'
        message = 'Optimal objective for model was proven to be worse than the value specified in the Cutoff  parameter. No solution information is available.'
        term_cond = 'minFunctionValue'
    elif (solver_status == GRB.ITERATION_LIMIT):
        status = 'aborted'
        message = 'Optimization terminated because the total number of simplex iterations performed exceeded the value specified in the IterationLimit parameter.'
        term_cond = 'maxIterations'
    elif (solver_status == GRB.NODE_LIMIT):
        status = 'aborted'
        message = 'Optimization terminated because the total number of branch-and-cut nodes explored exceeded the value specified in the NodeLimit parameter.'
        term_cond = 'maxEvaluations'
    elif (solver_status == GRB.TIME_LIMIT):
        status = 'aborted'
        message = 'Optimization terminated because the time expended exceeded the value specified in the TimeLimit parameter.'
        term_cond = 'maxTimeLimit'
    elif (solver_status == GRB.SOLUTION_LIMIT):
        status = 'aborted'
        message = 'Optimization terminated because the number of solutions found reached the value specified in the SolutionLimit parameter.'
        term_cond = 'stoppedByLimit'
    elif (solver_status == GRB.INTERRUPTED):
        status = 'aborted'
        message = 'Optimization was terminated by the user.'
        term_cond = 'error'
    elif (solver_status == GRB.NUMERIC):
        status = 'error'
        message = 'Optimization was terminated due to unrecoverable numerical difficulties.'
        term_cond = 'error'
    else:
        status = 'error'
        message = 'Unknown return code from GUROBI model.getAttr(GRB.Attr.Status) call'
        term_cond = 'unsure'

    try:
        obj_value = model.getAttr(GRB.Attr.ObjVal)
    except:
        obj_value = None

    # write the solution file
    solnfile = open(soln_file, "w+")

    # write the information required by results.problem
    print >>solnfile, "section:problem"
    name = model.getAttr(GRB.Attr.ModelName)
    print >>solnfile, "name:",name

    sense = model.getAttr(GRB.Attr.ModelSense)

    # TODO: find out about bounds and fix this with error checking
    # this line fails for some reason so set the value to unknown
    try:
        bound = model.getAttr(GRB.Attr.ObjBound)
    except Exception, e:
        if term_cond == 'optimal':
            bound = obj_value
        else:
            bound = None

    if (sense < 0):
        print >>solnfile, "sense:maximize"
        if bound is None:
            print >>solnfile, "upper_bound:",float('infinity')
        else:
            print >>solnfile, "upper_bound:",bound
    else:
        print >>solnfile, "sense:minimize"
        if bound is None:
            print >>solnfile, "lower_bound:",float('-infinity')
        else:
            print >>solnfile, "lower_bound:",bound

    # TODO: Get the number of objective functions from GUROBI
    n_objs = 1
    print >>solnfile, "number_of_objectives:", n_objs

    cons = model.getConstrs()
    print >>solnfile, "number_of_constraints:",len(cons)

    vars = model.getVars()
    print >>solnfile, "number_of_variables:",len(vars)

    n_binvars = model.getAttr(GRB.Attr.NumBinVars)
    print >>solnfile, "number_of_binary_variables:", n_binvars

    n_intvars = model.getAttr(GRB.Attr.NumIntVars)
    print >>solnfile, "number_of_integer_variables:", n_intvars

    print >>solnfile, "number_of_continuous_variables:", len(vars)-n_intvars

    print >>solnfile, "number_of_nonzeros:",model.getAttr(GRB.Attr.NumNZs)

    # write out the information required by results.solver
    print >>solnfile, "section:solver"

    print >>solnfile, 'status:', status
    print >>solnfile, 'return_code:', return_code
    print >>solnfile, 'message:',message
    print >>solnfile, 'user_time:', model.getAttr(GRB.Attr.Runtime)
    print >>solnfile, 'system_time:', str(0.0)
    print >>solnfile, 'termination_condition:', term_cond
    print >>solnfile, 'termination_message:', message

    is_discrete = False
    if (model.getAttr(GRB.Attr.IsMIP)):
        is_discrete = True

    if (term_cond == 'optimal') or (model.getAttr(GRB.Attr.SolCount) >= 1):
        print >>solnfile, 'section:solution'
        print >>solnfile, 'status:optimal'
        print >>solnfile, 'message:',message
        print >>solnfile, 'objective:',obj_value
        print >>solnfile, 'gap:',0.

        for var in vars:
            print >>solnfile, 'var:',var.getAttr(GRB.Attr.VarName), ":",var.getAttr(GRB.Attr.X)

        if (is_discrete is False) and (extract_reduced_costs is True):
            print "RC=",var.getAttr(GRB.Attr.RC)
            print >>solnfile, 'varrc:',var.getAttr(GRB.Attr.VarName), ":",var.getAttr(GRB.Attr.RC)

        if (is_discrete is False) and (extract_duals is True):
            for con in cons:
               # Pi attributes in Gurobi are the constraint duals
                print >>solnfile, "constraintdual:",con.getAttr(GRB.Attr.ConstrName),":",con.getAttr(GRB.Attr.Pi)

        if (is_discrete is True) and (extract_slacks is True):
            for con in cons:
                print >>solnfile, "constraintslack:",con.getAttr(GRB.Attr.ConstrName),":",con.getAttr(GRB.Attr.Slack)

    solnfile.close()
