#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import gc         # garbage collection control.
import os
import pickle
import pstats     # for profiling
import sys
import time
import traceback

from optparse import OptionParser

try:
    import cProfile as profile
except ImportError:
    import profile

from coopr.opt.base import SolverFactory
from coopr.pysp.scenariotree import *

from pyutilib.misc import import_file
from pyutilib.services import TempfileManager

import Pyro.core
import Pyro.naming
from Pyro.errors import PyroError, NamingError

from phinit import *
from phutils import *
from phobjective import *

import pyutilib.pyro

# IMPT: HOW DOES THE TASK WORKER KNOW WHAT QUEUE TO REQUEST/PING? WE NEED TO OVER-RIDE THIS METHOD, OR ASK FOR AN OF-ANY (OR CHANGE IT EXPLICITLY)

class PHSolverServer(pyutilib.pyro.TaskWorker):

    def __init__(self, **kwds):

        pyutilib.pyro.TaskWorker.__init__(self)

        self._instances = kwds.get("scenario_instances", None) # a map from scenario name to pyomo model instance
        self._scenario_tree = kwds.get("scenario_tree", None)
        self._bundle_name = kwds.get("bundle_name", None)

        self._solver = kwds.get("solver", None)
        self._solver_type = kwds.get("solver_type", None)

        self._output_solver_logs = kwds.get("output_solver_logs", False)

        # we can presently only handle an individual scenario or a single bundle of scenarios.
        if (self._bundle_name is None) and (len(self._instances) != 1):
           raise RuntimeError, "PH solver servers are currently limited to handling solve requests for a single scenario / bundle."

        # TBD - validate presence of (some of the) non-None components above

        # the TaskWorker base uses the "type" option to determine the name
        # of the queue from which to request work, via the dispatch server.
        if self._bundle_name is not None:
            self.type = self._bundle_name
        else:
            scenario_name = self._instances.keys()[0]
            self.type = scenario_name

        # create the bundle extensive form, if bundling.
        if self._bundle_name is not None:
            self._bundle_scenario_tree = self._scenario_tree.get_bundle(self._bundle_name)._scenario_tree

            # WARNING: THIS IS A PURE HACK - WE REALLY NEED TO CALL THIS WHEN WE CONSTRUCT THE BUNDLE SCENARIO TREE.
            #          AS IT STANDS, THIS MUST BE DONE BEFORE CREATING THE EF INSTANCE.
            self._bundle_scenario_tree.defineVariableIndexSets(self._instances)
    
            # create the bundle EF instance, and cache the original EF objective.
            self._bundle_ef_instance = create_ef_instance(self._bundle_scenario_tree, self._instances, verbose_output=False) # don't generate output, because it because comparison of log files impossible due to asychronicity
            bundle_ef_objectives = self._bundle_ef_instance.active_components(Objective)
            objective_name = bundle_ef_objectives.keys()[0]
            bundle_ef_objective = bundle_ef_objectives[objective_name]            
            self._original_bundle_objective = bundle_ef_objective._data[None].expr

        # the objective functions are modified throughout the course of PH iterations.
        # save the original, as a baseline to modify in subsequent iterations. reserve
        # the original objectives, for subsequent modification.
        self._original_objective_expression = {}
        for instance_name, instance in self._instances.items():
            objective_name = instance.active_components(Objective).keys()[0]
            expr = instance.active_components(Objective)[objective_name]._data[None].expr
            if isinstance(expr, Expression) is False:
                expr = _IdentityExpression(expr)
            self._original_objective_expression[instance_name] = expr

        # TBD: A bit hack-ish - revisit
        self._instance_ph_linear_expressions = {}
        self._instance_ph_quadratic_expressions = {}

        # the server is in one of two modes - solve the baseline instances, or
        # those augmented with the PH penalty terms. default is standard.
        # NOTE: This is currently a global flag for all scenarios handled
        #       by this server - easy enough to extend if we want.
        self._solving_standard_objective = True

        # as occurs in the main PH routine, track which components - if any - need to
        # be pre-processed prior to the next invocation of the solve() method.
        self._instance_objectives_modified = False
        self._instance_constraints_modified = False
        self._instance_variables_fixed = False

    def form_standard_objective(self, scenario_name, verbose):

        if verbose is True:
           print "Received request to enable standard objective for scenario="+scenario_name
        if verbose is True:
            print "Forming standard objective function"           

        form_standard_objective(scenario_name, scenario_instance, self._original_objective_expression[scenario_name], self._scenario_tree)           
        self._solving_standard_objective = True
        self._instance_objectives_modified = True

    def form_ph_objective(self, scenario_name, verbose):

        if verbose is True:
            print "Received request to enable PH objective for scenario="+scenario_name

        scenario_instance = self._instances[scenario_name]            

        new_lin_terms, new_quad_terms = form_ph_objective(scenario_name, scenario_instance, \
                                                          self._original_objective_expression[scenario_name], self._scenario_tree, \
                                                          False, False, False)

        self._instance_ph_linear_expressions[scenario_name] = new_lin_terms
        self._instance_ph_quadratic_expressions[scenario_name] = new_quad_terms      

        if verbose is True:
            print "Forming PH objective function"                  

        self._solving_standard_objective = False
        self._instance_objectives_modified = True

    def solve(self, object_name, verbose):

      if verbose is True:
          if self._bundle_name is not None:
              print "Received request to solve scenario bundle="+object_name
          else:
              print "Received request to solve scenario instance="+object_name

      # preprocess all scenario instances as needed - if bundling, we take care of the specifics below.
      for scenario_name, scenario_instance in self._instances.iteritems():
          preprocess_scenario_instance(scenario_instance, self._instance_variables_fixed, self._instance_constraints_modified, self._instance_objectives_modified, self._solver_type)

      self._instance_variables_fixed = False
      self._instance_constraints_modified = False
      self._instance_objectives_modified = False

      solve_method_result = None

      if self._bundle_name is not None:

          if object_name != self._bundle_name:
              print "Requested scenario bundle to solve not known to PH solver server!"
              return None

          if self._solving_standard_objective is False:
              
              # restore the original EF objective.
              bundle_ef_objectives = self._bundle_ef_instance.active_components(Objective)
              objective_name = bundle_ef_objectives.keys()[0]
              bundle_ef_objective = bundle_ef_objectives[objective_name]
              bundle_ef_objective._data[None].expr = self._original_bundle_objective

              # augment the EF objective with the PH penalty terms for each composite scenario.
              scenario_bundle = self._scenario_tree.get_bundle(self._bundle_name)
              for scenario_name in scenario_bundle._scenario_names:
                 scenario = self._scenario_tree.get_scenario(scenario_name)
                 new_lin_terms = self._instance_ph_linear_expressions[scenario_name] # TBD - don't need to split linear and quadratic!
                 new_quad_terms = self._instance_ph_quadratic_expressions[scenario_name]
                 scenario = self._scenario_tree._scenario_map[scenario_name]
                 # TBD: THIS SHOULD NOT HAVE TO BE DONE EACH ITERATION - THE OBJECTIVE STRUCTURE DOES NOT CHANGE, AND THE LINEARIZATION 
                 #      CONSTRAINTS ARE ON THE SCENARIO INSTANCES.
                 bundle_ef_objective._data[None].expr += (scenario._probability / scenario_bundle._probability) * (new_lin_terms)
                 bundle_ef_objective._data[None].expr += (scenario._probability / scenario_bundle._probability) * (new_quad_terms)

              # TBD: JUST PREPROCESS OBJECTIVE - NOT THE WHOLE EF INSTANCE.
              self._bundle_ef_instance.preprocess()                 

          results = self._solver.solve(self._bundle_ef_instance, tee=self._output_solver_logs)

          if verbose is True:
              print "Successfully solved scenario bundle="+object_name      

          # TBD: We probably don't want to crater the solver server.
          if len(results.solution) == 0:
              results.write()
              raise RuntimeError, "Solve failed for bundle="+object_name+"; no solutions generated"          

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          self._bundle_ef_instance.load(results)

          if verbose is True:
              print "Successfully loaded solution for bundle="+object_name            

          result = {}
          for scenario_name, scenario_instance in self._instances.iteritems():
              # extract the variable values into one big dictionary - one for each instance.
              variable_values = {}
              for variable_name, variable in scenario_instance.active_components(Var).iteritems():
                  variable_values[variable_name] = variable.extract_values()
              result[scenario_name] = variable_values

          solve_method_result = result

      else:

          if object_name not in self._instances:
              print "Requested instance to solve not in PH solver server instance collection!"
              return None

          scenario_instance = self._instances[object_name]

          # IMPT: You have to re-presolve, as the simple presolver collects the linear terms together. If you
          # don't do this, you won't see any chance in the output files as you vary the problem parameters!
          # ditto for instance fixing!
          scenario_instance.preprocess()

          results = self._solver.solve(scenario_instance, tee=self._output_solver_logs)

          if verbose is True:
              print "Successfully solved scenario instance="+object_name      

          # TBD: We probably don't want to crater the solver server.
          if len(results.solution) == 0:
              results.write()
              raise RuntimeError, "Solve failed for scenario="+object_name+"; no solutions generated"          

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          scenario_instance.load(results)

          if verbose is True:
              print "Successfully loaded solution for scenario="+object_name            

          # extract the variable values into one big dictionary.
          variable_values = {}
          for variable_name, variable in scenario_instance.active_components(Var).iteritems():
              variable_values[variable_name] = variable.extract_values()

          solve_method_result = variable_values

      # set up preprocessing expectations for the next round - by now, we are guaranteed to
      # have generated the ampl representation via a prior write invocation.
      # TBD: by default, assume we are *not* going to re-generate the AMPL representations within
      #      the NL writer - self._preprocess_scenario_instances() may over-ride these values as needed.
      if (self._solver_type == "asl") or (self._solver_type == "ipopt"):
           for scenario_name, scenario_instance in self._instances.iteritems():
               # this is kludgy until we make workflows explicit in Coopr - the NL writer combines writing and
               # preprocessing, so all we can do is tag the instance with an appropriate attribute.
               setattr(scenario_instance, "gen_obj_ampl_repn", False)
               setattr(scenario_instance, "gen_con_ampl_repn", False)

      return solve_method_result

    #
    # udpating weights and averages only applies to scenarios - not bundles.
    #
    def update_weights_and_averages(self, scenario_name, new_weights, new_averages, verbose):

        if verbose is True:
            print "Received request to update weights and averages for scenario="+scenario_name

        # if you have new weights and averages, instance objectives will have to be preprocessed
        self._instance_objectives_modified = True

        if scenario_name not in self._instances:
            print "ERROR: Received request to update weights for instance not in PH solver server instance collection!"
            return None
        scenario_instance = self._instances[scenario_name]

        for weight_parameter_name, weight_update in new_weights.iteritems():

            instance_weight_parameter = getattr(scenario_instance, weight_parameter_name)

            for index, new_value in weight_update.iteritems():
                instance_weight_parameter[index] = new_value

        # IMPT: The PHAVG and PHXBAR parameters are distinct - but the latter is the
        #       most important, as it is used in the objective. We currently just
        #       mirror the average into xbar - this will not work for operator splitting.
        for average_parameter_name, average_update in new_averages.iteritems():

            xbar_parameter_name = "PHXBAR_"+average_parameter_name[6:]

            instance_average_parameter = getattr(scenario_instance, average_parameter_name)
            instance_xbar_parameter = getattr(scenario_instance, xbar_parameter_name)            

            for index, new_value in average_update.iteritems():
                instance_average_parameter[index] = new_value
                instance_xbar_parameter[index] = new_value

    #
    # udpating rhos is only applicable to scenarios.
    #
    def update_rhos(self, scenario_name, new_rhos, verbose):

        if verbose is True:
            print "Received request to update rhos for scenario="+scenario_name

        # if you have new rhos, instance objectives will have to be preprocessed
        self._instance_objectives_modified = True

        if scenario_name not in self._instances:
            print "ERROR: Received request to update rhos for instance not in PH solver server instance collection!"
            return None
        scenario_instance = self._instances[scenario_name]

        for rho_parameter_name, rho_update in new_rhos.iteritems():

            instance_rho_parameter = getattr(scenario_instance, rho_parameter_name)

            for index, new_value in rho_update.iteritems():
                instance_rho_parameter[index] = new_value

    #
    # udpating tree node statistics is bundle versus scenario agnostic.
    #

    def update_tree_node_statistics(self, scenario_name, new_node_minimums, new_node_maximums, verbose):

        if verbose is True:
            if self._bundle_name is not None:
                print "Received request to update tree node statistics for bundle="+self._bundle_name
            else:
                print "Received request to update tree node statistics for scenario="+scenario_name

        for tree_node_name, tree_node_minimums in new_node_minimums.items():

            tree_node = self._scenario_tree._tree_node_map[tree_node_name]
            tree_node._minimums = tree_node_minimums

        for tree_node_name, tree_node_maximums in new_node_maximums.items():

            tree_node = self._scenario_tree._tree_node_map[tree_node_name]
            tree_node._maximums = tree_node_maximums

    def process(self, data):

        result = None
        # TBD: The data actions should really be the enum type associated with the PH solver server.
        if data.action == "solve":
           result = self.solve(data.name, data.verbose)
        elif data.action == "form_ph_objective":
           if self._bundle_name is not None:
               for scenario in self._bundle_scenario_tree._scenarios:
                   self.form_ph_objective(scenario._name, data.verbose)                   
           else:
               self.form_ph_objective(data.name, data.verbose)
           result = True
        elif data.action == "load_rhos":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in self._instances.iteritems():
                   self.update_rhos(scenario_name, data.new_rhos[scenario_name], data.verbose)               
           else:
               self.update_rhos(data.name, data.new_rhos, data.verbose)
           result = True
        elif data.action == "load_weights_and_averages":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in self._instances.iteritems():
                   self.update_weights_and_averages(scenario_name, data.new_weights[scenario_name], data.new_averages[scenario_name], data.verbose)
           else:
               self.update_weights_and_averages(data.name, data.new_weights, data.new_averages, data.verbose)
           result = True
        elif data.action == "load_tree_node_stats":
           self.update_tree_node_statistics(data.name, data.new_mins, data.new_maxs, data.verbose)
           result = True
        else:
           raise RuntimeError, "ERROR: Unknown action="+str(data.action)+" received by PH solver server"

        # a bit goofy - the Coopr Pyro infrastructure 
        return pickle.dumps(result)

#
# utility method to construct an option parser for ph arguments, to be
# supplied as an argument to the runph method.
#

def construct_options_parser(usage_string):

    solver_list = SolverFactory.services()
    solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
    solver_help = \
    "Specify the solver with which to solve scenario sub-problems.  The "      \
    "following solver types are currently supported: %s; Default: cplex"
    solver_help %= ', '.join( solver_list )

    parser = OptionParser()
    parser.add_option("--verbose",
                      help="Generate verbose output for both initialization and execution. Default is False.",
                      action="store_true",
                      dest="verbose",
                      default=False)
    parser.add_option("--scenario",
                      help="Specify a scenario that this server is responsible for solving. IMPT: The --scenario and --bundle options are mutually exclusive.",
                      action="append",
                      dest="scenarios",
                      default=[])
    parser.add_option("--bundle",
                      help="Specify a bundle that this server is responsible for solving. IMPT: The --scenario and --bundle options are mutually exclusive.",
                      action="store",
                      dest="bundle",
                      default=None)
    parser.add_option("--all-scenarios",
                      help="Indicate that the server is responsible for solving all scenarios",
                      action="store_true",
                      dest="all_scenarios",
                      default=False)
    parser.add_option('--scenario-bundle-specification',
                      help="The name of the scenario bundling specification to be used when executing Progressive Hedging. Default is None, indicating no bundling is employed. If the specified name ends with a .dat suffix, the argument is interpreted as a filename. Otherwise, the name is interpreted as a file in the instance directory, constructed by adding the .dat suffix automatically",
                      action="store",
                      dest="scenario_bundle_specification",
                      default=None)
    parser.add_option("--report-solutions",
                      help="Always report PH solutions after each iteration. Enabled if --verbose is enabled. Default is False.",
                      action="store_true",
                      dest="report_solutions",
                      default=False)
    parser.add_option("--report-weights",
                      help="Always report PH weights prior to each iteration. Enabled if --verbose is enabled. Default is False.",
                      action="store_true",
                      dest="report_weights",
                      default=False)
    parser.add_option('-m',"--model-directory",
                      help="The directory in which all model (reference and scenario) definitions are stored. Default is \".\".",
                      action="store",
                      dest="model_directory",
                      type="string",
                      default=".")
    parser.add_option('-i',"--instance-directory",
                      help="The directory in which all instance (reference and scenario) definitions are stored. Default is \".\".",
                      action="store",
                      dest="instance_directory",
                      type="string",
                      default=".")
    parser.add_option("--solver",
                      help=solver_help,
                      action="store",
                      dest="solver_type",
                      type="string",
                      default="cplex")
    # TBD - a lot of these options should probably be eliminated, and passed through the PH interface.
    parser.add_option("--scenario-solver-options",
                      help="Solver options for all PH scenario sub-problems",
                      action="append",
                      dest="scenario_solver_options",
                      type="string",
                      default=[])
    parser.add_option("--scenario-mipgap",
                      help="Specifies the mipgap for all PH scenario sub-problems",
                      action="store",
                      dest="scenario_mipgap",
                      type="float",
                      default=None)
    parser.add_option('-k',"--keep-solver-files",
                      help="Retain temporary input and output files for scenario sub-problem solves",
                      action="store_true",
                      dest="keep_solver_files",
                      default=False)
    parser.add_option("--output-solver-logs",
                      help="Output solver logs during scenario sub-problem solves",
                      action="store_true",
                      dest="output_solver_logs",
                      default=False)
    parser.add_option("--output-solver-results",
                      help="Output solutions obtained after each scenario sub-problem solve",
                      action="store_true",
                      dest="output_solver_results",
                      default=False)
    parser.add_option("--output-times",
                      help="Output timing statistics for various PH components",
                      action="store_true",
                      dest="output_times",
                      default=False)
    parser.add_option("--disable-warmstarts",
                      help="Disable warm-start of scenario sub-problem solves in PH iterations >= 1. Default is False.",
                      action="store_true",
                      dest="disable_warmstarts",
                      default=False)
    parser.add_option("--profile",
                      help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
                      action="store",
                      dest="profile",
                      type="int",
                      default=0)
    parser.add_option("--disable-gc",
                      help="Disable the python garbage collecter. Default is False.",
                      action="store_true",
                      dest="disable_gc",
                      default=False)

    parser.usage=usage_string

    return parser

#
# Execute the PH solver server daemon.
#

def run_server(options, scenario_instances, solver, solver_type, scenario_tree):

    pyutilib.pyro.TaskWorkerServer(PHSolverServer, scenario_instances=scenario_instances, solver=solver, solver_type=solver_type, scenario_tree=scenario_tree, bundle_name=options.bundle, output_solver_logs=options.output_solver_logs)

#
# The main daemon initialization / runner routine.
#

def exec_server(options):

    # the solver instance is persistent, applicable to all instances here.
    if options.verbose is True:
        print "Constructing solver type="+options.solver_type
    solver = SolverFactory(options.solver_type)
    if solver == None:
        raise ValueError, "Unknown solver type=" + options.solver_type + " specified"
    if options.keep_solver_files is True:
        solver.keepFiles = True
    if len(options.scenario_solver_options) > 0:
        if options.verbose is True:
            print "Initializing scenario sub-problem solver with options="+str(options.scenario_solver_options)
        solver.set_options("".join(options.scenario_solver_options))
    if options.output_times is True:
        solver._report_timing = True

    # we need the base model (not so much the reference instance, but that
    # can't hurt too much - until proven otherwise, that is) to construct
    # the scenarios that this server is responsible for.
    reference_model, reference_instance, scenario_tree, scenario_tree_instance = load_reference_and_scenario_models(options)
    if reference_model is None or reference_instance is None or scenario_tree is None:
        raise RuntimeError, "***Unable to launch PH solver server."

    # check to see if both the --bundle and --scenario options have been specified 
    # on the command-line - error if so, as they are exclusive.
    if (options.bundle is not None) and (len(options.scenarios) > 0):
        raise RuntimeError, "***The use of the --bundle and --scenario options are mutually exclusive."

    scenarios_to_construct = []

    if options.bundle is not None:
       # validate that the bundle actually exists. 
       if scenario_tree.contains_bundle(options.bundle) is False:
           raise RuntimeError, "***Bundle="+options.bundle+" does not exist."

       if options.verbose is True:
           print "Loading scenarios for bundle="+options.bundle

       # bundling should use the local or "mini" scenario tree - and 
       # then enable the flag to load all scenarios for this instance.
       scenario_bundle = scenario_tree.get_bundle(options.bundle)
       scenarios_to_construct = scenario_bundle._scenario_names

    else:
        if (options.all_scenarios is True) and (len(options.scenarios) > 0):
            print "***WARNING: Both individual scenarios and all-scenarios were specified on the command-line; proceeding using all scenarios."

        if (len(options.scenarios) == 0) and (options.all_scenarios is False):
            raise RuntimeError, "***Unable to launch PH solver server - no scenario(s) specified!"

    # construct the set of scenario instances based on the command-line.
    scenario_instances = {} # a map between scenario names and the corresponding Pyomo instance
    if options.bundle is None:
        if options.all_scenarios is True:
            scenarios_to_construct.extend(scenario_tree._scenario_map.keys())
        else:
           scenarios_to_construct.extend(options.scenarios)

    for scenario_name in scenarios_to_construct:
        print "Creating instance for scenario="+scenario_name
        if scenario_tree.contains_scenario(scenario_name) is False:
            raise RuntimeError, "***Unable to launch PH solver server - unknown scenario specified with name="+scenario_name+"."

        # create the baseline scenario instance
        scenario_instance = construct_scenario_instance(scenario_tree,
                                                        options.instance_directory,
                                                        scenario_name,
                                                        reference_model,
                                                        options.verbose,
                                                        preprocess=False,
                                                        linearize=False)

        # important - mark the scenario instances as "concrete" - PH augments
        # the instances in various ways, including via variable, constraint, and
        # objective modifications when dealing with quadratic proximal and the weight
        # penalty terms.
        scenario_instance.concrete_mode()

        # IMPT: disable canonical representation construction for ASL solvers.
        #       this is a hack, in that we need to address encodings and
        #       the like at a more general level.
        if options.solver_type == "asl" or options.solver_type == "ipopt":
            scenario_instance.skip_canonical_repn = True

        scenario_instance.preprocess()            

        # TBD: keep track of the new penalty variables / etc returned by the method below. ALSO ADD RHO/LINEARIZATION.
        create_ph_parameters(scenario_instance, scenario_tree, 1, False)

        if scenario_instance is None:
            raise RuntimeError, "***Unable to launch PH solver server - failed to create instance for scenario="+scenario_name

        # augment the instance with PH-specific parameters (weights, rhos, etc).
        # TBD: The default rho of 1.0 is kind of bogus. Need to somehow propagate
        #      this value and the linearization parameter as a command-line argument.
        new_penalty_variable_names = create_ph_parameters(scenario_instance, scenario_tree, 1.0, False)

        scenario_instances[scenario_name] = scenario_instance

    # with the scenario instances now available, have the scenario tree 
    # compute the variable match indices at each node.
    scenario_tree.defineVariableIndexSets(scenario_instances)

    # spawn the daemon.
    run_server(options, scenario_instances, solver, options.solver_type, scenario_tree)

def run(args=None):

    #
    # Top-level command that executes the ph solver server daemon.
    # This is segregated from phsolverserver to faciliate profiling.
    #

    #
    # Parse command-line options.
    #
    try:
        options_parser = construct_options_parser("phsolverserver [options]")
        (options, args) = options_parser.parse_args(args=args)
    except SystemExit:
        # the parser throws a system exit if "-h" is specified - catch
        # it to exit gracefully.
        return

    # for a one-pass execution, garbage collection doesn't make
    # much sense - so it is disabled by default. Because: It drops
    # the run-time by a factor of 3-4 on bigger instances.
    if options.disable_gc is True:
        gc.disable()
    else:
        gc.enable()

    if options.profile > 0:
        #
        # Call the main PH routine with profiling.
        #
        tfile = TempfileManager.create_tempfile(suffix=".profile")
        tmp = profile.runctx('exec_server(options)',globals(),locals(),tfile)
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cum')
        p = p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('cum','calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        TempfileManager.clear_tempfiles()
        ans = [tmp, None]
    else:
        #
        # Call the main PH routine without profiling.
        #
        ans = exec_server(options)

    gc.enable()

    return ans

def main():
    try:
        run()
    except IOError, str:
        print "IO ERROR:"
        print str
    except pyutilib.common.ApplicationError, str:
        print "APPLICATION ERROR:"
        print str
    except RuntimeError, str:
        print "RUN-TIME ERROR:"
        print str
    # pyutilib.pyro tends to throw SystemExit exceptions if things cannot be found or hooked
    # up in the appropriate fashion. the name is a bit odd, but we have other issues to worry 
    # about. we are dumping the trace in case this does happen, so we can figure out precisely
    # who is at fault.
    except SystemExit, str:
        print "PH solver server encountered system error"
        print "Error:", str
        print "Stack trace:"
        traceback.print_exc()
    except:
        print "Encountered unhandled exception"
        traceback.print_exc()
