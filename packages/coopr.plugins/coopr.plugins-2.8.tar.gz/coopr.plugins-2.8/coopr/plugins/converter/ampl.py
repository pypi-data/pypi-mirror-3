#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['AmplMIPConverter']

from coopr.opt.base import *

from pyutilib.component.core import *
from pyutilib.component.config import *
from pyutilib.component.executables import *
import pyutilib.subprocess
import pyutilib.common


class AmplMIPConverter(ManagedSingletonPlugin):

    implements(IProblemConverter)

    executable = ExtensionPoint(IExternalExecutable)

    def __init__(self,**kwds):
        ManagedSingletonPlugin.__init__(self,**kwds)

    def can_convert(self, from_type, to_type):
        """Returns true if this object supports the specified conversion"""
        #
        # Test if the ampl executable is available
        #
        if self.executable.service("ampl") is None:
            return False
        #
        # Return True for specific from/to pairs
        #
        if from_type == ProblemFormat.mod and to_type == ProblemFormat.nl:
            return True
        if from_type == ProblemFormat.mod and to_type == ProblemFormat.mps:
            return True
        return False

    def apply(self, *args, **kwargs):
        """Convert an instance of one type into another"""
        if not isinstance(args[2],basestring):
            raise ConverterError, "Can only apply ampl to convert file data"
        cmd = self.executable.service("ampl").get_path()
        if cmd is None:
            raise ConverterError, "The 'ampl' executable cannot be found"
        script_filename = pyutilib.services.TempfileManager.create_tempfile(suffix = '.ampl')
        output_filename = pyutilib.services.TempfileManager.create_tempfile(suffix = '.nl')
        script_filename = "tmp.ampl"
        cmd += " " + script_filename
        #
        # Create the AMPL script
        #
        OUTPUT = open(script_filename, 'w')
        print >>OUTPUT, "#"
        print >>OUTPUT, "# AMPL script for converting the following files"
        print >>OUTPUT, "#"
        if len(args[2:]) == 1:
            print >>OUTPUT, 'model '+args[2]+";"
        else:
            print >>OUTPUT, 'model '+args[2]+";"
            print >>OUTPUT, 'data '+args[3]+";"
        abs_ofile = os.path.abspath(output_filename)
        if args[1] == ProblemFormat.nl:
            print >>OUTPUT, 'write b'+abs_ofile[:-3]+";"
        else:
            print >>OUTPUT, 'write m'+abs_ofile[:-3]+";"
        OUTPUT.close()
        #
        # Execute command and cleanup
        #
        output = pyutilib.subprocess.run(cmd)
        if not os.path.exists(output_filename):       #pragma:nocover
            raise pyutilib.common.ApplicationError, "Problem launching 'ampl' to create '%s': %s" % (output_filename, output)
        return (output_filename,),None # empty variable map
