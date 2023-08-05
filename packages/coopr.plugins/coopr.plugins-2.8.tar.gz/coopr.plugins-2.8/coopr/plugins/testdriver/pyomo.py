#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import os
import os.path
import sys
import re

import pyutilib.autotest
from pyutilib.component.core import *
import pyutilib.services
from pyutilib.misc import Options

import coopr.opt

class PyomoTestDriver(Plugin):

    implements(pyutilib.autotest.ITestDriver)
    alias('coopr.pyomo')

    def setUpClass(self, cls, options):
        try:
            cls.pico_convert =  pyutilib.services.registered_executable("pico_convert")
            cls.pico_convert_available= (not cls.pico_convert is None)
        except pyutilib.common.ApplicationError:
            cls.pico_convert_available=False

    def tearDownClass(self, cls, options):
        pass

    def setUp(self, testcase, options):
        global tmpdir
        tmpdir = os.getcwd()
        os.chdir(options.currdir)
        pyutilib.services.TempfileManager.sequential_files(0)
        pyutilib.services.TempfileManager.tempdir = options.currdir
        #
        try:
            testcase.opt = coopr.opt.SolverFactory(options.solver, options=options.solver_options, solver_io=options.solver_io)
        except Exception, e:
            pass
        if testcase.opt is None or not testcase.opt.available(False):
            err = 'Solver %s is not available' % options.solver
            print err
            testcase.skipTest(err)
        else:
            testcase.opt.suffixes = ['.*']

    def tearDown(self, testcase, options):
        global tmpdir
        pyutilib.services.TempfileManager.clear_tempfiles()
        os.chdir(tmpdir)
        pyutilib.services.TempfileManager.unique_files()

    def pyomo(self, cmd, **kwds):
        import coopr.pyomo.scripting.pyomo as main
        sys.stdout.flush()
        sys.stderr.flush()
        print "Running: pyomo "+cmd
        args = re.split('[ ]+',cmd.strip())
        output = main.run(list(args))
        return output

    def perform_tests(self, testcase, name, options):
        if options.baseline is None:
            possible_baseline = []
            if pyutilib.misc.pyyaml_util.json_available:
                possible_baseline.append('json')
            if pyutilib.misc.pyyaml_util.yaml_available:
                possible_baseline.append('yml')
            baseline = options.problem+'.'+possible_baseline[0]
            for ext in possible_baseline:
                if os.path.exists(options.problem+'.'+ext):
                    baseline = options.problem+'.'+ext
                    break
        else:
            baseline = options.baseline
        if not os.path.exists(baseline):
            print "Missing baseline file: %s" % baseline

        if baseline.lower().endswith('yml') or baseline.lower().endswith('yaml'):
            baseline = pyutilib.misc.load_yaml( pyutilib.misc.extract_subtext( baseline ) )
        else:
            baseline = pyutilib.misc.load_json( pyutilib.misc.extract_subtext( baseline ) )

        # Currently, Pyomo prefers to use YAML to write out solver results
        if pyutilib.misc.pyyaml_util.yaml_available:
            results = pyutilib.misc.load_yaml( pyutilib.misc.extract_subtext( options.root+'.out' ) )
        else:
            results = pyutilib.misc.load_json( pyutilib.misc.extract_subtext( options.root+'.out' ) )
        #
        if options.tolerance is None:
            tol = 1e-7
        else:
            tol = options.tolerance
        #
        if not options.options is None and not options.options.max_memory is None:
            testcase.recordTestData('Maximum memory used', options.options.max_memory)
        pyutilib.misc.compare_repn( baseline, results, tolerance=tol, exact=False)

    def run_test(self, testcase, name, options):
        if options.verbose or options.debug:
            print "Test %s - Running pyomo with options %s" % (name, str(options))
        #
        if options.files is None:
            files = options.problem+'.py'
            if os.path.exists(options.problem+'.dat'):
                files += ' '+options.problem+'.dat'
        else:
            files = options.files
        #
        root = options.solver+'_'+options.problem
        if options.pyomo is None:
            options.pyomo = ''
        if not options.solver_io is None:
            options.pyomo += ' --solver-io='+options.solver_io
        try:
            ans = self.pyomo('%s -w -c --solver=%s --output=%s --save-results=%s %s' % (options.pyomo, options.solver, root+'.log', root+'.out', files))
            if not ans is None:
                options.results = ans.instance.update_results(ans.results)
                options.options = ans.options
            options.root = root
        except Exception, e:
            print "ERROR: Problem solving Pyomo model - "+str(e)
            raise
        self.perform_tests(testcase, name, options)
        #
        os.remove(root+'.out')
        os.remove(root+'.log')
