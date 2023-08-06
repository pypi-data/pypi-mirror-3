#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['GlpsolMIPConverter']

from coopr.opt.base import *

from pyutilib.component.core import *
from pyutilib.component.config import *
from pyutilib.component.executables import *
import pyutilib.subprocess
import pyutilib.common


class GlpsolMIPConverter(ManagedSingletonPlugin):

    implements(IProblemConverter)

    executable = ExtensionPoint(IExternalExecutable)

    def __init__(self,**kwds):
        ManagedSingletonPlugin.__init__(self,**kwds)

    def can_convert(self, from_type, to_type):
        """Returns true if this object supports the specified conversion"""
        #
        # Test if the glpsol executable is available
        #
        if self.executable.service("glpsol") is None:
            return False
        #
        # Return True for specific from/to pairs
        #
        if from_type == ProblemFormat.mod and to_type == ProblemFormat.cpxlp:
            return True
        if from_type == ProblemFormat.mod and to_type == ProblemFormat.mps:
            return True
        return False

    def apply(self, *args, **kwargs):
        """Convert an instance of one type into another"""
        if not isinstance(args[2],basestring):
            raise ConverterError, "Can only apply glpsol to convert file data"
        cmd = self.executable.service("glpsol").get_path()
        if cmd is None:
            raise ConverterError, "The 'glpsol' executable cannot be found"
        cmd = cmd +" --math"
        #
        # MPS->LP conversion is ignored in coverage because it's not being
        #   used; instead, we're using pico_convert for this conversion
        #
        if args[1] == ProblemFormat.mps: #pragma:nocover
            ofile="glpsol.mps"
            cmd = cmd + " --check --wfreemps "+ofile
        elif args[1] == ProblemFormat.cpxlp:
            ofile="glpsol.lp"
            cmd = cmd + " --check --wcpxlp "+ofile
        if len(args[2:]) == 1:
            cmd = cmd+" "+args[2]
        else:
            #
            # Create a temporary model file, since GLPSOL can only
            # handle one input file
            #
            OUTPUT=open("glpsol.mod","w")
            flag=False
            #
            # Read the model file
            #
            INPUT= open(args[2])
            for line in INPUT:
                line = line.strip()
                if line == "data;":
                    raise ConverterError, "Problem composing mathprog model and data files - mathprog file already has data in it!"
                if line != "end;":
                    print >>OUTPUT, line
            INPUT.close()
            print >>OUTPUT, "data;"
            #
            # Read the data files
            #
            for file in args[3:]:
                INPUT= open(file)
                for line in INPUT:
                    line = line.strip()
                    if line != "end;" and line != "data;":
                        print >>OUTPUT, line
                INPUT.close()
                print >>OUTPUT, "end;"
            OUTPUT.close()
            cmd = cmd+" glpsol.mod"
        pyutilib.subprocess.run(cmd)
        if not os.path.exists(ofile):       #pragma:nocover
            raise pyutilib.common.ApplicationError, "Problem launching 'glpsol' to create "+ofile
        if os.path.exists("glpsol.mod"):
            os.remove("glpsol.mod")
        return (ofile,),None # empty variable map
