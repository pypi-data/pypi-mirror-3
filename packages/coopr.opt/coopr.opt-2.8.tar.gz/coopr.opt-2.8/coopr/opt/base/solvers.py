#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['IOptSolver', 'OptSolver', 'SolverFactory']

import os
import sys

# need to do the below for the is_constructed check - just can't yet due to a circular dependency
#from coopr.pyomo.base import Block

from convert import convert_problem
from formats import ResultsFormat, ProblemFormat
import results
from coopr.opt.results import SolverResults, SolverStatus

from pyutilib.enum import Enum
from pyutilib.component.core import *
from pyutilib.component.config import *
import pyutilib.common
import pyutilib.misc
import pyutilib.services
import time


class IOptSolver(Interface):
    """Interface class for creating optimization solvers"""

    def available(self, exception_flag=True):
        """Determine if this optimizer is available."""

    def warm_start_capable(self):
        """ True is the solver can accept a warm-start solution."""

    def solve(self, *args, **kwds):
        """Perform optimization and return an SolverResults object."""

    def reset(self):
        """Reset the state of an optimizer"""

    def set_options(self, istr):
        """Set the options in the optimizer from a string."""


SolverFactory = CreatePluginFactory(IOptSolver)
def __solver_call__(self, _name=None, args=[], **kwds):
    if _name is None:
        return self
    _name=str(_name)
    if ':' in _name:
        _name, subsolver = _name.split(':',1)
    elif 'solver' in kwds:
        subsolver = kwds['solver']
        del kwds['solver']
    else:
        subsolver = None
    opt = None
    if _name in IOptSolver._factory_active:
        opt = PluginFactory(IOptSolver._factory_cls[_name], args, **kwds)
    else:
        mode = kwds.get('solver_io', 'nl')
        if mode is None:
            mode = 'nl'
        #print "HERE", _name, subsolver, mode
        pyutilib.services.register_executable(name=_name)
        if pyutilib.services.registered_executable(_name):
            if mode == 'nl':
                opt = PluginFactory(IOptSolver._factory_cls['_asl'], args, **kwds)
            elif mode == 'os':
                opt = PluginFactory(IOptSolver._factory_cls['_ossolver'], args, **kwds)
            if not opt is None:
                opt.set_options('solver='+_name)
    if not opt is None and not subsolver is None:
        opt.set_options('subsolver='+subsolver)
    #print opt.options
    return opt
pyutilib.misc.add_method(SolverFactory, __solver_call__, name='__call__')


#class OptSolver(ManagedPlugin):
class OptSolver(Plugin):
    """A generic optimization solver"""

    implements(IOptSolver)

    def __init__(self, **kwds):
        """ Constructor """
        #ManagedPlugin.__init__(self,**kwds)
        Plugin.__init__(self,**kwds)
        #
        # The 'type' is the class type of the solver instance
        #
        if "type" in kwds:
            self.type = kwds["type"]
        else:                           #pragma:nocover
            raise PluginError, "Expected option 'type' for OptSolver constructor"
        #
        # The 'name' is either the class type of the solver instance, or a
        # assigned name.
        #
        if "name" in kwds:
            self.name = kwds["name"]
        else:
            self.name = self.type
        if "doc" in kwds:
            self._doc = kwds["doc"]
        else:
            if self.type is None:           # pragma:nocover
                self._doc = ""
            elif self.name == self.type:
                self._doc = "%s OptSolver" % self.name
            else:
                self._doc = "%s OptSolver (type %s)" % (self.name,self.type)
        if False:
            # This was used for the managed plugin
            declare_option("options", cls=DictOption, section=self.name, doc=self._doc, ignore_missing=True)
        else:
            self.options = pyutilib.misc.Options()
        if 'options' in kwds and not kwds['options'] is None:
            for key in kwds['options']:
                setattr(self.options,key,kwds['options'][key])

        # the symbol map is an attribute of the solver plugin only because
        # it is generated in presolve and used to tag results so they are
        # interpretable - basically, it persists across multiple methods.
        self._symbol_map=None
        
        self._problem_format=None
        self._results_format=None
        self._valid_problem_formats=[]
        self._valid_result_formats={}
        self.results_reader=None
        self.problem=None
        self._assert_available=False
        self._report_timing = False # timing statistics are always collected, but optionally reported.
        self.suffixes = [] # a list of the suffixes the user has request be loaded in a solution.

        # We define no capabilities for the generic solver; base classes must override this
        self._capabilities = pyutilib.misc.Options()

    def has_capability(self, cap):
        """
        Returns a boolean value representing whether a solver supports
        a specific feature. Defaults to 'False' if the solver is unaware
        of an option. Expects a string.

        Example:
        print solver.sos1 # prints True if solver supports sos1 constraints,
                          # and False otherwise
        print solver.feature # prints True is solver supports 'feature', and
                             # False otherwise
        """
        if not isinstance(cap, str):
            raise TypeError, "Expected argument to be of type '%s', not " + \
                  "'%s'." % (str(type(str())), str(type(cap)))
        else:
            val = self._capabilities[str(cap)]
            if val is None:
                return False
            else:
                return val

    def available(self, exception_flag=True):
        """ True if the solver is available """
        if self._assert_available:
            return True
        tmp = self.enabled()
        if exception_flag and not tmp:
            raise pyutilib.common.ApplicationError, "OptSolver plugin %s is disabled" % self.name
        return tmp

    def warm_start_capable(self):
        """ True is the solver can accept a warm-start solution """
        return False

    def solve(self, *args, **kwds):
        """ Solve the problem """

        # NOTE: We need to do the following, but this requires the
        #   import of Block from coopr.pyomo.base.  However, this import
        #   yields a circular dependency, which hoses everything.
        #
        # If the inputs are models, then validate that they have been
        # constructed!
        #
        #for arg in args:
        #    if isinstance(arg, Block) is True:
        #        if arg.is_constructed() is False:
        #            raise RuntimeError(
        #                "Attempting to solve model=%s with unconstructed "
        #                "component=%s" % (arg.name, component_name) )

        # ignore the verbosity flag.
        if 'verbose' in kwds:
            del kwds['verbose']

        # we're good to go.
        initial_time = time.time()

        self._presolve(*args, **kwds)
        presolve_completion_time = time.time()

        self._apply_solver()
        solve_completion_time = time.time()

        result = self._postsolve()
        postsolve_completion_time = time.time()

        result._symbol_map = self._symbol_map
        # if you don't do this, you won't be able to delete the instance - because
        # the symbol map holds a reference to the instance! which is fine, as
        # technically the symbol map isn't 'good' past the life of the solve().
        self._symbol_map = None

        if self._report_timing is True:
            print "Presolve time=%0.2f seconds" % (presolve_completion_time-initial_time)
            print "Solve time=%0.2f seconds" % (solve_completion_time - presolve_completion_time)
            print "Postsolve time=%0.2f seconds" % (postsolve_completion_time-solve_completion_time)

        return result

    def _presolve(self, *args, **kwds):
        self._timelimit=None
        self.tee=None
        for key in kwds:
            if key == "pformat":
                self._problem_format=kwds[key]
            elif key == "rformat":
                self._results_format=kwds[key]
            elif key == "logfile":
                self.log_file=kwds[key]
            elif key == "solnfile":
                self.soln_file=kwds[key]
            elif key == "timelimit":
                self._timelimit=kwds[key]
            elif key == "tee":
                self.tee=kwds[key]
            elif key == "options":
                self.set_options(kwds[key])
            elif key == "available":
                self._assert_available=True
            elif key == "suffixes":
                val = kwds[key]
                self.suffixes=kwds[key]
            else:
                raise ValueError, "Unknown option="+key+" for solver="+self.type
        self.available()

        (self._problem_files,self._problem_format,self._symbol_map) = self._convert_problem(args, self._problem_format, self._valid_problem_formats)
        if self._results_format is None:
            self._results_format= self._default_results_format(self._problem_format)
        #
        # Disabling this check for now.  A solver doesn't have just _one_ results format.
        #
        #if self._results_format not in self._valid_result_formats[self._problem_format]:
        #   raise ValueError, "Results format `"+str(self._results_format)+"' cannot be used with problem format `"+str(self._problem_format)+"' in solver "+self.name
        if self._results_format == ResultsFormat.soln:
            self.results_reader = None
        else:
            self.results_reader = results.ReaderFactory(self._results_format)

    def _apply_solver(self):
        """The routine that performs the solve"""
        raise NotImplementedError       #pragma:nocover

    def _postsolve(self):
        """The routine that does solve post-processing"""
        return self.results

    def _convert_problem(self, args, pformat, valid_pformats):
        #
        # If the problem is not None, then we assume that it has already
        # been appropriately defined.  Either it's a string name of the
        # problem we want to solve, or its a functor object that we can
        # evaluate directly.
        #
        if self.problem is not None:
            return (self.problem,ProblemFormat.colin_optproblem,None)
        #
        # Otherwise, we try to convert the object explicitly.
        #
        return convert_problem(args, pformat, valid_pformats, self.has_capability)

    def _default_results_format(self, prob_format):
        """Returns the default results format for different problem
            formats.
        """
        return ResultsFormat.results

    def reset(self):
        """
        Reset the state of the solver
        """
        pass

    def set_options(self, istr):
        istr = istr.strip()
        if istr is '':
            return
        if istr[0] == "'" or istr[0] == '"':
            istr = eval(istr)
        tokens = pyutilib.misc.quote_split('[ ]+',istr)
        for token in tokens:
            index = token.find('=')
            if index is -1:
                raise ValueError, "Solver options must have the form option=value"
            try:
                val = eval(token[(index+1):])
            except:
                val = token[(index+1):]
            setattr(self.options, token[:index], val)
