#
# Unit Tests for util/misc
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+"/../.."
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import coopr.opt
import coopr
import pyutilib.services
from pyutilib.component.core import alias


class TestSolver1(coopr.opt.OptSolver):

    alias('stest1')

    def __init__(self, **kwds):
        kwds['type'] = 'stest_type'
        kwds['doc'] = 'TestSolver1 Documentation'
        coopr.opt.OptSolver.__init__(self,**kwds)

    def enabled(self):
        return False


class OptSolverDebug(unittest.TestCase):

    def setUp(self):
        coopr.opt.SolverFactory.activate('stest1')
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()


    def test_solver_init1(self):
        """
        Verify the processing of 'type', 'name' and 'doc' options
        """
        ans = coopr.opt.SolverFactory("stest1")
        self.assertEqual(type(ans), TestSolver1)
        self.assertEqual(ans._doc, "TestSolver1 Documentation")

        ans = coopr.opt.SolverFactory("stest1", doc="My Doc")
        self.assertEqual(type(ans), TestSolver1)
        self.assertEqual(ans._doc, "TestSolver1 Documentation")

        ans = coopr.opt.SolverFactory("stest1", name="my name")
        self.assertEqual(type(ans), TestSolver1)
        self.assertEqual(ans._doc, "TestSolver1 Documentation")

    def test_solver_init2(self):
        """
        Verify that options can be passed in.
        """
        opt = {}
        opt['a'] = 1
        opt['b'] = "two"
        ans = coopr.opt.SolverFactory("stest1", name="solver_init2", options=opt)
        self.assertEqual(ans.options['a'], opt['a'])
        self.assertEqual(ans.options['b'], opt['b'])

    def test_avail(self):
        ans = coopr.opt.SolverFactory("stest1")
        try:
            ans.available()
            self.fail("Expected exception for 'stest1' solver, which is disabled")
        except pyutilib.common.ApplicationError:
            pass



if __name__ == "__main__":
    unittest.main()
