import os
import pyutilib.th as unittest
from nose.tools import timed
from pyutilib.misc.pyyaml_util import *
import coopr.pyomo.scripting.util as util
import coopr.plugins
from coopr.pyomo.scripting.util import apply_optimizer
from pyutilib.misc import Options
import pickle
import sys
currdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currdir)
problem_list = ['trivial_model']

def module_available(module):
    try:
        __import__(module)
        return True
    except ImportError:
        return False
def has_python(name):
    if module_available(name):
        return True
    return False

def has_gurobi_lp():
    try:
        gurobi = coopr.plugins.solvers.GUROBI(keepFiles=True)
        available = (not gurobi.executable() is None) and gurobi.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
def has_cplex_lp():
    try:
        cplex = coopr.plugins.solvers.CPLEX(keepFiles=True)
        available = (not cplex.executable() is None) and cplex.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
def has_glpk_lp():
    try:
        glpk = coopr.plugins.solvers.GLPK(keepFiles=True)
        available = (not glpk.executable() is None) and glpk.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
def has_cbc_lp():
    try:
        cbc = coopr.plugins.solvers.CBC(keepFiles=True)
        available = (not cbc.executable() is None) and cbc.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
def has_pico_lp():
    try:
        PICO = coopr.plugins.solvers.PICO(keepFiles=True)
        available = (not PICO.executable() is None) and PICO.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

def has_cplex_nl():
    try:
        cplex = coopr.plugins.solvers.CPLEX(keepFiles=True)
        available = (not cplex.executable() is None) and cplex.available(False)
        asl = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'cplexamp'})
        return available and (not asl.executable() is None) and asl.available(False)
    except pyutilib.common.ApplicationError:
        return False
def has_gurobi_nl():
    try:
        gurobi = coopr.plugins.solvers.GUROBI(keepFiles=True)
        available = (not gurobi.executable() is None) and gurobi.available(False)
        asl = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'gurobi_ampl'})
        return available and (not asl.executable() is None) and asl.available(False)
    except pyutilib.common.ApplicationError:
        return False
def has_ipopt_nl():
    try:
        asl = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'ipopt'})
        return (not asl.executable() is None) and asl.available(False)
    except pyutilib.common.ApplicationError:
        return False

writer_solver = []
if has_python('cplex'):
    writer_solver.append(('python','cplex',True))
else:
    writer_solver.append(('python','cplex',False))

if has_python('gurobipy'):
    writer_solver.append(('python','gurobi',True))
else:
    writer_solver.append(('python','gurobi',False))

if has_python('glpk'):
    writer_solver.append(('python','glpk',True))
else:
    writer_solver.append(('python','glpk',False))
    
if has_cplex_lp():
    writer_solver.append(('lp','cplex',True))
else:
    writer_solver.append(('lp','cplex',False))

if has_gurobi_lp():
    writer_solver.append(('lp','gurobi',True))
else:
    writer_solver.append(('lp','gurobi',False))
    
if has_glpk_lp():
    writer_solver.append(('lp','glpk',True))
else:
    writer_solver.append(('lp','glpk',False))

if has_cplex_nl():
    writer_solver.append(('nl','cplexamp',True))
elif has_gurobi_nl():
    writer_solver.append(('nl','gurobi_ampl',True))
elif has_ipopt_nl():
    writer_solver.append(('nl','ipopt',True))
else:
    writer_solver.append(('nl','ASL',False))

if has_cbc_lp():
    writer_solver.append(('lp','cbc',True))
else:
    writer_solver.append(('lp','cbc',False))
    
if has_pico_lp():
    writer_solver.append(('lp','pico',True))
else:
    writer_solver.append(('lp','pico',False))

def createTestMethod(pName,pickle_which,problem,solver,writer,do_test):

    @unittest.skipUnless(do_test,solver+"_"+writer+" not available")
    def testMethod(obj):
        options = Options()
        options.solver = solver
        options.solver_io = writer
        options.quiet = True

        p = __import__(problem)
        model = p.define_model()
        inst = model.create()

        results, opt = apply_optimizer(options,inst)

        f = open('junk.pickle','w')
        if pickle_which == 'instance':
            inst.load(results)
            pickle.dump(inst,f)
        elif pickle_which == 'results':
            pickle.dump(results,f)
        f.close()

    return testMethod

def assignTests(cls):
    for PROBLEM in problem_list:
        for writer,solver,do_test in writer_solver:
            #for pickle_which in ['instance']:
            for pickle_which in ['instance','results']:
                attrName = "test_pickle_{0}_{1}_{2}_{3}".format(pickle_which,PROBLEM,solver,writer)
                setattr(cls,attrName,createTestMethod(attrName,pickle_which,PROBLEM,solver,writer,do_test))

@unittest.skipIf(writer_solver==[], "Can't find a solver.")
class PickleTest(unittest.TestCase):
    
    @classmethod
    def tearDownClass(self):
        try:
            os.unlink('junk.pickle')
        except Exception:
            pass

assignTests(PickleTest)

if __name__ == "__main__":
    unittest.main()

