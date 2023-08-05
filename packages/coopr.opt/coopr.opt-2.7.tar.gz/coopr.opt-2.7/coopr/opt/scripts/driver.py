
import argparse
import coopr.misc.coopr_parser
import os.path
import textwrap
import coopr.opt

def setup_solvers_parser(parser):
    parser.add_argument("--list", dest="summary", action='store_true', default=False,
                        help="list the active solvers")
    parser.add_argument("--options", dest="options", action='store_true', default=False,
                        help="print the solver options that are supported by solvers")

def setup_test_parser(parser):
    parser.add_argument('--csv-file', '--csv', action='store', dest='csv', default=None,
                        help='Save test results to this file in a CSV format')
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", default=False,
                        help="Show debugging information and text generated during tests.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                        help="Show verbose results output.")
    parser.add_argument("solver", metavar="SOLVER", default=None, nargs='*',
                        help="a solver name")

def print_solvers():
    wrapper = textwrap.TextWrapper(replace_whitespace=False)
    print wrapper.fill("The following pre-defined solver interfaces are recognized by Pyomo:")
    print ""
    solver_list = coopr.opt.SolverFactory.services()
    solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
    n = max(map(len, solver_list))
    wrapper = textwrap.TextWrapper(subsequent_indent=' '*(n+9))
    for s in solver_list:
        format = '    %-'+str(n)+'s  %s'
        print wrapper.fill(format % (s , coopr.opt.SolverFactory.doc(s)))
    print ""
    wrapper = textwrap.TextWrapper(subsequent_indent='')
    print wrapper.fill('The default solver is glpk.')
    print ""
    print wrapper.fill('Subsolver options can be specified by with the solver name followed by colon and then the subsolver.  For example, the following specifies that the asl solver will be used:')
    print '   --asl:PICO'
    print wrapper.fill('This indicates that the asl solver will launch the PICO executable to perform optimization.  Currently, no other solver supports this syntax.')


def main_exec(options):
    import coopr.pyomo.check as check
    if options.options:
        print "TODO - print solver options"
    elif options.summary:
        print_solvers()
    else:
        print "No solver action specified."

def test_exec(options):
    try:
        import coopr.data.pyomo
    except ImportError:
        print "Cannot test solvers.  The package coopr.data.pyomo is not installed!"
        return
    coopr.data.pyomo.test_solvers(options)
    
    
#
# Add a subparser for the coopr command
#
setup_solvers_parser(
    coopr.misc.coopr_parser.add_subparser('solvers',
        func=main_exec, 
        help='Print information on Coopr solvers.',
        description='This coopr subcommand is used to print solver information.',
        epilog='Note that the different options are meant to be used exclusively.  Additionally, the solver name is not used when listing all solvers.'
        ))

setup_test_parser(
    coopr.misc.coopr_parser.add_subparser('test-solvers',
        func=test_exec,
        help='Test Coopr solvers',
        description='This coopr subcommand is used to run tests on installed solvers.',
        epilog="""
This Coopr subcommand executes solvers on a variety of test problems that
are defined in the coopr.data.pyomo package.  The default behavior is to
test all available solvers, but the testing can be limited by explicitly
specifying the solvers that are tested.  For example:

  coopr test-solvers glpk cplex

will test only the glpk and cplex solvers.

The configuration file test_solvers.yml in coopr.data.pyomo defines a
series of test suites, each of which specifies a list of solvers that are
tested with a list of problems.  For each solver-problem pair, the Pyomo
problem is created and optimized with the the Coopr solver interface.
The optimization results are then analyzed using a function with the
same name as the test suite (found in the coopr/data/pyomo/plugins
directory).  These functions perform a sequence of checks that compare
the optimization results with baseline data, evaluate the solver return
status, and otherwise verify expected solver behavior.

The default summary is a simple table that describes the percentage of
checks that passed.  The '-v' option can be used to provide a summary
of all checks that failed, which is generally useful for evaluating
solvers.  The '-d' option provides additional detail about all checks
performed (both passed and failed checks).  Additionally, this option
prints information about the optimization process, such as the pyomo
command-line that was executed.""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
)


def main(args=None):
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    parser.set_defaults(func=main_exec)
    ret = parser.parse_args(args)
    ret = ret.func(ret)

