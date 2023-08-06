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

from pyutilib.misc import import_file, PauseGC
from pyutilib.services import TempfileManager

import Pyro.core
import Pyro.naming
from Pyro.errors import PyroError, NamingError

from phinit import *
from phutils import *
from phobjective import *

import pyutilib.pyro

class PHSolverServer(pyutilib.pyro.TaskWorker):

    # NOTE: The following two methods are stolen from ph.py, and are identical. The code should
    #       be shared, but we are being lazy and are unsure how to deal with the "self" object
    #       at this point.

    #
    # a utility intended for folks who are brave enough to script variable bounds setting in a python file.
    #

    def setVariableBoundsAllScenarios(self, variable_name, variable_index, lower_bound, upper_bound):

        if isinstance(lower_bound, float) is False:
            raise ValueError, "Lower bound supplied to PH method setVariableBoundsAllScenarios for variable="+variable_name+indexToString(variable_index)+" must be a constant; value supplied="+str(lower_bound)

        if isinstance(upper_bound, float) is False:
            raise ValueError, "Upper bound supplied to PH method setVariableBoundsAllScenarios for variable="+variable_name+indexToString(variable_index)+" must be a constant; value supplied="+str(upper_bound)

        for name, instance in self._instances.itervalues():

            variable = getattr(instance, variable_name)
            variable[variable_index].setlb(lower_bound)
            variable[variable_index].setub(upper_bound)

    #
    # a utility intended for folks who are brave enough to script variable bounds setting in a python file.
    # same functionality as above, but applied to all indicies of the variable, in all scenarios.
    #

    def setVariableBoundsAllIndicesAllScenarios(self, variable_name, lower_bound, upper_bound):

        if isinstance(lower_bound, float) is False:
            raise ValueError, "Lower bound supplied to PH method setVariableBoundsAllIndiciesAllScenarios for variable="+variable_name+" must be a constant; value supplied="+str(lower_bound)

        if isinstance(upper_bound, float) is False:
            raise ValueError, "Upper bound supplied to PH method setVariableBoundsAllIndicesAllScenarios for variable="+variable_name+" must be a constant; value supplied="+str(upper_bound)

        for instance in self._instances.values():

            variable = getattr(instance, variable_name)
            for index in variable:
                variable[index].setlb(lower_bound)
                variable[index].setub(upper_bound)

    def __init__(self, **kwds):

        pyutilib.pyro.TaskWorker.__init__(self)

        self._solver = None
        self._solver_type = None

        # only one of these will be != None, following initialization.
        self._scenario_name = None
        self._bundle_name = None

        # for largely cosmetic purposes at the moment, we track
        # various additions / modifications of the original instances.
        self._instance_ph_variables = {}
        self._instance_ph_constraints = {}
        self._instance_ph_linear_expressions = {}
        self._instance_ph_quadratic_expressions = {}

        # the TaskWorker base uses the "type" option to determine the name
        # of the queue from which to request work, via the dispatch server.
        # 
        # the default type is "initialize", which is the queue to which the
        # runph client will transmit initialization to. once initialized,
        # the queue name will be changed to the scenario/bundle name for
        # which this solver server is responsible.
        self.type = "initialize"

        # a simple boolean flag indicating whether or not this ph solver 
        # server has received an initialization method and has successfully
        # processed it.
        self._initialized = False

    def initialize(self, model_directory, instance_directory, 
                   solver_type, object_name,
                   scenario_bundle_specification,
                   create_random_bundles, scenario_tree_random_seed,
                   default_rho, linearize_nonbinary_penalty_terms, 
                   verbose):

        if verbose:
            print "Received request to initialize PH solver server"
            print ""
            print "Model directory:",model_directory
            print "Instance directory:",instance_directory
            print "Solver type:",solver_type
            print "Scenario or bundle name:",object_name
            print "Scenario tree bundle specification:",scenario_bundle_specification
            print "Create random bundles:", create_random_bundles
            print "Scenario tree random seed:", scenario_tree_random_seed
            print "Linearize non-binary penalty terms: ", linearize_nonbinary_penalty_terms

        if self._initialized:
            raise RuntimeError, "***PH solver servers cannot currently be re-initialized"

        self._linearize_nonbinary_penalty_terms = linearize_nonbinary_penalty_terms

        # the solver instance is persistent, applicable to all instances here.
        self._solver_type = solver_type
        if verbose:
            print "Constructing solver type="+solver_type
        self._solver = SolverFactory(solver_type)
        if self._solver == None:
            raise ValueError, "Unknown solver type=" + solver_type + " specified"

        # we need the base model (not so much the reference instance, but that
        # can't hurt too much - until proven otherwise, that is) to construct
        # the scenarios that this server is responsible for.
        # TBD - revisit the various "weird" scenario tree arguments
        self._reference_model, self._model_instance, self._scenario_tree, self._scenario_tree_instance = load_reference_and_scenario_models(model_directory,
                                                                                                                                            instance_directory,
                                                                                                                                            scenario_bundle_specification,
                                                                                                                                            None,
                                                                                                                                            scenario_tree_random_seed,
                                                                                                                                            create_random_bundles,
                                                                                                                                            solver_type,
                                                                                                                                            verbose)
                                                                                                                                                
                                                                                                                                                
          
        if self._reference_model is None or self._model_instance is None or self._scenario_tree is None:
             raise RuntimeError, "***Unable to launch PH solver server."

        self._instances = {}
        scenarios_to_construct = []

        if self._scenario_tree.contains_bundles():
            self._bundle_name = object_name

            # validate that the bundle actually exists. 
            if self._scenario_tree.contains_bundle(object_name) is False:
                raise RuntimeError, "***Bundle="+object_name+" does not exist."
    
            if verbose:
                print "Loading scenarios for bundle="+object_name

            # bundling should use the local or "mini" scenario tree - and 
            # then enable the flag to load all scenarios for this instance.
            scenario_bundle = self._scenario_tree.get_bundle(object_name)
            scenarios_to_construct = scenario_bundle._scenario_names

        else:
            self._scenario_name = object_name
            scenarios_to_construct.append(object_name)

        for scenario_name in scenarios_to_construct:

            print "Creating instance for scenario="+scenario_name

            if self._scenario_tree.contains_scenario(scenario_name) is False:
                raise RuntimeError, "***Unable to launch PH solver server - unknown scenario specified with name="+scenario_name+"."

            # create the baseline scenario instance
            scenario_instance = construct_scenario_instance(self._scenario_tree,
                                                            instance_directory,
                                                            scenario_name,
                                                            self._reference_model,
                                                            verbose,
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
            if self._solver_type == "asl" or self._solver_type == "ipopt":
                scenario_instance.skip_canonical_repn = True

            if scenario_instance is None:
                raise RuntimeError, "***Unable to launch PH solver server - failed to create instance for scenario="+scenario_name

            # augment the instance with PH-specific parameters (weights, rhos, etc).
            #      this value and the linearization parameter as a command-line argument.
            new_penalty_variable_names = create_ph_parameters(scenario_instance, self._scenario_tree, default_rho, linearize_nonbinary_penalty_terms)
            self._instance_ph_variables[scenario_name] = new_penalty_variable_names

            self._instance_ph_constraints[scenario_name] = []

            # preprocess the whole thing in preparation for solves.
            scenario_instance.preprocess()            

            self._instances[scenario_name] = scenario_instance

        # with the scenario instances now available, have the scenario tree 
        # compute the variable match indices at each node.
        self._scenario_tree.defineVariableIndexSets(self._instances)

        # create the bundle extensive form, if bundling.
        if self._bundle_name is not None:
            self._bundle_scenario_tree = self._scenario_tree.get_bundle(self._bundle_name)._scenario_tree

            # WARNING: THIS IS A PURE HACK - WE REALLY NEED TO CALL THIS WHEN WE CONSTRUCT THE BUNDLE 
            #          SCENARIO TREE. AS IT STANDS, THIS MUST BE DONE BEFORE CREATING THE EF INSTANCE.
            self._bundle_scenario_tree.defineVariableIndexSets(self._instances)
    
            # create the bundle EF instance, and cache the original EF objective.
            self._bundle_ef_instance = create_ef_instance(self._bundle_scenario_tree, self._instances, verbose_output=verbose)
            bundle_ef_objectives = self._bundle_ef_instance.active_components(Objective)
            objective_name = bundle_ef_objectives.keys()[0]
            bundle_ef_objective = bundle_ef_objectives[objective_name]            
            self._original_bundle_objective = bundle_ef_objective._data[None].expr

            # finally, preprocess the bundle instance
            self._bundle_ef_instance.preprocess()

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

        # the server is in one of two modes - solve the baseline instances, or
        # those augmented with the PH penalty terms. default is standard.
        # NOTE: This is currently a global flag for all scenarios handled
        #       by this server - easy enough to extend if we want.
        self._solving_standard_objective = True

        # as occurs in the main PH routine, track which components - if any - need to
        # be pre-processed prior to the next invocation of the solve() method.
        self._instance_objectives_changed = False        
        self._instance_objectives_modified = False
        self._instance_piecewise_constraints_modified = False
        self._instance_variables_fixed = False

        # the TaskWorker base uses the "type" option to determine the name
        # of the queue from which to request work, via the dispatch server.
        self.type = object_name

        # we're good to go!
        self._initialized = True

    def form_standard_objective(self, scenario_name, verbose):

        if verbose:
           print "Received request to enable standard objective for scenario="+scenario_name

        if self._initialized is False:
            raise RuntimeError, "***PH solver server has not been initialized!"

        if verbose:
            print "Forming standard objective function"           

        form_standard_objective(scenario_name, scenario_instance, self._original_objective_expression[scenario_name], self._scenario_tree)           
        self._solving_standard_objective = True
        self._instance_objectives_changed = True

    def form_ph_objective(self, scenario_name, drop_proximal_terms, retain_quadratic_binary_terms, verbose):

        if verbose:
            print "Received request to enable PH objective for scenario="+scenario_name

        if self._initialized is False:
            raise RuntimeError, "***PH solver server has not been initialized!"

        scenario_instance = self._instances[scenario_name]            

        new_lin_terms, new_quad_terms = form_ph_objective(scenario_name, scenario_instance, 
                                                          self._original_objective_expression[scenario_name], 
                                                          self._scenario_tree, 
                                                          self._linearize_nonbinary_penalty_terms,
                                                          drop_proximal_terms,
                                                          retain_quadratic_binary_terms)

        self._instance_ph_linear_expressions[scenario_name] = new_lin_terms
        self._instance_ph_quadratic_expressions[scenario_name] = new_quad_terms      

        if verbose:
            print "Forming PH objective function"                  

        self._solving_standard_objective = False
        self._instance_objectives_changed = True

    def solve(self, object_name, verbose, tee, solver_options, breakpoint_strategy, integer_tolerance):

      if verbose:
          if self._bundle_name is not None:
              print "Received request to solve scenario bundle="+object_name
          else:
              print "Received request to solve scenario instance="+object_name

      if self._initialized is False:
          raise RuntimeError, "***PH solver server has not been initialized!"

      # process input solver options - they will be persistent across to the  next solve. 
      # TBD: we might want to re-think a reset() of the options, or something.
      for key,value in solver_options.iteritems():
          if verbose:
              print "Processing solver option="+key+", value="+str(value)
          self._solver.options[key] = value

      # with the introduction of piecewise linearization, the form of the
      # penalty-weighted objective is no longer fixed. thus, when linearizing,
      # we need to construct (or at least modify) the constraints used to
      # compute the linearized cost terms.
      if (self._linearize_nonbinary_penalty_terms > 0) and (self._solving_standard_objective is False):
          for instance_name, instance in self._instances.iteritems():
              new_attrs = form_linearized_objective_constraints(instance_name, 
                                                                instance, 
                                                                self._scenario_tree, 
                                                                self._linearize_nonbinary_penalty_terms, 
                                                                breakpoint_strategy, 
                                                                integer_tolerance)

              self._instance_ph_constraints[instance_name].extend(new_attrs)

              # if linearizing, clear the values of the PHQUADPENALTY* variables.
              # if they have values, this can intefere with warm-starting due to
              # constraint infeasibilities.
              reset_linearization_variables(instance)

          self._instance_piecewise_constraints_modified = True

      # preprocess all scenario instances as needed - if bundling, we take care of the specifics below.
      for scenario_name, scenario_instance in self._instances.iteritems():
          
          instance_constraints = []
          if (self._solving_standard_objective is False) and (self._linearize_nonbinary_penalty_terms > 0):
              instance_constraints = self._instance_ph_constraints[scenario_name]

          preprocess_scenario_instance(scenario_instance, 
                                       self._instance_variables_fixed, 
                                       self._instance_piecewise_constraints_modified, 
                                       instance_constraints,
                                       self._instance_objectives_changed,
                                       self._instance_objectives_modified, 
                                       self._solver_type)

      self._instance_variables_fixed = False
      self._instance_piecewise_constraints_modified = False
      self._instance_objectives_changed = False
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
                 new_lin_terms = self._instance_ph_linear_expressions[scenario_name] 
                 new_quad_terms = self._instance_ph_quadratic_expressions[scenario_name]
                 scenario = self._scenario_tree._scenario_map[scenario_name]
                 # TBD: THIS SHOULD NOT HAVE TO BE DONE EACH ITERATION - THE OBJECTIVE STRUCTURE DOES NOT CHANGE, AND THE LINEARIZATION 
                 #      CONSTRAINTS ARE ON THE SCENARIO INSTANCES.
                 bundle_ef_objective._data[None].expr += (scenario._probability / scenario_bundle._probability) * (new_lin_terms)
                 bundle_ef_objective._data[None].expr += (scenario._probability / scenario_bundle._probability) * (new_quad_terms)

              # TBD: JUST PREPROCESS OBJECTIVE - NOT THE WHOLE EF INSTANCE - OTHERWISE, WE'RE DOING A LOT OF UNNECESSARY WORK.
              self._bundle_ef_instance.preprocess()                 

          results = self._solver.solve(self._bundle_ef_instance, tee=tee)

          if verbose:
              print "Successfully solved scenario bundle="+object_name      

          if len(results.solution) == 0:
              results.write()
              raise RuntimeError, "Solve failed for bundle="+object_name+"; no solutions generated"          

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          self._bundle_ef_instance.load(results)

          if verbose:
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

          # the PH objective being enabled is a proxy for having a solution available from which to warm-start.
          if self._solver.warm_start_capable() and (not self._solving_standard_objective): 
             results = self._solver.solve(scenario_instance, tee=tee, warmstart=True) 
          else:
             results = self._solver.solve(scenario_instance, tee=tee)

          if verbose:
              print "Successfully solved scenario instance="+object_name      

          if len(results.solution) == 0:
              results.write()
              raise RuntimeError, "Solve failed for scenario="+object_name+"; no solutions generated"          

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          scenario_instance.load(results)

          if verbose:
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
    # updating weights and averages only applies to scenarios - not bundles.
    #
    def update_weights_and_averages(self, scenario_name, new_weights, new_averages, verbose):

        if verbose:
            print "Received request to update weights and averages for scenario="+scenario_name

        if self._initialized is False:
            raise RuntimeError, "***PH solver server has not been initialized!"

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
    # updating bounds is only applicable to scenarios.
    #
    def update_bounds(self, scenario_name, new_bounds, verbose):

        if verbose:
            print "Received request to update variable bounds for scenario="+scenario_name

        if self._initialized is False:
            raise RuntimeError, "***PH solver server has not been initialized!"

        if scenario_name not in self._instances:
            print "ERROR: Received request to update variable bounds for instance not in PH solver server instance collection!"
            return None
        scenario_instance = self._instances[scenario_name]

        for variable_name, bounds_update in new_bounds.iteritems():

            instance_variable = getattr(scenario_instance, variable_name)

            for index, new_value in bounds_update.iteritems():
                instance_variable[index].setlb(new_value[0])
                instance_variable[index].setub(new_value[1])                

    #
    # updating rhos is only applicable to scenarios.
    #
    def update_rhos(self, scenario_name, new_rhos, verbose):

        if verbose:
            print "Received request to update rhos for scenario="+scenario_name

        if self._initialized is False:
            raise RuntimeError, "***PH solver server has not been initialized!"

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
    # updating tree node statistics is bundle versus scenario agnostic.
    #

    def update_tree_node_statistics(self, scenario_name, new_node_minimums, new_node_maximums, verbose):

        if verbose:
            if self._bundle_name is not None:
                print "Received request to update tree node statistics for bundle="+self._bundle_name
            else:
                print "Received request to update tree node statistics for scenario="+scenario_name

        if self._initialized is False:
            raise RuntimeError, "***PH solver server has not been initialized!"

        for tree_node_name, tree_node_minimums in new_node_minimums.items():

            tree_node = self._scenario_tree._tree_node_map[tree_node_name]
            tree_node._minimums = tree_node_minimums

        for tree_node_name, tree_node_maximums in new_node_maximums.items():

            tree_node = self._scenario_tree._tree_node_map[tree_node_name]
            tree_node._maximums = tree_node_maximums


    #
    # fix variables as instructed by the PH client.
    #
    def fix_variables(self, scenario_name, variables_to_fix, verbose):

        if verbose:
            print "Received request to fix variables for scenario="+scenario_name

        if self._initialized is False:
            raise RuntimeError, "***PH solver server has not been initialized!"

        for variable_name, index in variables_to_fix:
           if verbose is True:
               print "Fixing variable="+variable_name+indexToString(index)+" on instance="+scenario_name
           getattr(self._instances[scenario_name], variable_name)[index].fixed = True

        self._instance_variables_fixed = True
    
    def process(self, data):

        suspend_gc = PauseGC()

        result = None
        if data.action == "initialize":
           result = self.initialize(data.model_directory, data.instance_directory, 
                                    data.solver_type, data.object,
                                    data.scenario_bundle_specification,
                                    data.create_random_bundles, data.scenario_tree_random_seed, 
                                    data.default_rho, data.linearize_nonbinary_penalty_terms,
                                    data.verbose)
        elif data.action == "solve":
           result = self.solve(data.name, data.verbose, data.tee, data.solver_options, data.breakpoint_strategy, data.integer_tolerance)
        elif data.action == "form_ph_objective":
           if self._bundle_name is not None:
               for scenario in self._bundle_scenario_tree._scenarios:
                   self.form_ph_objective(scenario._name, data.drop_proximal_terms, data.retain_quadratic_binary_terms, data.verbose)                   
           else:
               self.form_ph_objective(data.name, data.drop_proximal_terms, data.retain_quadratic_binary_terms, data.verbose)                   
           result = True
        elif data.action == "load_bounds":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in self._instances.iteritems():
                   self.update_bounds(scenario_name, data.new_bounds[scenario_name], data.verbose)               
           else:
               self.update_bounds(data.name, data.new_bounds, data.verbose)
           result = True           
        elif data.action == "load_rhos":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in self._instances.iteritems():
                   self.update_rhos(scenario_name, data.new_rhos[scenario_name], data.verbose)               
           else:
               self.update_rhos(data.name, data.new_rhos, data.verbose)
           result = True
        elif data.action == "fix_variables":
           if self._bundle_name is not None:
               for scenario_name, scenario_instance in self._instances.iteritems():
                   self.fix_variables(scenario_name, data.fixed_variables[scenario_name], data.verbose)               
           else:
               self.fix_variables(data.name, data.fixed_variables, data.verbose)
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

    parser = OptionParser()
    parser.add_option("--verbose",
                      help="Generate verbose output for both initialization and execution. Default is False.",
                      action="store_true",
                      dest="verbose",
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

def run_server(options):

    # just spawn the daemon!
    pyutilib.pyro.TaskWorkerServer(PHSolverServer)

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
    if options.disable_gc:
        gc.disable()
    else:
        gc.enable()

    if options.profile > 0:
        #
        # Call the main PH routine with profiling.
        #
        tfile = TempfileManager.create_tempfile(suffix=".profile")
        tmp = profile.runctx('run_server(options)',globals(),locals(),tfile)
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
        ans = run_server(options)

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
