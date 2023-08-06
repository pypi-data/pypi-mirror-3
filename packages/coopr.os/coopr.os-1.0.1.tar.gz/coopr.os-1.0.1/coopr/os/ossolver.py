#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from coopr.opt.base import ProblemFormat, ResultsFormat
from coopr.opt.solver import SystemCallSolver
from pyutilib.component.core import alias
from pyutilib.misc import Bunch
from pyutilib.services import register_executable, registered_executable
from pyutilib.services import TempfileManager

create_tempfile = TempfileManager.create_tempfile

class OSSolver(SystemCallSolver):
    """The Optimization Systems solver."""

    alias('os', doc='An interface to a OS solver service')

    def __init__ (self, **kwargs):
        #
        # Call base constructor
        #
        kwargs['type'] = 'os'
        SystemCallSolver.__init__( self, **kwargs )
        #
        # Valid problem formats, and valid results for each format
        #
        self._valid_problem_formats = [ ProblemFormat.osil ]
        self._valid_result_formats  = { ProblemFormat.osil : [ResultsFormat.osrl] }

    def executable(self):
        executable = registered_executable('OSSolverService')
        if executable is None:
            pyutilib.component.core.PluginGlobals.env().log.error("Could not locate the OSSolverService executable, which is required for solver %s" % self.name)
            self.enable = False
            return None
        return executable.get_path()

    def create_command_line(self, executable, problem_files):
        #
        # Define log file
        #
        if self.log_file is None:
            self.log_file = TempfileManager.create_tempfile(suffix="_os.log")
        fname = problem_files[0]
        self.results_file = problem_files[0]+'.osrl'
        #
        options = []
        for key in self.options:
            if key == 'solver':
                continue
            elif isinstance(self.options[key],basestring) and ' ' in self.options[key]:
                opt.append('-'+key+" \""+str(self.options[key])+"\"")
            elif key == 'subsolver':
                opt.append("-solver "+str(self.options[key]))
            else:
                opt.append('-'+key+" "+str(self.options[key]))
        #
        options = ' '.join( options )
        proc = self._timer + " " + executable + " -osil " + problem_files[0] + " -osrl " + self.results_file + ' ' + options
        return Bunch(cmd=proc, log_file=None, env=None)

    def _default_results_format(self, prob_format):
        return ResultsFormat.osrl


register_executable(name='OSSolverService')
