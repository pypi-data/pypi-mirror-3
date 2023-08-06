#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import copy
import gc
import logging
import pickle
import sys
import traceback
import types
import time
import types

from math import fabs, log, exp
from os import path

from coopr.opt import SolverResults, SolverStatus
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
from coopr.pyomo import *
from coopr.pyomo.base.expr import Expression, _IdentityExpression
from coopr.pysp.phextension import IPHExtension
from coopr.pysp.ef import create_ef_instance, write_ef

from phutils import *
from phobjective import *
from scenariotree import *

from pyutilib.component.core import ExtensionPoint

# a hack for now - should go away soon.
from coopr.opt.base.symbol_map import *

try:
    from guppy import hpy
    guppy_available = True
except ImportError:
    guppy_available = False

logger = logging.getLogger('coopr.pysp')

class ProgressiveHedging(object):
    
    def __del__(self):
        pass
        #print "Called __del__ on ProgressiveHedging plugin; garbage collecting?"
        #print hpy().heap()

    #
    # a pair of utilities intended for folks who are brave enough to script rho setting in a python file.
    #

    def setRhoAllScenarios(self, variable_value, rho_expression):

        variable_name = None
        variable_index = None

        if isVariableNameIndexed(variable_value.name):

            variable_name, variable_index = extractVariableNameAndIndex(variable_value.name)

        else:

            variable_name = variable_value.name
            variable_index = None

        new_rho_value = None
        if isinstance(rho_expression, float):
            new_rho_value = rho_expression
        else:
            new_rho_value = rho_expression()

        if self._verbose:
            print "Setting rho="+str(new_rho_value)+" for variable="+variable_value.name

        for instance in self._instances.itervalues():

            rho_param = getattr(instance, "PHRHO_"+variable_name)
            rho_param[variable_index] = new_rho_value

    def setRhoOneScenario(self, scenario_instance, variable_value, rho_expression):

        variable_name = None
        variable_index = None

        if isVariableNameIndexed(variable_value.name):

            variable_name, variable_index = extractVariableNameAndIndex(variable_value.name)

        else:

            variable_name = variable_value.name
            variable_index = None

        new_rho_value = None
        if isinstance(rho_expression, float):
            new_rho_value = rho_expression
        else:
            new_rho_value = rho_expression()

        if self._verbose:
            print "Setting rho="+str(new_rho_value)+" for variable="+variable_value.name

        rho_param = getattr(scenario_instance, "PHRHO_"+variable_name)
        rho_param[variable_index] = new_rho_value

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

        for instance_name, instance in self._instances.items():

            variable = getattr(instance, variable_name)
            for index in variable:
                variable[index].setlb(lower_bound)
                variable[index].setub(upper_bound)

    #
    # checkpoint the current PH state via pickle'ing. the input iteration count
    # simply serves as a tag to create the output file name. everything with the
    # exception of the _ph_plugins, _solver_manager, and _solver attributes are
    # pickled. currently, plugins fail in the pickle process, which is fine as
    # JPW doesn't think you want to pickle plugins (particularly the solver and
    # solver manager) anyway. For example, you might want to change those later,
    # after restoration - and the PH state is independent of how scenario
    # sub-problems are solved.
    #

    def checkpoint(self, iteration_count):

        checkpoint_filename = "checkpoint."+str(iteration_count)

        tmp_ph_plugins = self._ph_plugins
        tmp_solver_manager = self._solver_manager
        tmp_solver = self._solver

        self._ph_plugins = None
        self._solver_manager = None
        self._solver = None

        checkpoint_file = open(checkpoint_filename, "w")
        pickle.dump(self,checkpoint_file)
        checkpoint_file.close()

        self._ph_plugins = tmp_ph_plugins
        self._solver_manager = tmp_solver_manager
        self._solver = tmp_solver

        print "Checkpoint written to file="+checkpoint_filename

    #
    # a simple utility to count the number of continuous and discrete variables in a set of instances.
    # unused variables are ignored, and counts include all active indices. returns a pair - num-discrete,
    # num-continuous.
    #

    def compute_blended_variable_counts(self):

        num_continuous_vars = 0
        num_discrete_vars = 0

        for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage

            for tree_node in stage._tree_nodes:

                for variable_name, (variable, index_template) in stage._variables.iteritems():

                    variable_indices = tree_node._variable_indices[variable.name]

                    for index in variable_indices:

                        is_used = True # until proven otherwise
                        for scenario in tree_node._scenarios:
                            instance = self._instances[scenario._name]
                            if getattr(instance,variable.name)[index].status == VarStatus.unused:
                                is_used = False

                        if is_used:

                            if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
                                num_discrete_vars = num_discrete_vars + 1
                            else:
                                num_continuous_vars = num_continuous_vars + 1

        return (num_discrete_vars, num_continuous_vars)

    #
    # ditto above, but count the number of fixed discrete and continuous variables.
    # important: once a variable (value) is fixed, it is flagged as unused in the
    # course of presolve - because it is no longer referenced. this makes sense,
    # of course; it's just something to watch for. this is an obvious assumption
    # that we won't be fixing unused variables, which should not be an issue.
    #

    def compute_fixed_variable_counts(self):

        num_fixed_continuous_vars = 0
        num_fixed_discrete_vars = 0

        for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage

            for tree_node in stage._tree_nodes:

                for variable_name, (variable, index_template) in stage._variables.iteritems():

                    variable_indices = tree_node._variable_indices[variable.name]

                    for index in variable_indices:

                        # implicit assumption is that if a variable value is fixed in one
                        # scenario, it is fixed in all scenarios.

                        is_fixed = False # until proven otherwise
                        for scenario in tree_node._scenarios:
                            instance = self._instances[scenario._name]
                            var_value = getattr(instance,variable.name)[index]
                            if var_value.fixed:
                                is_fixed = True

                        if is_fixed:

                            if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
                                num_fixed_discrete_vars = num_fixed_discrete_vars + 1
                            else:
                                num_fixed_continuous_vars = num_fixed_continuous_vars + 1

        return (num_fixed_discrete_vars, num_fixed_continuous_vars)

    #
    # when the quadratic penalty terms are approximated via piecewise linear segments,
    # we end up (necessarily) "littering" the scenario instances with extra constraints.
    # these need to and should be cleaned up after PH, for purposes of post-PH manipulation,
    # e.g., writing the extensive form. equally importantly, we need to re-establish the
    # original instance objectives.
    #

    def _cleanup_scenario_instances(self):

        for instance_name, instance in self._instances.items():

           for constraint_name in self._instance_ph_variables[instance_name]:

               # NOTE: we don't like using the _clear_attribute method, but this is the only one that worked
               #       at the time this code was originally written. 
               instance._clear_attribute(constraint_name)

           for variable_name in self._instance_ph_constraints[instance_name]:

               # NOTE: we don't like using the _clear_attribute method, but this is the only one that worked
               #       at the time this code was originally written. 
               instance._clear_attribute(variable_name)

           form_standard_objective(instance_name, instance, self._original_objective_expression[instance_name])

           # if you don't pre-solve, the name collections/canonicals/etc won't be updated.
           instance.preprocess()

    #
    # create PH weight and xbar vectors, on a per-scenario basis, for each variable that is not in the
    # final stage, i.e., for all variables that are being blended by PH. the parameters are created
    # in the space of each scenario instance, so that they can be directly and automatically
    # incorporated into the (appropriately modified) objective function.
    #

    def _create_scenario_ph_parameters(self):

        for (instance_name, instance) in self._instances.items():

            new_penalty_variable_names = create_ph_parameters(instance, self._scenario_tree, self._rho, self._linearize_nonbinary_penalty_terms)
            self._instance_ph_variables[instance_name].extend(new_penalty_variable_names)

    #
    # a simple utility to extract the first-stage cost statistics, e.g., min, average, and max.
    #

    def _extract_first_stage_cost_statistics(self):

        maximum_value = 0.0
        minimum_value = 0.0
        sum_values = 0.0
        num_values = 0
        first_time = True

        first_stage = self._scenario_tree._stages[0]
        (cost_variable, cost_variable_index) = first_stage._cost_variable
        for scenario_name, instance in self._instances.items():
            this_value = getattr(instance, cost_variable.name)[cost_variable_index].value
            if this_value is not None: # None means not reported by the solver.
                num_values += 1
                sum_values += this_value
                if first_time:
                    first_time = False
                    maximum_value = this_value
                    minimum_value = this_value
                else:
                    if this_value > maximum_value:
                        maximum_value = this_value
                    if this_value < minimum_value:
                        minimum_value = this_value

        if num_values > 0:
            sum_values = sum_values / num_values

        return minimum_value, sum_values, maximum_value

    #
    # a utility to transmit - across the PH solver manager - the current weights
    # and averages for each of my problem instances. used to set up iteration K solves.
    #

    def _extract_weight_and_average_maps(self, scenario_instance):

        # dictionaries of dictionaries. the first key is the parameter name. 
        # the second key is the index for the parameter. the value is the value.
        weights_to_transmit = {}
        averages_to_transmit = {}

        for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage, so no weights to worry about.

            for variable_name, (variable, index_templates) in stage._variables.iteritems():
    
                # the parameters we are transmitting have a fully populated index set - by
                # construction, there are no unused indices. thus, we can simple extract
                # the values in bulk, with no filtering.
                weight_parameter_name = "PHWEIGHT_"+variable_name
                weight_parameter = getattr(scenario_instance, weight_parameter_name)
                weights_to_transmit[weight_parameter_name] = weight_parameter.extract_values()
                    
                average_parameter_name = "PHAVG_"+variable_name
                average_parameter = getattr(scenario_instance, average_parameter_name)                  
                averages_to_transmit[average_parameter_name] = average_parameter.extract_values()

        return weights_to_transmit, averages_to_transmit


    def _transmit_weights_and_averages(self):

        start_time = time.time()

        if self._verbose:
            print "Transmitting instance weights and averages to PH solver servers"

        action_handles = []

        if self._scenario_tree.contains_bundles():

            for bundle in self._scenario_tree._scenario_bundles:

                weights_to_transmit = {}  # map from scenario name to the corresponding weight map
                averages_to_transmit = {} # ditto above, but for averages.

                for scenario_name in bundle._scenario_names:

                    scenario_instance = self._instances[scenario_name]

                    scenario_weights_to_transmit, scenario_averages_to_transmit = self._extract_weight_and_average_maps(scenario_instance)

                    weights_to_transmit[scenario_name] = scenario_weights_to_transmit
                    averages_to_transmit[scenario_name] = scenario_averages_to_transmit

                action_handles.append(self._solver_manager.queue(action="load_weights_and_averages", name=bundle._name, new_weights=weights_to_transmit, new_averages=averages_to_transmit, verbose=self._verbose))                    

        else:

            for scenario_name, scenario_instance in self._instances.items():

                weights_to_transmit, averages_to_transmit = self._extract_weight_and_average_maps(scenario_instance)

                action_handles.append(self._solver_manager.queue(action="load_weights_and_averages", name=scenario_name, new_weights=weights_to_transmit, new_averages=averages_to_transmit, verbose=self._verbose))

        self._solver_manager.wait_all(action_handles)

        end_time = time.time()

        if self._output_times:
            print "Weight and average transmission time=%.2f seconds" % (end_time - start_time)       

    def _initialize_ph_solver_servers(self):

        start_time = time.time()
 
        if self._verbose:
            print "Transmitting initialization information to PH solver servers"

        action_handles = []

        # both the dispatcher queue for initialization and the action name are "initialize" - might be confusing, but hopefully not so much.

        if self._scenario_tree.contains_bundles():

            for bundle in self._scenario_tree._scenario_bundles:

                action_handles.append(self._solver_manager.queue(action="initialize", name="initialize", 
                                                                 model_directory=self._model_directory_name, 
                                                                 instance_directory=self._scenario_data_directory_name,
                                                                 scenario_bundle_specification=self._scenario_bundle_specification,                                                                 
                                                                 create_random_bundles=self._create_random_bundles,
                                                                 scenario_tree_random_seed=self._scenario_tree_random_seed,
                                                                 default_rho=self._rho, 
                                                                 linearize_nonbinary_penalty_terms=self._linearize_nonbinary_penalty_terms,
                                                                 object=bundle._name, verbose=self._verbose, 
                                                                 solver_type=self._solver_type))

        else:

            for scenario_name, scenario_instance in self._instances.iteritems():

                action_handles.append(self._solver_manager.queue(action="initialize", name="initialize", 
                                                                 model_directory=self._model_directory_name, 
                                                                 instance_directory=self._scenario_data_directory_name, 
                                                                 create_random_bundles=self._create_random_bundles,
                                                                 scenario_bundle_specification=None,
                                                                 scenario_tree_random_seed=self._scenario_tree_random_seed,
                                                                 default_rho=self._rho, 
                                                                 linearize_nonbinary_penalty_terms=self._linearize_nonbinary_penalty_terms,
                                                                 object=scenario_name, verbose=self._verbose, 
                                                                 solver_type=self._solver_type))

        # TBD - realistically need a time-out here - look into possibilities.
        self._solver_manager.wait_all(action_handles)

        end_time = time.time()

        if self._output_times:
            print "Initialization transmission time=%.2f seconds" % (end_time - start_time)



    #
    # a utility to extract the bounds for all variables in an instance.
    #

    def _extract_bounds_map(self, scenario_instance):

        # a dictionary of dictionaries. the first key is the variable name, the
        # second key is a variable index. the value is a (lb,ub) pair, where None
        # can be supplied for either.
        bounds_to_transmit = {}

        for tree_node in self._scenario_tree.get_scenario(scenario_instance.name)._node_list:

            for variable_name, variable_indices in tree_node._variable_indices.iteritems():

                bounds_map = bounds_to_transmit.setdefault(variable_name,{})

                variable = getattr(scenario_instance, variable_name)

                for index in variable_indices:
                    bounds_map[index] = (value(variable[index].lb), value(variable[index].ub))
                
        return bounds_to_transmit

    #
    # a utility to transmit - across the PH solver manager - the current rho values for each problem instance. 
    #

    def _transmit_bounds(self):

        start_time = time.time()
 
        if self._verbose:
            print "Transmitting instance variable bounds to PH solver servers"

        action_handles = []

        if self._scenario_tree.contains_bundles():

            for bundle in self._scenario_tree._scenario_bundles:

                bounds_to_transmit = {} # map from scenario name to the corresponding bounds map

                for scenario_name in bundle._scenario_names:

                    scenario_instance = self._instances[scenario_name]                    

                    bounds_to_transmit[scenario_name] = self._extract_bounds_map(scenario_instance)

                action_handles.append(self._solver_manager.queue(action="load_bounds", name=bundle._name, new_bounds=bounds_to_transmit, verbose=self._verbose))                

        else:

            for scenario_name, scenario_instance in self._instances.iteritems():

                bounds_to_transmit = self._extract_bounds_map(scenario_instance)

                action_handles.append(self._solver_manager.queue(action="load_bounds", name=scenario_name, new_bounds=bounds_to_transmit, verbose=self._verbose))

        self._solver_manager.wait_all(action_handles)

        end_time = time.time()

        if self._output_times:
            print "Variable bound transmission time=%.2f seconds" % (end_time - start_time)           

    #
    #
    #

    def _extract_rho_map(self, scenario_instance):

        # a dictionary of dictionaries. the first key is the variable name.
        # the second key is the index for the particular rho. the value is the rho.
        rhos_to_transmit = {} 

        # TBD: I think we have a problem below with over-riding in situations where a variable is shared 
        #      across multiple stages - we probably need to do some kind of collect. same goes for 
        #      weight/average transmission logic above.
        for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage, so no rhos to worry about.

            for variable_name, (variable, index_templates) in stage._variables.iteritems():

                rho_parameter_name = "PHRHO_"+variable_name
                rho_parameter = getattr(scenario_instance, rho_parameter_name)
                rhos_to_transmit[rho_parameter_name] = rho_parameter.extract_values()

        return rhos_to_transmit

    #
    # a utility to transmit - across the PH solver manager - the current rho values for each problem instance. 
    #

    def _transmit_rhos(self):

        start_time = time.time()
 
        if self._verbose:
            print "Transmitting instance rhos to PH solver servers"

        action_handles = []

        if self._scenario_tree.contains_bundles():

            for bundle in self._scenario_tree._scenario_bundles:

                rhos_to_transmit = {} # map from scenario name to the corresponding rho map

                for scenario_name in bundle._scenario_names:

                    scenario_instance = self._instances[scenario_name]                    

                    rhos_to_transmit[scenario_name] = self._extract_rho_map(scenario_instance)

                action_handles.append(self._solver_manager.queue(action="load_rhos", name=bundle._name, new_rhos=rhos_to_transmit, verbose=self._verbose))                

        else:

            for scenario_name, scenario_instance in self._instances.iteritems():

                rhos_to_transmit = self._extract_rho_map(scenario_instance)

                action_handles.append(self._solver_manager.queue(action="load_rhos", name=scenario_name, new_rhos=rhos_to_transmit, verbose=self._verbose))

        self._solver_manager.wait_all(action_handles)

        end_time = time.time()

        if self._output_times:
            print "Rho transmission time=%.2f seconds" % (end_time - start_time)       

    #
    # a utility to transmit - across the PH solver manager - the current scenario
    # tree node statistics to each of my problem instances. done prior to each
    # PH iteration k.
    #

    def _transmit_tree_node_statistics(self):

        # NOTE: A lot of the information here is redundant, as we are currently
        #       transmitting all information for all nodes to all solver servers,
        #       rather than information for the tree nodes associated with 
        #       scenarios for which a solver server is responsible.
        

        start_time = time.time()
 
        if self._verbose:
            print "Transmitting tree node statistics to PH solver servers"

        action_handles = []

        if self._scenario_tree.contains_bundles():

            for bundle in self._scenario_tree._scenario_bundles:

                tree_node_minimums = {}
                tree_node_maximums = {}                

                # iterate over the tree nodes in the bundle scenario tree - but
                # there aren't any statistics there - be careful!
                for bundle_tree_node in bundle._scenario_tree._tree_nodes:

                    primary_tree_node = self._scenario_tree._tree_node_map[bundle_tree_node._name]

                    tree_node_minimums[primary_tree_node._name] = primary_tree_node._minimums
                    tree_node_maximums[primary_tree_node._name] = primary_tree_node._maximums

                action_handles.append(self._solver_manager.queue(action="load_tree_node_stats", name=bundle._name, new_mins=tree_node_minimums, new_maxs=tree_node_maximums, verbose=self._verbose))                    

        else:

            for scenario_name, scenario_instance in self._instances.iteritems():

                tree_node_minimums = {}
                tree_node_maximums = {}

                scenario = self._scenario_tree._scenario_map[scenario_name]

                for tree_node in scenario._node_list:

                    tree_node_minimums[tree_node._name] = tree_node._minimums
                    tree_node_maximums[tree_node._name] = tree_node._maximums

                action_handles.append(self._solver_manager.queue(action="load_tree_node_stats", name=scenario_name, new_mins=tree_node_minimums, new_maxs=tree_node_maximums, verbose=self._verbose))

        self._solver_manager.wait_all(action_handles)

        end_time = time.time()

        if self._output_times:
            print "Tree node statistics transmission time=%.2f seconds" % (end_time - start_time)       

    #
    # a utility to enable - across the PH solver manager - weighted penalty objectives.
    #

    def _enable_ph_objectives(self):

        if self._verbose:
            print "Transmitting request to form PH objectives to PH solver servers"        

        action_handles = []

        if self._scenario_tree.contains_bundles():

            for bundle in self._scenario_tree._scenario_bundles:
                action_handles.append(self._solver_manager.queue(action="form_ph_objective", 
                                                                 name=bundle._name, 
                                                                 drop_proximal_terms=self._drop_proximal_terms,
                                                                 retain_quadratic_binary_terms=self._retain_quadratic_binary_terms,
                                                                 verbose=self._verbose))            

        else:

            for scenario_name, scenario_instance in self._instances.iteritems():
                action_handles.append(self._solver_manager.queue(action="form_ph_objective", 
                                                                 name=scenario_name, 
                                                                 drop_proximal_terms=self._drop_proximal_terms,
                                                                 retain_quadratic_binary_terms=self._retain_quadratic_binary_terms,
                                                                 verbose=self._verbose))
            
        self._solver_manager.wait_all(action_handles)

    def _transmit_fixed_variables(self):

        start_time = time.time()
 
        if self._verbose:
            print "Transmitting fixed variable status to PH solver servers"

        action_handles = []

        if self._scenario_tree.contains_bundles():

            for bundle in self._scenario_tree._scenario_bundles:

                fixed_variables_to_transmit = {} # map from scenario name to the corresponding list of fixed variables

                for scenario_name in bundle._scenario_names:

                    scenario_instance = self._instances[scenario_name]                    

                    fixed_variables_to_transmit[scenario_name] = self._instance_variables_fixed_detail[scenario_name]

                action_handles.append(self._solver_manager.queue(action="fix_variables", name=bundle._name, fixed_variables=fixed_variables_to_transmit, verbose=self._verbose))                

        else:

            for scenario_name, scenario_instance in self._instances.iteritems():

                fixed_variables_to_transmit = self._instance_variables_fixed_detail[scenario_name]

                action_handles.append(self._solver_manager.queue(action="fix_variables", name=scenario_name, fixed_variables=fixed_variables_to_transmit, verbose=self._verbose))

        self._solver_manager.wait_all(action_handles)

        end_time = time.time()

        if self._output_times:
            print "Fixed variable transmission time=%.2f seconds" % (end_time - start_time)       

    #
    # load results coming back from the Pyro PH solver server into the input instance.
    # the input results are a dictionary of dictionaries, mapping variable name to
    # dictionaries the first level; mapping indices to new values at the second level.
    #

    def _load_variable_values(self, scenario_instance, variable_values):

        for variable_name, values in variable_values.iteritems():
            variable = getattr(scenario_instance, variable_name)
            variable.store_values(values)

    # 
    # when bundling, form the extensive form binding instances given the current scenario tree specification.
    # unless bundles are dynamic, only needs to be invoked once, before PH iteration 0. otherwise, needs to
    # be invoked each time the bundles are tweaked.
    #
    # the resulting binding instances are stored in: self._bundle_extensive_form_map.
    # the scenario instances associated with a bundle are stored in: self._bundle_scenario_instance_map.
    #
    
    def _form_bundle_binding_instances(self):

        start_time = time.time()
        if self._verbose:
           print "Forming binding instances for all scenario bundles"
       
        self._bundle_binding_instance_map.clear()
        self._bundle_binding_instance_objective_map.clear()
        self._bundle_scenario_instance_map.clear()

        if self._scenario_tree.contains_bundles() is False:
           raise RuntimeError, "Failed to create binding instances for scenario bundles - bundling is not enabled!"

        for scenario_bundle in self._scenario_tree._scenario_bundles:        

            if self._verbose:
                print "Creating binding instance for scenario bundle="+scenario_bundle._name

            self._bundle_scenario_instance_map[scenario_bundle._name] = {}
            for scenario_name in scenario_bundle._scenario_names:
               self._bundle_scenario_instance_map[scenario_bundle._name][scenario_name] = self._instances[scenario_name]

            # WARNING: THIS IS A PURE HACK - WE REALLY NEED TO CALL THIS WHEN WE CONSTRUCT THE BUNDLE SCENARIO TREE.
            #          AS IT STANDS, THIS MUST BE DONE BEFORE CREATING THE EF INSTANCE.
            scenario_bundle._scenario_tree.defineVariableIndexSets(self._instances)

            bundle_ef_instance = create_ef_instance(scenario_bundle._scenario_tree, self._bundle_scenario_instance_map[scenario_bundle._name], self._verbose)
            self._bundle_binding_instance_map[scenario_bundle._name] = bundle_ef_instance

            # cache the binding instance objective expression - this is the only aspect 
            # that needs to change across PH iterations. we make the EF, so we know it
            # only has one objective.
            bundle_ef_objectives = bundle_ef_instance.active_components(Objective)
            objective_name = bundle_ef_objectives.keys()[0]
            bundle_ef_objective = bundle_ef_objectives[objective_name]
            self._bundle_binding_instance_objective_map[scenario_bundle._name] = bundle_ef_objective._data[None].expr # this is just a variable for now, so you can't and don't need to clone.
        end_time = time.time()

        if self._output_times:
            print "Scenario bundle construction time=%.2f seconds" % (end_time - start_time)

    # 
    # a utility to perform preprocessing on all scenario instances, on an as-needed basis. 
    # queries the instance modification indicator attributes on the ProgressiveHedging (self)
    # object. intended to be invoked before each iteration of PH, just before scenario solves.
    #

    def _preprocess_scenario_instances(self):

        start_time = time.time()

        for scenario_name, scenario_instance in self._instances.iteritems():

            preprocess_scenario_instance(scenario_instance, self._instance_variables_fixed, \
                                         self._instance_piecewise_constraints_modified, self._instance_ph_constraints[scenario_name], \
                                         self._instance_objectives_changed, self._instance_objectives_modified, self._solver_type)

        end_time = time.time()

        if self._output_times:
            print "Scenario instance preprocessing time=%.2f seconds" % (end_time - start_time)

    #
    # when linearizing the PH objective, PHQUADPENALTY* variables are introduced. however, the inclusion /
    # presence of these variables in warm-start files leads to infeasible MIP starts. thus, we want to flag
    # their value as None in all scenario instances prior to performing scenario sub-problem solves.
    #

    def _reset_instance_linearization_variables(self):

       for scenario_instance in self._instances.itervalues():
           reset_linearization_variables(scenario_instance)

    def __init__(self, options):

        # PH configuration parameters
        self._rho = 0.0 # a default, global value for rho. 0 indicates unassigned.
        self._overrelax = False 
        self._nu = 0.0  # a default, global value for nu. 0 indicates unassigned.
        self._rho_setter = None # filename for the modeler to set rho on a per-variable or per-scenario basis.
        self._bounds_setter = None # filename for the modeler to set rho on a per-variable basis, after all scenarios are available.
        self._max_iterations = 0
        self._async = False
        self._async_buffer_len = 1

        # PH reporting parameters
        self._verbose = False # do I flood the screen with status output?
        self._report_solutions = False # do I report solutions after each PH iteration?
        self._report_weights = False # do I report PH weights prior to each PH iteration?
        self._report_only_statistics = False # do I report only variable statistics when outputting solutions and weights?
        self._output_continuous_variable_stats = True # when in verbose mode, do I output weights/averages for continuous variables?
        self._output_solver_results = False
        self._output_times = False
        self._output_scenario_tree_solution = False

        # PH performance diagnostic parameters and related timing parameters.
        self._profile_memory = 0 # indicates disabled.
        self._time_since_last_garbage_collect = time.time()
        self._minimum_garbage_collection_interval = 5 # units are seconds

        # PH run-time variables
        self._current_iteration = 0 # the 'k'
        self._xbar = {} # current per-variable averages. maps (node_id, variable_name) -> value
        self._initialized = False # am I ready to call "solve"? Set to True by the initialize() method.

        # PH solver information / objects.
        self._solver_type = "cplex" # string indicating the solver type
        self._solver_io = "lp" 
        self._solver_manager_type = "serial" # serial, pyro, and phpyro are the options currently available

        self._solver = None
        self._solver_manager = None

        self._keep_solver_files = False
        self._output_solver_logs = False

        # string to support suffix specification by callbacks
        self._extensions_suffix_list = None

        # PH convergence computer/updater.
        self._converger = None

        # PH history
        self._solutions = {}

        # the checkpoint interval - expensive operation, but worth it for big models.
        # 0 indicates don't checkpoint.
        self._checkpoint_interval = 0

        # all information related to the scenario tree (implicit and explicit).
        self._model = None # not instantiated
        self._model_instance = None # instantiated

        self._scenario_tree = None

        # the source model and instance directories.
        self._model_directory_name = "" 
        self._scenario_data_directory_name = ""

        self._instances = {} # maps scenario name to the corresponding model instance

        # components added to various PH instances during the course of execution. 
        self._instance_ph_variables = {} 
        self._instance_ph_constraints = {} 
        self._instance_ph_linear_expressions = {} # objective terms
        self._instance_ph_quadratic_expressions = {} # objective terms

        # for various reasons (mainly hacks at this point), it's good to know whether we're minimizing or maximizing.
        self._is_minimizing = None

        # global handle to ph extension plugins
        self._ph_plugins = ExtensionPoint(IPHExtension)

        # PH timing statistics - relative to last invocation.
        self._init_start_time = None # for initialization() method
        self._init_end_time = None
        self._solve_start_time = None # for solve() method
        self._solve_end_time = None
        self._cumulative_solve_time = None # seconds, over course of solve()
        self._cumulative_xbar_time = None # seconds, over course of update_xbars()
        self._cumulative_weight_time = None # seconds, over course of update_weights()

        # do I disable warm-start for scenario sub-problem solves during PH iterations >= 1?
        self._disable_warmstarts = False

        # do I drop proximal (quadratic penalty) terms from the weighted objective functions?
        self._drop_proximal_terms = False

        # do I linearize the quadratic penalty term for continuous variables via a
        # piecewise linear approximation? the default should always be 0 (off), as 
        # the user should be aware when they are forcing an approximation.
        self._linearize_nonbinary_penalty_terms = 0

        # the breakpoint distribution strategy employed when linearizing. 0 implies uniform
        # distribution between the variable lower and upper bounds.
        self._breakpoint_strategy = 0

        # do I retain quadratic objective terms associated with binary variables? in general,
        # there is no good reason to not linearize, but just in case, we introduced the option.
        self._retain_quadratic_binary_terms = False

        # PH default tolerances - for use in fixing and testing equality across scenarios,
        # and other stuff.
        self._integer_tolerance = 0.00001

        # PH iteratively solves scenario sub-problems, so we don't want to waste a ton of
        # time preprocessing unless some specific aspects of the scenario instances change.
        # for example, a variable was fixed, the objective was modified, or constraints
        # were added. and if instances do change, we only want to do the minimal amount
        # of work to get the instance back to a consistent "preprocessed" state.
        # the following attributes are introduced to help perform the minimal amount of
        # work, and should be augmented in the future if we can somehow do less.
        # these attributes are initially cleared, and are re-set - following preprocessing, 
        # if necessary - at the top of the PH iteration loop. this gives a chance for 
        # plugins and linearization to get a chance at modification, and to set the 
        # appropriate attributes so that the instances can be appropriately preprocessed
        # before solves for the next iteration commence. we assume (by prefixing the 
        # attribute name with "instance") that modifications of the indicated type have
        # been uniformly applied to all instances.
        self._instance_variables_fixed = False
        self._instance_variables_fixed_detail = {} # maps between instance name and a list of (variable-name, index) pairs
        self._instance_objectives_changed = False # structurally modified
        self._instance_objectives_modified = False # just coefficients modified
        self._instance_piecewise_constraints_modified = False # just coefficients modified

        # PH maintains a mipgap that is applied to each scenario solve that is performed.
        # this attribute can be changed by PH extensions, and the change will be applied
        # on all subsequent solves - until it is modified again. the default is None,
        # indicating unassigned.
        self._mipgap = None

        # when bundling, we cache the extensive form binding instances to save re-generation costs.
        self._bundle_binding_instance_map = {} # maps bundle name in a scenario tree to the binding instance   
        self._bundle_binding_instance_objective_map = {} # maps bundle name in a scenario tree to the original binding instance objective expression
        self._bundle_scenario_instance_map = {} # maps bundle name in a scenario tree to a name->instance map of the scenario instances in the bundle

        # we only store these temporarily...
        scenario_solver_options = None

        # process the keyword options
        self._max_iterations         = options.max_iterations
        self._overrelax              = options.overrelax
        self._nu                     = options.nu
        self._async                  = options.async
        self._async_buffer_len       = options.async_buffer_len
        self._rho                    = options.default_rho
        self._rho_setter             = options.rho_cfgfile
        self._bounds_setter          = options.bounds_cfgfile
        self._solver_type            = options.solver_type
        self._solver_io              = options.solver_io
        self._solver_manager_type    = options.solver_manager_type
        scenario_solver_options      = options.scenario_solver_options
        self._mipgap                 = options.scenario_mipgap
        self._keep_solver_files      = options.keep_solver_files
        self._output_solver_results  = options.output_solver_results
        self._output_solver_logs     = options.output_solver_logs
        self._verbose                = options.verbose
        self._report_solutions       = options.report_solutions
        self._report_weights         = options.report_weights
        self._report_only_statistics = options.report_only_statistics
        self._output_times           = options.output_times
        self._disable_warmstarts     = options.disable_warmstarts
        self._drop_proximal_terms    = options.drop_proximal_terms
        self._retain_quadratic_binary_terms = options.retain_quadratic_binary_terms
        self._linearize_nonbinary_penalty_terms = options.linearize_nonbinary_penalty_terms
        self._breakpoint_strategy    = options.breakpoint_strategy
        self._checkpoint_interval    = options.checkpoint_interval
        self._output_scenario_tree_solution = options.output_scenario_tree_solution
        if hasattr(options, "profile_memory"):
            self._profile_memory = options.profile_memory
        else:
            self._profile_memory = False

        # cache stuff relating to scenario tree manipulation - the ph solver servers may need it.
        self._scenario_bundle_specification = options.scenario_bundle_specification
        self._create_random_bundles = options.create_random_bundles
        self._scenario_tree_random_seed = options.scenario_tree_random_seed

        # validate all "atomic" options (those that can be validated independently)
        if self._max_iterations < 0:
            raise ValueError, "Maximum number of PH iterations must be non-negative; value specified=" + `self._max_iterations`
        if self._rho <= 0.0:
            raise ValueError, "Value of the rho parameter in PH must be non-zero positive; value specified=" + `self._rho`
        if self._nu <= 0.0 or self._nu >= 2:
            raise ValueError, "Value of the nu parameter in PH must be on the interval (0, 2); value specified=" + `self._nu`
        if (self._mipgap is not None) and ((self._mipgap < 0.0) or (self._mipgap > 1.0)):
            raise ValueError, "Value of the mipgap parameter in PH must be on the unit interval; value specified=" + `self._mipgap`

        # validate the linearization (number of pieces) and breakpoint distribution parameters.
        if self._linearize_nonbinary_penalty_terms < 0:
            raise ValueError, "Value of linearization parameter for nonbinary penalty terms must be non-negative; value specified=" + `self._linearize_nonbinary_penalty_terms`
        if self._breakpoint_strategy < 0:
            raise ValueError, "Value of the breakpoint distribution strategy parameter must be non-negative; value specified=" + str(self._breakpoint_strategy)
        if self._breakpoint_strategy > 3:
            raise ValueError, "Unknown breakpoint distribution strategy specified - valid values are between 0 and 2, inclusive; value specified=" + str(self._breakpoint_strategy)

        # validate rho setter file if specified.
        if self._rho_setter is not None:
            if path.exists(self._rho_setter) is False:
                raise ValueError, "The rho setter script file="+self._rho_setter+" does not exist"

        # validate bounds setter file if specified.
        if self._bounds_setter is not None:
            if path.exists(self._bounds_setter) is False:
                raise ValueError, "The bounds setter script file="+self._bounds_setter+" does not exist"

        # validate the checkpoint interval.
        if self._checkpoint_interval < 0:
            raise ValueError, "A negative checkpoint interval with value="+str(self._checkpoint_interval)+" was specified in call to PH constructor"

        # construct the sub-problem solver.
        if self._verbose:
            print "Constructing solver type="+self._solver_type
        self._solver = SolverFactory(self._solver_type, solver_io=self._solver_io)
        if self._solver == None:
            raise ValueError, "Unknown solver type=" + self._solver_type + " specified in call to PH constructor"
        if self._keep_solver_files:
            self._solver.keepFiles = True
        if len(scenario_solver_options) > 0:
            if self._verbose:
                print "Initializing scenario sub-problem solver with options="+str(scenario_solver_options)
            self._solver.set_options("".join(scenario_solver_options))
        if self._output_times:
            self._solver._report_timing = True

        # construct the solver manager.
        if self._verbose:
            print "Constructing solver manager of type="+self._solver_manager_type
        self._solver_manager = SolverManagerFactory(self._solver_manager_type)
        if self._solver_manager is None:
            raise ValueError, "Failed to create solver manager of type="+self._solver_manager_type+" specified in call to PH constructor"

        # a set of all valid PH iteration indicies is generally useful for plug-ins, so create it here.
        self._iteration_index_set = Set(name="PHIterations")
        for i in range(0,self._max_iterations + 1):
            self._iteration_index_set.add(i)

        # spit out parameterization if verbosity is enabled
        if self._verbose:
            print "PH solver configuration: "
            print "   Max iterations=" + `self._max_iterations`
            print "   Async mode=" + str(self._async)
            print "   Async buffer len=" + str(self._async_buffer_len)
            print "   Default global rho=" + `self._rho`
            print "   Over-relaxation enabled="+str(self._overrelax)
            if self._overrelax:
                print "   Nu=" + self._nu              
            if self._rho_setter is not None:
                print "   Rho initialization file=" + self._rho_setter
            if self._bounds_setter is not None:
                print "   Variable bounds initialization file=" + self._bounds_setter
            print "   Sub-problem solver type=" + `self._solver_type`
            print "   Solver manager type=" + `self._solver_manager_type`
            print "   Keep solver files? " + str(self._keep_solver_files)
            print "   Output solver results? " + str(self._output_solver_results)
            print "   Output solver log? " + str(self._output_solver_logs)
            print "   Output times? " + str(self._output_times)
            print "   Checkpoint interval="+str(self._checkpoint_interval)

    """ Initialize PH with model and scenario data, in preparation for solve().
        Constructs and reads instances.
    """
    def initialize(self, model_directory_name=".", scenario_data_directory_name=".", model=None, model_instance=None, scenario_tree=None, converger=None, linearize=False, retain_constraints=False):

        self._init_start_time = time.time()

        print "Initializing PH"
        print ""

        if self._verbose:
            print "   Scenario data directory=" + scenario_data_directory_name

        if not path.exists(scenario_data_directory_name):
            raise ValueError, "Scenario data directory=" + scenario_data_directory_name + " either does not exist or cannot be read"

        self._model_directory_name = model_directory_name
        self._scenario_data_directory_name = scenario_data_directory_name

        # IMPT: The input model should be an *instance*, as it is very useful (critical!) to know
        #       the dimensions of sets, be able to store suffixes on variable values, etc.
        if model is None:
            raise ValueError, "A model must be supplied to the PH initialize() method"

        if scenario_tree is None:
            raise ValueError, "A scenario tree must be supplied to the PH initialize() method"

        if converger is None:
            raise ValueError, "A convergence computer must be supplied to the PH initialize() method"

        self._model = model
        self._model_instance = model_instance
        self._scenario_tree = scenario_tree
        self._converger = converger

        model_objective = model.active_components(Objective)
        self._is_minimizing = (model_objective[ model_objective.keys()[0] ].sense == minimize)

        self._converger.reset()

        # construct the instances for each scenario.
        #
        # garbage collection noticeably slows down PH when dealing with
        # large numbers of scenarios. disable prior to instance construction,
        # and then re-enable. there isn't much collection to do as instances
        # are constructed.

        scenario_instance_construct_start_time = time.time()               
        
        re_enable_gc = gc.isenabled()
        gc.disable()

        if self._verbose:
            if self._scenario_tree._scenario_based_data == 1:
                print "Scenario-based instance initialization enabled"
            else:
                print "Node-based instance initialization enabled"

        for scenario in self._scenario_tree._scenarios:

            scenario_instance = construct_scenario_instance(self._scenario_tree,
                                                            self._scenario_data_directory_name,
                                                            scenario._name,
                                                            self._model,
                                                            self._verbose,
                                                            preprocess=False,
                                                            linearize=linearize)

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

            # do not preprocess the instances here - wait until after the instances
            # have been annotated below by ph-specific parameters. otherwise, these
            # variables will be flagged as in an "undefined" state.

            self._instances[scenario._name] = scenario_instance
            self._instances[scenario._name].name = scenario._name

            self._instance_ph_variables[scenario._name] = []
            self._instance_ph_constraints[scenario._name] = []
            self._instance_ph_linear_expressions[scenario._name] = None
            self._instance_ph_quadratic_expressions[scenario._name] = None
            
            # it would be better to never construct the scenario instances, but we need
            # to determine which variables are used prior to eliminating the constraints.
            # ultimately, we could get this information from the ph

            # if the phpyro solver manager is enabled, there is no need for the scenario instances
            # to have constraints instantiated - they are never referenced, therefore wasting memory
            # and construction time. the easiest way to accomplish this is to eliminate the
            # the Constraint components from the reference model, prior to scenario instance construction.            
            if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
                # TBD: we technically only have to execute the identify_variables preprocessor -
                # this will save significant time. and maybe not even that preprocessor.
                scenario_instance.preprocess()
                if retain_constraints:
                    print "***WARNING: Retaining instance constraints when executing phpyro solver manager - could lead to excessive memory requirements"
                else:
                    cull_constraints_from_instance(scenario_instance)            

        # perform a single pass of garbage collection and re-enable automatic collection.
        if re_enable_gc:
            if (time.time() - self._time_since_last_garbage_collect) >= self._minimum_garbage_collection_interval:
               gc.collect()
               self._time_since_last_garbage_collect = time.time()
            gc.enable()

        scenario_instance_construct_end_time = time.time()
        if self._output_times:
            print "PH scenario instance construction time=%.2f seconds" % (scenario_instance_construct_end_time - scenario_instance_construct_start_time)

        # with the scenario instances now available, have the scenario tree 
        # compute the variable match indices at each node.
        self._scenario_tree.defineVariableIndexSets(self._instances)

        # let plugins know if they care - this callback point allows
        # users to create/modify the original scenario instances and/or
        # the scenario tree prior to creating PH-related parameters,
        # variables, and the like.
        for plugin in self._ph_plugins:
            plugin.post_instance_creation(self)

        # create ph-specific parameters (weights, xbar, etc.) for each instance.
        if self._verbose:
            print "Creating weight, average, and rho parameter vectors for scenario instances"
        scenario_ph_parameters_start_time = time.time()       
        self._create_scenario_ph_parameters()
        scenario_ph_parameters_end_time = time.time()       
        if self._output_times:
            print "PH parameter vector construction time=%.2f seconds" % (scenario_ph_parameters_end_time - scenario_ph_parameters_start_time)

        # if specified, run the user script to initialize variable rhos at their whim.
        if self._rho_setter is not None:
            print "Executing user rho set script from filename="+self._rho_setter
            execfile(self._rho_setter)

        # with the instances created, run the user script to initialize variable bounds.
        if self._bounds_setter is not None:
            print "Executing user variable bounds set script from filename=", self._bounds_setter
            execfile(self._bounds_setter)

        # at this point, the instances are complete - preprocess them!
        # BUT: only if the phpyro solver manager isn't in use.
        if not isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):        
            if self._verbose:
                print "Preprocessing scenario instances"
            scenario_instance_preprocess_start_time = time.time()
            for scenario_name, scenario_instance in self._instances.iteritems():
                scenario_instance.preprocess()
            scenario_instance_preprocess_end_time = time.time()
            if self._output_times:
                print "Scenario instance preprocessing time=%.2f seconds" % (scenario_instance_preprocess_end_time - scenario_instance_preprocess_start_time)

        # the instances have been preprocessed at this point. any subsequent 
        # modification(s) will trigger subsequent preprocessing prior to solves.
        self._instance_variables_fixed = False
        for (instance_name, instance) in self._instances.iteritems():
            self._instance_variables_fixed_detail[instance_name] = []
        self._instance_objectives_changed = False
        self._instance_objectives_modified = False
        self._instance_piecewise_constraints_modified = False

        # create parameters to store variable statistics (of general utility) at each node in the scenario tree.

        if self._verbose:
            print "Creating variable statistic (min/avg/max) parameter vectors for scenario tree nodes"

        scenario_tree_variable_stats_start_time = time.time()

        # process all stages, simply for completeness, i.e., to create a fully populated scenario tree.
        for stage in scenario_tree._stages:

            instance_variables = {}          # map between variable names and the variable in the reference model
            instance_variable_templates = {} # map between variable names and a list of index match templates 

            for variable_name in stage._variables.iterkeys():

                # create min/avg/max parameters for each variable in the corresponding tree node.
                # NOTE: the parameter names below could really be empty, as they are never referenced
                #       explicitly.
                for tree_node in stage._tree_nodes:

                    match_indices = tree_node._variable_indices[variable_name]

                    tree_node._minimums[variable_name] = dict(((x,0) for x in match_indices))
                    # this is the true variable average at the node (unmodified)
                    tree_node._averages[variable_name] = dict(((x,0) for x in match_indices))
                    # this is the xbar used in the PH objective.                  
                    tree_node._xbars[variable_name] = dict(((x,0) for x in match_indices))
                    tree_node._maximums[variable_name] = dict(((x,0) for x in match_indices))

        scenario_tree_variable_stats_end_time = time.time()

        if self._output_times:
            print "Variable statistics parameter construction time=%.2f seconds" % (scenario_tree_variable_stats_end_time - scenario_tree_variable_stats_start_time)

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

        # cache the number of discrete and continuous variables in the master instance. this value
        # is of general use, e.g., in the converger classes and in plugins.
        (self._total_discrete_vars,self._total_continuous_vars) = self.compute_blended_variable_counts()
        if self._verbose:
            print "Total number of discrete instance variables="+str(self._total_discrete_vars)
            print "Total number of continuous instance variables="+str(self._total_continuous_vars)

        # track the total number of fixed variables of each category at the end of each PH iteration.
        (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

        # indicate that we're ready to run.
        self._initialized = True

        if self._verbose:
            print "PH successfully created model instances for all scenarios"

        if (self._scenario_tree.contains_bundles() is True) and (not isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro)):
            self._form_bundle_binding_instances()

        if self._verbose:
            print "PH is successfully initialized"

        # let plugins know if they care.
        if self._verbose:
            print "Initializing PH plugins"
        for plugin in self._ph_plugins:
            plugin.post_ph_initialization(self)
        if self._verbose:
            print "PH plugin initialization complete"

        # if using the phpyro solver manager, initialize the ph solver servers and send any variable bounds across.
        if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
            
            self._initialize_ph_solver_servers()
            if self._verbose:
                print "PH solver servers successfully initialized"

            if self._bounds_setter is not None:
                self._transmit_bounds()
                if self._verbose:
                    print "Successfully transmitted variable bounds to PH solver servers"

        self._init_end_time = time.time()
        if self._output_times:
            print "Overall initialization time=%.2f seconds" % (self._init_end_time - self._init_start_time)
            print ""


    """ Perform the non-weighted scenario solves and form the initial w and xbars.
    """
    def iteration_0_solves(self):
        # return None unless a sub-problem failure is detected, then return its name immediately

        if self._verbose:
            print "------------------------------------------------"
            print "Starting PH iteration 0 solves"

        iteration_start_time = time.time()

        # STEP 0: set up all global solver options.
        if self._mipgap is not None:
            self._solver.options.mipgap = float(self._mipgap)

        # STEP 0.25: scan any variables fixed prior to iteration 0, set
        #            up the appropriate flags for pre-processing, and - if
        #            appropriate - transmit the information to the PH 
        #            solver servers.
        self._instance_variables_fixed = False # until proven otherwise
        for instance_name, fixed_variable_list in self._instance_variables_fixed_detail.iteritems():
            if len(fixed_variable_list) > 0:
                self._instance_variables_fixed = True

        if self._instance_variables_fixed and isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
            self._transmit_fixed_variables()

        # STEP 0.5: preprocess all scenario instances, as needed.
        #           if a PH pyro solver manager is being used, skip this step -
        #           the instances are never written, so need for preprocessing.
        if not isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
            self._preprocess_scenario_instances()

        # STEP 0.75: now that we're preprocessed, clear the fixed variable status.
        self._instance_variables_fixed = False
        for instance_name in self._instances.iterkeys():
            self._instance_variables_fixed_detail[instance_name] = []        

        # STEP 1: queue up the solves for all scenario sub-problems and

        # we could use the same names for scenarios and bundles, but we are easily confused.
        scenario_action_handle_map = {} # maps scenario names to action handles
        action_handle_scenario_map = {} # maps action handles to scenario names

        bundle_action_handle_map = {} # maps bundle names to action handles
        action_handle_bundle_map = {} # maps action handles to bundle names

        # if running the phpyro solver server, we need to ship the solver options across the pipe.
        if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):        
            solver_options = {}
            for key in self._solver.options:
                solver_options[key]=self._solver.options[key]

        if self._scenario_tree.contains_bundles():

            for scenario_bundle in self._scenario_tree._scenario_bundles:

              if self._verbose:
                  print "Queuing solve for scenario bundle="+scenario_bundle._name

              if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro) is False:

                  # preprocess the ef binding instance - the scenario instances should be taken care of previously.
                  bundle_ef_instance = self._bundle_binding_instance_map[scenario_bundle._name]
                  bundle_scenario_instance_map = self._bundle_scenario_instance_map[scenario_bundle._name]
                  bundle_ef_instance.preprocess() # TBD - I THINK THIS PRESENTLY WORKS RECURSIVELY - IT SHOULD JUST DO THE OBJECTIVE.                                                      

              # and queue it up for solution - nothing to warm-start from at iteration 0.

              if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
                  new_action_handle = self._solver_manager.queue(action="solve",
                                                                 name=scenario_bundle._name,
                                                                 tee=self._output_solver_logs, 
                                                                 verbose=self._verbose, 
                                                                 solver_options=solver_options,
                                                                 breakpoint_strategy=self._breakpoint_strategy,
                                                                 integer_tolerance=self._integer_tolerance)
              else:
                  # if running silent but with timing enabled, output some information regarding which
                  # scenario instance is being processed, to provide some context for the timing information
                  # being reported by solver plugins.
                  if (self._output_times is True) and (self._verbose is False):
                      print "Solver manager queuing instance=%s" % (scenario_bundle._name)
                  new_action_handle = self._solver_manager.queue(bundle_ef_instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose)

              bundle_action_handle_map[scenario_bundle._name] = new_action_handle
              action_handle_bundle_map[new_action_handle] = scenario_bundle._name 

        else:

           for scenario in self._scenario_tree._scenarios:

              instance = self._instances[scenario._name]

              if self._verbose:
                  print "Queuing solve for scenario=" + scenario._name

              # there's nothing to warm-start from in iteration 0, so don't include the keyword in the solve call.
              # the reason you don't want to include it is that some solvers don't know how to handle the keyword
              # at all (despite it being false). you might want to solve iteration 0 solves using some other solver.

              if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
                  new_action_handle = self._solver_manager.queue(action="solve", 
                                                                name=scenario._name, 
                                                                tee=self._output_solver_logs, 
                                                                verbose=self._verbose, 
                                                                solver_options=solver_options,
                                                                breakpoint_strategy=self._breakpoint_strategy,
                                                                integer_tolerance=self._integer_tolerance)
              else:
                  if (self._output_times is True) and (self._verbose is False):
                      print "Solver manager queuing instance=%s" % (scenario._name)                  
                  if self._extensions_suffix_list is not None:
                      new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose, suffixes=self._extensions_suffix_list)
                  else:
                      new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose)
              scenario_action_handle_map[scenario._name] = new_action_handle
              action_handle_scenario_map[new_action_handle] = scenario._name

        # STEP 2: loop for the solver results, reading them and loading
        #         them into instances as they are available.

        if self._scenario_tree.contains_bundles():

            if self._verbose:
                print "Waiting for bundle sub-problem solves"

            num_results_so_far = 0

            while (num_results_so_far < len(self._scenario_tree._scenario_bundles)):

                bundle_action_handle = self._solver_manager.wait_any()
                bundle_results = self._solver_manager.get_results(bundle_action_handle)
                bundle_name = action_handle_bundle_map[bundle_action_handle]
                
                if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):                

                    if self._output_solver_results:
                        print "Results for scenario bundle="+bundle_name+":"
                        print bundle_results

                    if len(bundle_results) == 0:
                        if self._verbose:
                            print "Solve failed for scenario bundle="+bundle_name+"; no solutions generated"
                        return bundle_name

                    for scenario_name, instance_results in bundle_results.iteritems():
                        self._load_variable_values(self._instances[scenario_name], instance_results)
 
                else:

                    # a temporary hack - if results come back from pyro, they won't
                    # have a symbol map attached. so create one.
                    if bundle_results._symbol_map is None:
                        bundle_results._symbol_map = symbol_map_from_instance(bundle_instance)

                    bundle_instance = self._bundle_binding_instance_map[bundle_name]                

                    if self._verbose:
                        print "Results obtained for bundle="+bundle_name

                    if len(bundle_results.solution) == 0:
                        if self._verbose:
                            print "Solve failed for scenario bundle="+bundle_name+"; no solutions generated"
                        return bundle_name
 
                    if self._output_solver_results:
                        print "Results for bundle=",bundle_name
                        bundle_results.write(num=1)

                    start_time = time.time()
                    bundle_instance.load(bundle_results)
                    end_time = time.time()
                    if self._output_times:
                        print "Time loading results for bundle %s=%0.2f seconds" % (bundle_name, end_time-start_time)

                if self._verbose:
                    print "Successfully loaded solution for bundle="+bundle_name

                num_results_so_far = num_results_so_far + 1

        else:

            if self._verbose:
                print "Waiting for scenario sub-problem solves"

            num_results_so_far = 0

            while (num_results_so_far < len(self._scenario_tree._scenarios)):

                action_handle = self._solver_manager.wait_any()
                results = self._solver_manager.get_results(action_handle)
                scenario_name = action_handle_scenario_map[action_handle]
                instance = self._instances[scenario_name]

                if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):                

                    if self._output_solver_results:
                        print "Results for scenario=",scenario_name
                        print results

                    self._load_variable_values(instance, results)
                else:
                    # a temporary hack - if results come back from pyro, they won't
                    # have a symbol map attached. so create one.
                    if results._symbol_map is None:
                        results._symbol_map = symbol_map_from_instance(instance)

                    if self._verbose:
                        print "Results obtained for scenario="+scenario_name

                    if len(results.solution) == 0:
                        if self._verbose:
                            print "Solve failed for scenario="+scenario_name+"; no solutions generated"
                        return scenario_name

                    if self._output_solver_results:
                        print "Results for scenario=",scenario_name
                        results.write(num=1)

                    start_time = time.time()
                    instance.load(results)
                    end_time = time.time()
                    if self._output_times:
                        print "Time loading results into instance %s=%0.2f seconds" % (scenario_name, end_time-start_time)

                if self._verbose:
                    print "Successfully loaded solution for scenario="+scenario_name

                num_results_so_far = num_results_so_far + 1

        ###############################
        # STEP 3: Summarize results
        ###############################

        if self._verbose:
            print "Scenario sub-problem solves completed"

        iteration_end_time = time.time()
        self._cumulative_solve_time += (iteration_end_time - iteration_start_time)

        if self._output_times:
            print "Total time this PH iteration=%.2f seconds" % (iteration_end_time - iteration_start_time)
            print ""

        if self._verbose:
            print "Successfully completed PH iteration 0 solves - solution statistics:"
            print "         Scenario              Objective                  Value"
            for scenario in self._scenario_tree._scenarios:
                instance = self._instances[scenario._name]
                for objective_name in instance.active_components(Objective):
                    objective = instance.active_components(Objective)[objective_name]
                    print "%20s       %15s     %14.4f" % (scenario._name, objective.name, objective._data[None].expr())
            print "------------------------------------------------"

    #
    # recompute the averages, minimum, and maximum statistics for all variables to be blended by PH, i.e.,
    # not appearing in the final stage. technically speaking, the min/max aren't required by PH, but they
    # are used often enough to warrant their computation and it's basically free if you're computing the
    # average.
    #

    def update_variable_statistics(self):

        start_time = time.time()

        # NOTE: the following code has some optimizations that are not normally recommended, in particular
        #       the direct access and manipulation of parameters via the .value attribute instead of the
        #       user-level-preferred value() method. this is justifiable in this particular instance
        #       because we are creating the PH parameters (and therefore can manipulate them safely), and
        #       this routine takes a non-trivial amount of the overall run-time.

        # cache the lookups - don't want to do them deep in the index loop.
        overrelax = self._overrelax
        current_iteration = self._current_iteration

        # compute statistics over all stages, even the last. this is necessary in order to
        # successfully snapshot a scenario tree solution from the average values.
        for stage in self._scenario_tree._stages:

            for tree_node in stage._tree_nodes:

                tree_node_instances = [self._instances[scenario._name] for scenario in tree_node._scenarios]

                for variable_name, variable_indices in tree_node._variable_indices.iteritems():

                    avg_parameter_name = "PHAVG_"+variable_name
                    xbar_parameter_name = "PHXBAR_"+variable_name

                    tree_node_var_mins = tree_node._minimums[variable_name]
                    tree_node_var_avgs = tree_node._averages[variable_name]
                    tree_node_var_maxs = tree_node._maximums[variable_name]

                    tree_node_var_xbars = tree_node._xbars[variable_name]

                    scenario_variables = [getattr(instance, variable_name) for instance in tree_node_instances]

                    for index in variable_indices:

                        min = float("inf")
                        avg = 0.0
                        max = float("-inf")
                        node_probability = 0.0

                        is_used = True # until proven otherwise
                        for scenario_variable in scenario_variables:

                            if scenario_variable[index].status == VarStatus.unused:
                                is_used = False
                            else:
                                node_probability += scenario._probability
                                var_value = scenario_variable[index].value
                                if var_value < min:
                                    min = var_value
                                avg += (scenario._probability * var_value)
                                if var_value > max:
                                    max = var_value

                        if is_used:

                            tree_node_var_mins[index] = min
                            tree_node_var_avgs[index] = avg / node_probability
                            tree_node_var_maxs[index] = max

                            if (overrelax is True) and (current_iteration >= 1):
                               tree_node_var_xbars[index] = self._nu * tree_node_var_avgs[index]+ (1-self._nu) * tree_node_var_xbars[index]
                            else:                                
                               tree_node_var_xbars[index] = tree_node_var_avgs[index]

                            # distribute the newly computed average to the xbar variable in
                            # each instance/scenario associated with this node. only do this
                            # if the variable is used!
                            for instance in tree_node_instances:
                                # TBD: Why is this in a try block? Seems like a really dangerous/bad idea.
                                try:
                                    #  TBD: The getattr should be eliminated this deep in the code - the store and extract should be in bulk
                                    avg_parameter = getattr(instance, avg_parameter_name)
                                    xbar_parameter = getattr(instance, xbar_parameter_name)
                                    avg_parameter[index].value = tree_node_var_avgs[index]
                                    xbar_parameter[index].value = tree_node_var_xbars[index]
                                except:
                                    pass

        end_time = time.time()
        self._cumulative_xbar_time += (end_time - start_time)

        if self._output_times:
            print "Variable statistics compute time=%.2f seconds" % (end_time - start_time)       

    def update_weights(self):

        start_time = time.time()

        # because the weight updates rely on the xbars, and the xbars are node-based,
        # I'm looping over the tree nodes and pushing weights into the corresponding scenarios.
        start_time = time.time()

        # NOTE: the following code has some optimizations that are not normally recommended, in particular
        #       the direct access and manipulation of parameters via the .value attribute instead of the
        #       user-level-preferred value() method. this is justifiable in this particular instance
        #       because we are creating the PH parameters (and therefore can manipulate them safely), and
        #       this routine takes a non-trivial amount of the overall run-time.

        # cache the lookups - don't want to do them deep in the index loop.
        over_relaxing = self._overrelax
        is_minimizing = self._is_minimizing

        for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage, so no weights to worry about.

            for tree_node in stage._tree_nodes:

                for variable_name, variable_indices in tree_node._variable_indices.iteritems():

                    blend_parameter_name = "PHBLEND_"+variable_name
                    weight_parameter_name = "PHWEIGHT_"+variable_name
                    rho_parameter_name = "PHRHO_"+variable_name

                    for scenario in tree_node._scenarios:

                        instance = self._instances[scenario._name]

                        weight_parameter = getattr(instance, weight_parameter_name)
                        rho_parameter = getattr(instance, rho_parameter_name)
                        blend_parameter = getattr(instance, blend_parameter_name)

                        weight_values = weight_parameter.extract_values()
                        rho_values = rho_parameter.extract_values()
                        blend_values = blend_parameter.extract_values()                        

                        instance_variable = getattr(instance, variable_name)
                        variable_values = instance_variable.extract_values()

                        new_weight_values = {}

                        tree_node_averages = tree_node._averages[variable_name]

                        for index in variable_indices:

                            tree_node_average = tree_node_averages[index]

                            if instance_variable[index].status != VarStatus.unused:

                                # we are currently not updating weights if blending is disabled for a variable.
                                # this is done on the premise that unless you are actively trying to move
                                # the variable toward the mean, the weights will blow up and be huge by the
                                # time that blending is activated.

                                nu_value = 1.0
                                if over_relaxing:
                                    nu_value = self._nu
                                    
                                current_variable_weight = weight_values[index]

                                # if I'm maximizing, invert value prior to adding (hack to implement negatives).
                                # probably fixed in Pyomo at this point - I just haven't checked in a long while.
                                if is_minimizing is False:
                                    current_variable_weight = (-current_variable_weight)

                                new_variable_weight = current_variable_weight + blend_values[index] * rho_values[index] * nu_value * (variable_values[index] - tree_node_average)
                                
                                # I have the correct updated value, so now invert if maximizing.
                                if is_minimizing is False:
                                    new_variable_weight = (-new_variable_weight)

                                new_weight_values[index] = new_variable_weight

                        # store the computed weights in bulk, for efficiency.
                        weight_parameter.store_values(new_weight_values)

        end_time = time.time()
        self._cumulative_weight_time += (end_time - start_time)

        if self._output_times:
            print "Weight update time=%.2f seconds" % (end_time - start_time)       

    def update_weights_for_scenario(self, instance):

        start_time = time.time()

        scenario = self._scenario_tree.get_scenario(instance.name)

        for tree_node in scenario._node_list[:-1]:

            for variable_name, variable_indices in tree_node._variable_indices.iteritems():

                blend_parameter_name = "PHBLEND_"+variable_name
                weight_parameter_name = "PHWEIGHT_"+variable_name
                rho_parameter_name = "PHRHO_"+variable_name

                blend_parameter = getattr(instance, blend_parameter_name)
                weight_parameter = getattr(instance, weight_parameter_name)
                rho_parameter = getattr(instance, rho_parameter_name)
  
                tree_node_averages = tree_node._averages[variable_name]

                instance_variable = getattr(instance, variable_name)

                for index in variable_indices:

                    tree_node_average = tree_node_averages[index] # these are float values

                    if instance_variable[index].status != VarStatus.unused:

                        # we are currently not updating weights if blending is disabled for a variable.
                        # this is done on the premise that unless you are actively trying to move
                        # the variable toward the mean, the weights will blow up and be huge by the
                        # time that blending is activated.
                        variable_blend_indicator = blend_parameter[index].value

                        # get the weight and rho parameters for this variable/index combination.
                        rho_value = rho_parameter[index].value
                        current_variable_weight = weight_parameter[index].value

                        # if I'm maximizing, invert value prior to adding (hack to implement negatives).
                        # probably fixed in Pyomo at this point - I just haven't checked in a long while.
                        if self._is_minimizing is False:
                            current_variable_weight = (-current_variable_weight)
                        current_variable_value = instance_variable[index]()
                        new_variable_weight = current_variable_weight + variable_blend_indicator * rho_value * (current_variable_value - tree_node_average)
                        # I have the correct updated value, so now invert if maximizing.
                        if self._is_minimizing is False:
                            new_variable_weight = (-new_variable_weight)
                        weight_parameter[index].value = new_variable_weight

        end_time = time.time()
        self._cumulative_weight_time += (end_time - start_time)

    def form_ph_objectives(self):

        start_time = time.time()

        for instance_name, instance in self._instances.items():

            new_lin_terms, new_quad_terms = form_ph_objective(instance_name, \
                                                              instance, \
                                                              self._original_objective_expression[instance_name], \
                                                              self._scenario_tree, \
                                                              self._linearize_nonbinary_penalty_terms, \
                                                              self._drop_proximal_terms, \
                                                              self._retain_quadratic_binary_terms)

            self._instance_ph_linear_expressions[instance_name] = new_lin_terms
            self._instance_ph_quadratic_expressions[instance_name] = new_quad_terms      

        self._instance_objectives_changed = True

        end_time = time.time()

        if self._output_times:
            print "PH objective formation time=%.2f seconds" % (end_time - start_time)       

    def form_ph_linearized_objective_constraints(self):

        start_time = time.time()

        for instance_name, instance in self._instances.iteritems():

            new_attrs = form_linearized_objective_constraints(instance_name, \
                                                              instance, \
                                                              self._scenario_tree, \
                                                              self._linearize_nonbinary_penalty_terms, \
                                                              self._breakpoint_strategy, \
                                                              self._integer_tolerance)

            self._instance_ph_constraints[instance_name].extend(new_attrs)

        end_time = time.time()

        self._instance_piecewise_constraints_modified = True

        if self._output_times:
            print "PH linearized objective constraint formation time=%.2f seconds" % (end_time - start_time)       

    def iteration_k_solves(self):

        if self._verbose:
            print "------------------------------------------------"
            print "Starting PH iteration " + str(self._current_iteration) + " solves"

        # cache the objective values generated by PH for output at the end of this function.
        ph_objective_values = {}

        iteration_start_time = time.time()

        # STEP -1: if using a PH solver manager, propagate current weights/averages to the appropriate solver servers.
        #          ditto the tree node statistics, which are necessary if linearizing (so an optimization could be
        #          performed here).
        # NOTE: We aren't currently propagating rhos, as they generally don't change - we need to
        #       have a flag, though, indicating whether the rhos have changed, so they can be
        #       transmitted if needed.
        if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):        
            self._transmit_weights_and_averages()
            self._transmit_tree_node_statistics()

        # if using a PH solver server, trasnsmit the rhos prior to the execution
        # of PH iteration 1. for now, we are assuming that the rhos don't change
        # on a per-iteration basis, but that assumption can be easily relaxed.
        # it is important to do this after the plugins have a chance to do their
        # computation.
        if (isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro) is True) and (self._current_iteration == 1):
            self._transmit_rhos()
            self._enable_ph_objectives()

        # STEP 0: set up all global solver options.
        if self._mipgap is not None:
            self._solver.options.mipgap = float(self._mipgap)

        # STEP 0.25: scan any variables fixed prior to iteration 0, set
        #            up the appropriate flags for pre-processing, and - if
        #            appropriate - transmit the information to the PH 
        #            solver servers.

        self._instance_variables_fixed = False # until proven otherwise
        for instance_name, fixed_variable_list in self._instance_variables_fixed_detail.iteritems():
            if len(fixed_variable_list) > 0:
                self._instance_variables_fixed = True

        if self._instance_variables_fixed and isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
            self._transmit_fixed_variables()

        # STEP 0.5: preprocess all scenario instances, if needed.
        #           if a PH pyro solver manager is being used, skip this step -
        #           the instances are never written, so need for preprocessing.
        if not isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):        

            # TBD: by default, assume we are *not* going to re-generate the AMPL representations within
            #      the NL writer - self._preprocess_scenario_instances() may over-ride these values as needed.
            if (self._solver_type == "asl") or (self._solver_type == "ipopt"):
                for scenario_name, scenario_instance in self._instances.iteritems():
                    # this is kludgy until we make workflows explicit in Coopr - the NL writer combines writing and
                    # preprocessing, so all we can do is tag the instance with an appropriate attribute.
                    setattr(scenario_instance, "gen_obj_ampl_repn", False)
                    setattr(scenario_instance, "gen_con_ampl_repn", False) 

            self._preprocess_scenario_instances()

        # STEP 0.75: now that we're preprocessed, clear the fixed variable status.
        self._instance_variables_fixed = False
        for instance_name in self._instances.iterkeys():
            self._instance_variables_fixed_detail[instance_name] = []        

        # STEP 0.85: if linearizing the PH objective, clear the values for any PHQUADPENALTY*
        #            variables - otherwise, the MIP starts are likely to be infeasible.
        if self._linearize_nonbinary_penalty_terms > 0:
           self._reset_instance_linearization_variables()

        # STEP 1: queue up the solves for all scenario sub-problems and

        # we could use the same names for scenarios and bundles, but we are easily confused.
        scenario_action_handle_map = {} # maps scenario names to action handles
        action_handle_scenario_map = {} # maps action handles to scenario names

        bundle_action_handle_map = {} # maps bundle names to action handles
        action_handle_bundle_map = {} # maps action handles to bundle names

        # if running the phpyro solver server, we need to ship the solver options across the pipe.
        if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):        
            solver_options = {}
            for key in self._solver.options:
                solver_options[key]=self._solver.options[key]

        if self._scenario_tree.contains_bundles():

            # clear non-converged variables and stage cost variables, to ensure feasible warm starts.
            reset_nonconverged_variables(self._scenario_tree, self._instances)
            reset_stage_cost_variables(self._scenario_tree, self._instances)

            for scenario_bundle in self._scenario_tree._scenario_bundles:

              if self._verbose:
                  print "Queuing solve for scenario bundle="+scenario_bundle._name

              if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro) is False:                  

                  bundle_scenario_instance_map = self._bundle_scenario_instance_map[scenario_bundle._name]
                  bundle_ef_instance = self._bundle_binding_instance_map[scenario_bundle._name]

                  # restore the original EF objective.
                  bundle_ef_objectives = bundle_ef_instance.active_components(Objective)
                  objective_name = bundle_ef_objectives.keys()[0]
                  bundle_ef_objective = bundle_ef_objectives[objective_name]
                  bundle_ef_objective._data[None].expr = self._bundle_binding_instance_objective_map[scenario_bundle._name]

                  # augment the EF objective with the PH penalty terms for each composite scenario.
                  for scenario_name in scenario_bundle._scenario_names:
                     new_lin_terms = self._instance_ph_linear_expressions[scenario_name] # TBD - don't need to split linear and quadratic!
                     new_quad_terms = self._instance_ph_quadratic_expressions[scenario_name]
                     scenario = self._scenario_tree._scenario_map[scenario_name]
                     # TBD: THIS SHOULD NOT HAVE TO BE DONE EACH ITERATION - THE OBJECTIVE STRUCTURE DOES NOT CHANGE, AND THE LINEARIZATION 
                     #      CONSTRAINTS ARE ON THE SCENARIO INSTANCES.
                     bundle_ef_objective._data[None].expr += (scenario._probability / scenario_bundle._probability) * (new_lin_terms)
                     bundle_ef_objective._data[None].expr += (scenario._probability / scenario_bundle._probability) * (new_quad_terms) 

                  # preprocess all scenario instances and the ef instance first, in that order.
                  bundle_scenario_instance_map = self._bundle_scenario_instance_map[scenario_bundle._name]
                  bundle_ef_instance = self._bundle_binding_instance_map[scenario_bundle._name]
                  bundle_ef_instance.preprocess()
              
              # and queue it up for solution - have to worry about warm-startig here.
              new_action_handle = None
              if (self._disable_warmstarts is False) and (self._solver.warm_start_capable() is True):
                 if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
                     new_action_handle = self._solver_manager.queue(action="solve", 
                                                                    name=scenario_bundle._name, 
                                                                    tee=self._output_solver_logs, 
                                                                    verbose=self._verbose, 
                                                                    solver_options=solver_options, 
                                                                    breakpoint_strategy=self._breakpoint_strategy,
                                                                    integer_tolerance=self._integer_tolerance,
                                                                    warmstart=True)                        
                 else:
                     if (self._output_times is True) and (self._verbose is False):
                         print "Solver manager queuing instance=%s" % (scenario_bundle._name)                     
                     new_action_handle = self._solver_manager.queue(bundle_ef_instance, opt=self._solver, warmstart=True, tee=self._output_solver_logs, verbose=self._verbose)                     
              else:
                 if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
                     new_action_handle = self._solver_manager.queue(action="solve", 
                                                                    name=scenario_bundle._name, 
                                                                    tee=self._output_solver_logs, 
                                                                    verbose=self._verbose, 
                                                                    solver_options=solver_options,
                                                                    breakpoint_strategy=self._breakpoint_strategy,
                                                                    integer_tolerance=self._integer_tolerance)
                 else:
                     if (self._output_times is True) and (self._verbose is False):
                         print "Solver manager queuing instance=%s" % (scenario_bundle._name)                                          
                     bundle_ef_instance.preprocess()                     
                     new_action_handle = self._solver_manager.queue(bundle_ef_instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose)
              bundle_action_handle_map[scenario_bundle._name] = new_action_handle
              action_handle_bundle_map[new_action_handle] = scenario_bundle._name 

        else:

            # clear stage cost variables, to ensure feasible warm starts.
            reset_stage_cost_variables(self._scenario_tree, self._instances)

            for scenario in self._scenario_tree._scenarios:

                instance = self._instances[scenario._name]

                if self._verbose:
                    print "Queuing solve for scenario=" + scenario._name

                # once past iteration 0, there is always a feasible solution from which to warm-start.
                # however, you might want to disable warm-start when the solver is behaving badly (which does happen).
                new_action_handle = None
                if (self._disable_warmstarts is False) and (self._solver.warm_start_capable() is True):
                    if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):                            
                        new_action_handle = self._solver_manager.queue(action="solve", 
                                                                       name=scenario._name, 
                                                                       warmstart=True, 
                                                                       tee=self._output_solver_logs, 
                                                                       verbose=self._verbose, 
                                                                       solver_options=solver_options,
                                                                       breakpoint_strategy=self._breakpoint_strategy,
                                                                       integer_tolerance=self._integer_tolerance)
                    else:
                        if (self._output_times is True) and (self._verbose is False):
                            print "Solver manager queuing instance=%s" % (scenario._name)                                                                  
                        if self._extensions_suffix_list is not None:
                            new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=True, tee=self._output_solver_logs, verbose=self._verbose, suffixes=self._extensions_suffix_list)
                        else:
                            new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=True, tee=self._output_solver_logs, verbose=self._verbose)
                else:
                    if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):                                                
                        new_action_handle = self._solver_manager.queue(action="solve", 
                                                                       name=scenario._name, 
                                                                       tee=self._output_solver_logs, 
                                                                       verbose=self._verbose, 
                                                                       solver_options=solver_options,
                                                                       breakpoint_strategy=self._breakpoint_strategy,
                                                                       integer_tolerance=self._integer_tolerance)
                    else:
                        if (self._output_times is True) and (self._verbose is False):
                            print "Solver manager queuing instance=%s" % (scenario._name)                                                                                          
                        if self._extensions_suffix_list is not None:
                            new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose, suffixes=self._extensions_suffix_list)
                        else:
                            new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose)

                scenario_action_handle_map[scenario._name] = new_action_handle
                action_handle_scenario_map[new_action_handle] = scenario._name

        # STEP 2: loop for the solver results, reading them and loading
        #         them into instances as they are available.

        if self._scenario_tree.contains_bundles():

            if self._verbose:
                print "Waiting for bundle sub-problem solves"

            num_results_so_far = 0

            while (num_results_so_far < len(self._scenario_tree._scenario_bundles)):

                bundle_action_handle = self._solver_manager.wait_any()
                bundle_results = self._solver_manager.get_results(bundle_action_handle)
                bundle_name = action_handle_bundle_map[bundle_action_handle]
                
                if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):                

                    if self._output_solver_results:
                        print "Results for scenario bundle="+bundle_name+":"
                        print bundle_results

                    if len(bundle_results) == 0:
                        if self._verbose:
                            print "Solve failed for scenario bundle="+bundle_name+"; no solutions generated"
                        return bundle_name

                    for scenario_name, instance_results in bundle_results.iteritems():
                        self._load_variable_values(self._instances[scenario_name], instance_results)
 
                else:                

                    # a temporary hack - if results come back from pyro, they won't
                    # have a symbol map attached. so create one.
                    if bundle_results._symbol_map is None:
                        bundle_results._symbol_map = symbol_map_from_instance(bundle_instance)

                    bundle_instance = self._bundle_binding_instance_map[bundle_name]

                    if self._verbose:
                        print "Results obtained for bundle="+bundle_name

                    if len(bundle_results.solution) == 0:
                        bundle_results.write(num=1)
                        raise RuntimeError, "Solve failed for bundle="+bundle_name+"; no solutions generated"

                    if self._output_solver_results:
                        print "Results for bundle=",bundle_name
                        bundle_results.write(num=1)

                    start_time = time.time()
                    bundle_instance.load(bundle_results)
                    end_time = time.time()
                    
                    if self._output_times:
                        print "Time loading results for bundle %s=%0.2f seconds" % (bundle_name, end_time-start_time)

                if self._verbose:
                    print "Successfully loaded solution for bundle="+bundle_name

                # TBD: LOOK AT THE CODE BELOW FOR NON-BUNDLE CASE - WE NEED TO SOMEHOW REPORT THE PH OBJECTIVES FOR THE SCENARIO PH COSTS?

                for instance_name in self._instances.keys():
                   ph_objective_values[instance_name] = 0.0                

                num_results_so_far = num_results_so_far + 1

        else:

            if self._verbose:
                print "Waiting for scenario sub-problem solves"

            num_results_so_far = 0

            while (num_results_so_far < len(self._scenario_tree._scenarios)):

                action_handle = self._solver_manager.wait_any()
                results = self._solver_manager.get_results(action_handle)
                scenario_name = action_handle_scenario_map[action_handle]
                instance = self._instances[scenario_name]

                # TBD: This won't work for bundling yet - there is a hierarchy of names,
                #      and we'll have to impose a scenario-variable naming convention on
                #      the solver server side.
                if isinstance(self._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):                

                    if self._output_solver_results:
                        print "Results for scenario=",scenario_name
                        print results

                    self._load_variable_values(instance, results)
                else:
                    # a temporary hack - if results come back from pyro, they won't
                    # have a symbol map attached. so create one.
                    if results._symbol_map is None:
                        results._symbol_map = symbol_map_from_instance(instance)

                    if self._verbose:
                        print "Results obtained for scenario="+scenario_name

                    if len(results.solution) == 0:
                        results.write(num=1)
                        raise RuntimeError, "Solve failed for scenario="+scenario_name+"; no solutions generated"

                    if self._output_solver_results:
                        print "Results for scenario=",scenario_name
                        results.write(num=1)

                    start_time = time.time()
                    instance.load(results)
                    end_time = time.time()
                    if self._output_times:
                        print "Time loading results into instance %s=%0.2f seconds" % (scenario_name, end_time-start_time)

                if self._verbose:
                    print "Successfully loaded solution for scenario="+scenario_name

                # we're assuming there is a single solution.
                # the "value" attribute is a pre-defined feature of any solution - it is relative to whatever
                # objective was selected during optimization, which of course should be the PH objective.
                try:
                    ph_objective_values[instance.name] = float(results.solution(0).objective[1].value)
                except AttributeError:
                    # some solvers (e.g., through the SOL interface) don't report objective function values.
                    ph_objective_values[instance.name] = 0.0

                num_results_so_far = num_results_so_far + 1

            if self._verbose:
                print "Scenario sub-problem solves completed"

        iteration_end_time = time.time()
        self._cumulative_solve_time += (iteration_end_time - iteration_start_time)

        # STEP 3: Summarize results

        if self._output_times:
            print "Total time this PH iteration=%.2f" % (iteration_end_time - iteration_start_time)
            print ""

        if self._verbose:
            print "Successfully completed PH iteration " + str(self._current_iteration) + " solves - solution statistics:"
            print "  Scenario             PH Objective             Cost Objective"
            for scenario in self._scenario_tree._scenarios:
                instance = self._instances[scenario._name]
                for objective_name in instance.active_components(Objective):
                    objective = instance.active_components(Objective)[objective_name]
                    print "%20s       %18.4f     %14.4f" % (scenario._name, ph_objective_values[scenario._name], self._scenario_tree.compute_scenario_cost(instance))

    def async_iteration_k_plus_solves(self):
        # note: this routine retains control until a termination criterion is met
        # modified nov 2011 by dlw to do async with a window-like paramater

        if self._async_buffer_len <=0 or self._async_buffer_len > len(self._scenario_tree._scenarios):
            raise RuntimeError, "Async buffer length parameter is bad:"+str(self._async_buffer_len)
        if self._verbose == True:
            print "Starting PH iteration k+ solves - running async with buffer length=", self._async_buffer_len

        # we are going to buffer the scenario names
        ScenarioBuffer = []

        # things progress at different rates - keep track of what's going on.
        total_scenario_solves = 0 # self-explanatory.
        scenario_ks = {} # a map of scenario name to the number of sub-problems solved thus far.
        for scenario in self._scenario_tree._scenarios:
            scenario_ks[scenario._name] = 0

        # keep track of action handles mapping to scenarios.
        action_handle_instance_map = {} # maps action handles to scenario names

        # only form the PH objective components once, before we start in on the asychronous sub-problem solves.
        self.form_ph_objectives()

        # STEP 1: queue up the solves for all scenario sub-problems.

        for scenario in self._scenario_tree._scenarios:

            instance = self._instances[scenario._name]

            # the objective has always been modified, due to the new weights.
            self._instance_objectives_modified = True

            # if linearizing, form the necessary terms to compute the cost variables.
            if self._linearize_nonbinary_penalty_terms > 0:
                new_attrs = form_linearized_objective_constraints(scenario._name, \
                                                                  instance, \
                                                                  self._scenario_tree, \
                                                                  self._linearize_nonbinary_penalty_terms, \
                                                                  self._breakpoint_strategy, \
                                                                  self._integer_tolerance)

                self._instance_ph_constraints[scenario._name].extend(new_attrs)
                self._instance_piecewise_constraints_modified = True

            # preprocess prior to queuing the solve.
            preprocess_scenario_instance(instance, self._instance_variables_fixed, \
                                         self._instance_piecewise_constraints_modified, self._instance_ph_constraints[scenario._name], \
                                         self._instance_objectives_changed, self._instance_objectives_modified, self._solver_type)

            if self._verbose == True:
                print "Queuing solve for scenario=" + scenario._name

            # once past iteration 0, there is always a feasible solution from which to warm-start.
            if (self._disable_warmstarts is False) and (self._solver.warm_start_capable()):
                new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=True, tee=self._output_solver_logs, verbose=self._verbose)
            else:
                new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose)

            action_handle_instance_map[new_action_handle] = scenario._name

        # STEP 2: wait for the first action handle to return, process it, and keep chugging.

        while(True):

            this_action_handle = self._solver_manager.wait_any()
            solved_scenario_name = action_handle_instance_map[this_action_handle]

            scenario_ks[solved_scenario_name] += 1
            total_scenario_solves += 1

            if int(total_scenario_solves / len(scenario_ks)) > self._current_iteration:
                new_reportable_iteration = True
                self._current_iteration += 1
            else:
                new_reportable_iteration = False

            if self._verbose:
                print "Solve for scenario="+solved_scenario_name+ "completed - new solve count for this scenario="+str(scenario_ks[solved_scenario_name])

            instance = self._instances[solved_scenario_name]
            results = self._solver_manager.get_results(this_action_handle)

            if len(results.solution) == 0:
                raise RuntimeError, "Solve failed for scenario="+solved_scenario_name+"; no solutions generated"

            if self._verbose:
                print "Solve completed successfully"

            if self._output_solver_results == True:
                print "Results:"
                results.write(num=1)

            # in async mode, it is possible that we will receive values for variables
            # that have been fixed due to apparent convergence - but the outstanding
            # scenario solves will obviously not know this. if the values are inconsistent,
            # we have bigger problems - an exception will be thrown, and we currently lack
            # a recourse mechanism in such a case.
            instance.load(results, allow_consistent_values_for_fixed_vars=True)

            if self._verbose == True:
                print "Successfully loaded solution"

            # we're assuming there is a single solution.
            # the "value" attribute is a pre-defined feature of any solution - it is relative to whatever
            # objective was selected during optimization, which of course should be the PH objective.
            try:
                ph_objective_value = float(results.solution(0).objective[1].value)
            except AttributeError:
                # some solvers (e.g., through the SOL interface) don't report objective function values.
                ph_objective_value = 0.0

            if self._verbose:
                for objective_name in instance.active_components(Objective):
                    objective = instance.active_components(Objective)[objective_name]
                    print "%20s       %18.4f     %14.4f" % (solved_scenario_name, ph_objective_value, 0.0)

            # changed 19 Nov 2011 to support scenario buffers for async
            ScenarioBuffer.append(solved_scenario_name)
            if len(ScenarioBuffer) == self._async_buffer_len:
                if self._verbose:
                    print "Processing async buffer."
                    
                # update variable statistics prior to any output.
                self.update_variable_statistics()
                for scenario_name in ScenarioBuffer:
                    self.update_weights_for_scenario(self._instances[scenario_name])

                # we don't want to report stuff and invoke callbacks after each scenario solve - wait
                # for when each scenario (on average) has reported back a solution.
                if new_reportable_iteration:

                    # let plugins know if they care.
                    for plugin in self._ph_plugins:
                        plugin.post_iteration_k_solves(self)

                    # update the fixed variable statistics.
                    (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

                    if self._verbose:
                        print "Async Reportable Iteration Current variable averages and weights:"
                        self.pprint(True,True,False,False)

                    # check for early termination.
                    self._converger.update(self._current_iteration, self, self._scenario_tree, self._instances)
                    first_stage_min, first_stage_avg, first_stage_max = self._extract_first_stage_cost_statistics()
                    print "Convergence metric=%12.4f  First stage cost avg=%12.4f  Max-Min=%8.2f" % (self._converger.lastMetric(), first_stage_avg, first_stage_max-first_stage_min)

                    if self._converger.isConverged(self):
                        if self._total_discrete_vars == 0:
                            print "PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold)
                        else:
                            print "PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold)+" or all discrete variables are fixed"
                        break

                # see if we've exceeded our patience with the iteration limit.
                # changed to be based on the average on July 10, 2011 by dlw
                # (really, it should be some combination of the min and average over the scenarios)
                if total_scenario_solves / len(self._scenario_tree._scenarios) >= self._max_iterations:
                    return

                # we're still good to run - re-queue the instance, following any necessary linearization 
                for  scenario_name in ScenarioBuffer:
                    instance = self._instances[scenario_name]

                    # the objective has always been modified, due to the new weights.
                    self._instance_objectives_modified = True
                    # if linearizing, form the necessary terms to compute the cost variables.
                    if self._linearize_nonbinary_penalty_terms > 0:
                        new_attrs = form_linearized_objective_constraints(scenario_name, \
                                                                  instance, \
                                                                  self._scenario_tree, \
                                                                  self._linearize_nonbinary_penalty_terms, \
                                                                  self._breakpoint_strategy, \
                                                                  self._integer_tolerance)

                        self._instance_ph_constraints[scenario_name].extend(new_attrs)
                        self._instance_piecewise_constraints_modified = True

                    # preprocess prior to queuing the solve.
                    preprocess_scenario_instance(instance, self._instance_variables_fixed, \
                                         self._instance_piecewise_constraints_modified, self._instance_ph_constraints[scenario_name], \
                                         self._instance_objectives_changed, self._instance_objectives_modified, self._solver_type)

                    # once past the initial sub-problem solves, there is always a feasible solution from which to warm-start.
                    if (self._disable_warmstarts is False) and (self._solver.warm_start_capable()):
                        new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=True, tee=self._output_solver_logs, verbose=self._verbose)
                    else:
                        new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_logs, verbose=self._verbose)

                    action_handle_instance_map[new_action_handle] = scenario_name

                    if self._verbose:
                        print "Queued solve k="+str(scenario_ks[scenario_name]+1)+" for scenario="+solved_scenario_name

                    if self._verbose:
                        for sname, scenario_count in scenario_ks.iteritems():
                            print "Scenario="+sname+" was solved "+str(scenario_count)+" times"
                        print "Cumulative number of scenario solves="+str(total_scenario_solves)
                        print "PH Iteration Count (computed)="+str(self._current_iteration) 

                    if self._verbose:
                        print "Variable values following scenario solves:"
                        self.pprint(False,False,True,False)

                if self._verbose is True:
                    print "Emptying the asynch scenario buffer."
                # this is not a speed issue, is there a memory issue?
                ScenarioBuffer = []

    def solve(self):
        # return None unless a solve failure was detected in iter0, then immediately return the iter0 solve return value 
        # (which should be the name of the scenario detected)

        self._solve_start_time = time.time()
        self._cumulative_solve_time = 0.0
        self._cumulative_xbar_time = 0.0
        self._cumulative_weight_time = 0.0
        self._current_iteration = 0;

        print "Starting PH"

        if self._initialized == False:
            raise RuntimeError, "PH is not initialized - cannot invoke solve() method"

        # garbage collection noticeably slows down PH when dealing with
        # large numbers of scenarios. fortunately, there are well-defined
        # points at which garbage collection makes sense (and there isn't a
        # lot of collection to do). namely, after each PH iteration.
        re_enable_gc = gc.isenabled()
        gc.disable()

        print ""        
        print "Initiating PH iteration=" + `self._current_iteration`

        iter0retval = self.iteration_0_solves()
        if iter0retval is not None:
            if self._verbose:
                print "Iteration zero reports trouble with scenario: ",iter0retval
            return iter0retval

        # update variable statistics prior to any output.
        self.update_variable_statistics()

        if (self._verbose) or (self._report_solutions):
            print "Variable values following scenario solves:"
            self.pprint(False, False, True, False, output_only_statistics=self._report_only_statistics)

        # let plugins know if they care.
        for plugin in self._ph_plugins:
            plugin.post_iteration_0_solves(self)

        # update the fixed variable statistics.
        (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

        if self._verbose:
            print "Number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
            print "Number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"

        # always output the convergence metric and first-stage cost statistics, to give a sense of progress.
        self._converger.update(self._current_iteration, self, self._scenario_tree, self._instances)
        first_stage_min, first_stage_avg, first_stage_max = self._extract_first_stage_cost_statistics()
        print "Convergence metric=%12.4f  First stage cost avg=%12.4f  Max-Min=%8.2f" % (self._converger.lastMetric(), first_stage_avg, first_stage_max-first_stage_min)

        self.update_weights()

        # let plugins know if they care.
        for plugin in self._ph_plugins:
            plugin.post_iteration_0(self)

        # checkpoint if it's time - which it always is after iteration 0,
        # if the interval is >= 1!
        if (self._checkpoint_interval > 0):
            self.checkpoint(0)

        # garbage-collect if it wasn't disabled entirely.
        if re_enable_gc:
            if (time.time() - self._time_since_last_garbage_collect) >= self._minimum_garbage_collection_interval:
               gc.collect()
               self._time_last_garbage_collect = time.time() 

        # gather memory statistics (for leak detection purposes) if specified.
        # XXX begin debugging - commented
        #if (pympler_available) and (self._profile_memory >= 1):
        #    objects_last_iteration = muppy.get_objects()
        #    summary_last_iteration = summary.summarize(objects_last_iteration)
        # XXX end debugging - commented
 
        ####################################################################################################
        # major logic branch - if we are not running async, do the usual PH - otherwise, invoke the async. #
        ####################################################################################################
        if self._async is False:

            ####################################################################################################

            # there is an upper bound on the number of iterations to execute -
            # the actual bound depends on the converger supplied by the user.
            for i in xrange(1, self._max_iterations+1):

                # XXX begin debugging
                #def muppetize(self):
                #    if (pympler_available) and (self._profile_memory >= 1):
                #        objects_this_iteration = muppy.get_objects()
                #        summary_this_iteration = summary.summarize(objects_this_iteration)
                #        summary.print_(summary_this_iteration)
                #        del summary_this_iteration
                # XXX end debugging

                self._current_iteration = self._current_iteration + 1

                print ""
                print "Initiating PH iteration=" + str(self._current_iteration)

                if (self._verbose) or (self._report_weights):
                    print "Variable averages and weights prior to scenario solves:"
                    self.pprint(True, True, False, False, output_only_statistics=self._report_only_statistics)

                if self._current_iteration == 1:
                    self.form_ph_objectives() 

                # with the introduction of piecewise linearization, the form of the
                # penalty-weighted objective is no longer fixed. thus, when linearizing,
                # we need to construct (or at least modify) the constraints used to
                # compute the linearized cost terms.
                if self._linearize_nonbinary_penalty_terms > 0:
                    self.form_ph_linearized_objective_constraints()

                # instance objectives are always modified via weight or rho updates.
                self._instance_objectives_modified = True 

                # let plugins know if they care.
                for plugin in self._ph_plugins:
                    plugin.pre_iteration_k_solves(self)

                # do the actual solves.
                self.iteration_k_solves()

                # update variable statistics prior to any output.
                self.update_variable_statistics()

                if (self._verbose) or (self._report_solutions):
                    print "Variable values following scenario solves:"
                    self.pprint(False, False, True, False, output_only_statistics=self._report_only_statistics)

                # we don't technically have to do this at the last iteration,
                # but with checkpointing and re-starts, you're never sure
                # when you're executing the last iteration.
                self.update_weights()

                # let plugins know if they care.
                for plugin in self._ph_plugins:
                    plugin.post_iteration_k_solves(self)

                # update the fixed variable statistics.
                (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

                if self._verbose:
                    print "Number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
                    print "Number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"

                # let plugins know if they care.
                for plugin in self._ph_plugins:
                    plugin.post_iteration_k(self)

                # at this point, all the real work of an iteration is complete.

                # checkpoint if it's time.
                if (self._checkpoint_interval > 0) and (i % self._checkpoint_interval is 0):
                    self.checkpoint(i)

                # check for early termination.
                self._converger.update(self._current_iteration, self, self._scenario_tree, self._instances)
                first_stage_min, first_stage_avg, first_stage_max = self._extract_first_stage_cost_statistics()
                print "Convergence metric=%12.4f  First stage cost avg=%12.4f  Max-Min=%8.2f" % (self._converger.lastMetric(), first_stage_avg, first_stage_max-first_stage_min)

                if self._converger.isConverged(self):
                    if self._total_discrete_vars == 0:
                        print "PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold)
                    else:
                        print "PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold)+" or all discrete variables are fixed"
                    break

                # if we're terminating due to exceeding the maximum iteration count, print a message
                # indicating so - otherwise, you get a quiet, information-free output trace.
                if i == self._max_iterations:
                    print "Halting PH - reached maximal iteration count="+str(self._max_iterations)

                # garbage-collect if it wasn't disabled entirely.
                if re_enable_gc:
                    if (time.time() - self._time_since_last_garbage_collect) >= self._minimum_garbage_collection_interval:
                       gc.collect()
                       self._time_since_last_garbage_collect = time.time()

                # gather and report memory statistics (for leak detection purposes) if specified.
                if (guppy_available) and (self._profile_memory >= 1):
                    print hpy().heap()

                    #print "New (persistent) objects constructed during PH iteration "+str(self._current_iteration)+":"
                    #memory_tracker.print_diff(summary1=summary_last_iteration,
                    #                          summary2=summary_this_iteration)

                    ## get ready for the next iteration.
                    #objects_last_iteration = objects_this_iteration
                    #summary_last_iteration = summary_this_iteration
                    
                    # XXX begin debugging
                    #print "Current type: {0} ({1})".format(type(self), type(self).__name__)
                    #print "Recognized objects in muppy:", len(muppy.get_objects())
                    #print "Uncollectable objects (cycles?):", gc.garbage

                    ##from pympler.muppy import refbrowser
                    ##refbrowser.InteractiveBrowser(self).main()

                    #print "Referents from PH solver:", gc.get_referents(self)
                    #print "Interesting referent keys:", [k for k in gc.get_referents(self)[0].keys() if type(gc.get_referents(self)[0][k]).__name__ not in ['list', 'int', 'str', 'float', 'dict', 'bool']]
                    #print "_ph_plugins:", gc.get_referents(self)[0]['_ph_plugins']
                    #print "_converger:", gc.get_referents(self)[0]['_converger']
                    # XXX end debugging

            ####################################################################################################

        else:

            ####################################################################################################
            self.async_iteration_k_plus_solves()
            ####################################################################################################

        # re-enable the normal garbage collection mode.
        if re_enable_gc:
            gc.enable()

        if self._verbose:
            print "Number of discrete variables fixed before final plugin calls="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
            print "Number of continuous variables fixed before final plugin calls="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"

        # let plugins know if they care. do this before
        # the final solution / statistics output, as the plugins
        # might do some final tweaking.
        for plugin in self._ph_plugins:
            plugin.post_ph_execution(self)

        # update the fixed variable statistics - the plugins might have done something.
        (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

        self._solve_end_time = time.time()

        print "PH complete"

        print "Convergence history:"
        self._converger.pprint()

        # print *the* metric of interest.
        print ""
        print "***********************************************************************************************"
        root_node = self._scenario_tree._stages[0]._tree_nodes[0]      
        print ">>>THE EXPECTED SUM OF THE STAGE COST VARIABLES="+str(root_node.computeExpectedNodeCost(self._instances))+"<<<"
        print ">>>***WARNING***: Assumes full (or nearly so) convergence of scenario solutions at each node in the scenario tree - computed costs are invalid otherwise<<<"      
        print "***********************************************************************************************"                  

        print "Final number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
        print "Final number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"

        # populate the scenario tree solution from the instances - to ensure consistent state
        # across the scenario tree instance and the scenario instances.
        self._scenario_tree.snapshotSolutionFromInstances(self._instances)

        print "Final variable values:"
        self.pprint(False, False, True, True, output_only_statistics=self._report_only_statistics)

        print "Final costs:"
        self._scenario_tree.pprintCosts(self._instances)

        if self._output_scenario_tree_solution:
            self._scenario_tree.snapshotSolutionFromAverages(self._instances)
            print "Final solution (scenario tree format):"
            self._scenario_tree.pprintSolution()

        if (self._verbose) and (self._output_times):
            print "Overall run-time=%.2f seconds" % (self._solve_end_time - self._solve_start_time)

        # cleanup the scenario instances for post-processing - ideally, we want to leave them in
        # their original state, minus all the PH-specific stuff. we don't do all cleanup (leaving
        # things like rhos, etc), but we do clean up constraints, as that really hoses up the ef
        # writer.
        # IMPT: this method does a full preprocess() on each instance, so any variables fixed at
        #       the last iteration will be picked up and processed in this routine. this is
        #       important in the context of post-PH processing, including the extensive form
        #       write and solve.
        self._cleanup_scenario_instances()

    #
    # prints a summary of all collected time statistics
    #

    def print_time_stats(self):

        print "PH run-time statistics:"

        print "Initialization time=  %.2f seconds" % (self._init_end_time - self._init_start_time)
        print "Overall solve time=   %.2f seconds" % (self._solve_end_time - self._solve_start_time)
        print "Scenario solve time=  %.2f seconds" % self._cumulative_solve_time
        print "Average update time=  %.2f seconds" % self._cumulative_xbar_time
        print "Weight update time=   %.2f seconds" % self._cumulative_weight_time

    #
    # a utility to determine whether to output weight / average / etc. information for
    # a variable/node combination. when the printing is moved into a callback/plugin,
    # this routine will go there. for now, we don't dive down into the node resolution -
    # just the variable/stage.
    #

    def should_print(self, stage, variable):

        if self._output_continuous_variable_stats is False:

            variable_type = variable.domain

            if (isinstance(variable_type, IntegerSet) is False) and (isinstance(variable_type, BooleanSet) is False):

                return False

        return True

    #
    # pretty-prints the state of the current variable averages, weights, and values.
    # inputs are booleans indicating which components should be output.
    #

    def pprint(self, output_averages, output_weights, output_values, output_fixed, output_only_statistics=False):

        if self._initialized is False:
            raise RuntimeError, "PH is not initialized - cannot invoke pprint() method"

        # print tree nodes and associated variable/xbar/ph information in stage-order
        # we don't blend in the last stage, so we don't current care about printing the associated information.
        for stage in self._scenario_tree._stages[:-1]:

            print "\tStage=" + str(stage._name)

            num_outputs_this_stage = 0 # tracks the number of outputs on a per-index basis.

            for variable_name, (variable, index_template) in stage._variables.iteritems():

                if self.should_print(stage, variable):

                    num_outputs_this_variable = 0 # track, so we don't output the variable names unless there is an entry to report.

                    for tree_node in stage._tree_nodes:

                        variable_indices = tree_node._variable_indices[variable_name]

                        for index in sorted(variable_indices):

                            weight_parameter_name = "PHWEIGHT_"+variable_name

                            num_outputs_this_index = 0 # track, so we don't output the variable index more than once.

                            # determine if the variable/index pair is used across the set of scenarios (technically,
                            # it should be good enough to check one scenario). ditto for "fixed" status. fixed does
                            # imply unused (see note below), but we care about the fixed status when outputting
                            # final solutions.

                            is_used = True # should be consistent across scenarios, so one "unused" flags as invalid.
                            is_fixed = False

                            for scenario in tree_node._scenarios:
                                instance = self._instances[scenario._name]
                                variable_value = getattr(instance,variable_name)[index]
                                if variable_value.status == VarStatus.unused:
                                    is_used = False
                                if variable_value.fixed:
                                    is_fixed = True

                            # IMPT: this is far from obvious, but variables that are fixed will - because
                            #       presolve will identify them as constants and eliminate them from all
                            #       expressions - be flagged as "unused" and therefore not output.

                            if ((output_fixed) and (is_fixed)) or (is_used):

                                minimum_value = tree_node._minimums[variable_name][index]
                                average_value = tree_node._averages[variable_name][index]
                                maximum_value = tree_node._maximums[variable_name][index]

                                # there really isn't a need to output variables whose
                                # values are equal to 0 across-the-board. and there is
                                # good reason not to, i.e., the volume of output.
                                if (fabs(minimum_value) > self._integer_tolerance) or \
                                   (fabs(maximum_value) > self._integer_tolerance):

                                    num_outputs_this_stage = num_outputs_this_stage + 1
                                    num_outputs_this_variable = num_outputs_this_variable + 1
                                    num_outputs_this_index = num_outputs_this_index + 1

                                    if num_outputs_this_variable == 1:
                                        print "\t\tVariable=" + variable_name

                                    if num_outputs_this_index == 1:
                                        if index is not None:
                                            print "\t\t\tIndex:", indexToString(index),

                                    if len(stage._tree_nodes) > 1:
                                        print ""
                                        print "\t\t\t\tTree Node="+tree_node._name,
                                    if output_only_statistics is False:
                                        print "\t\t (Scenarios: ",
                                        for scenario in tree_node._scenarios:
                                            print scenario._name," ",
                                            if scenario == tree_node._scenarios[-1]:
                                                print ")"

                                    if output_values:
                                        if output_only_statistics is False:
                                            print "\t\t\t\tValues: ",
                                        for scenario in tree_node._scenarios:
                                            instance = self._instances[scenario._name]
                                            this_value = getattr(instance,variable_name)[index].value
                                            if output_only_statistics is False:
                                                print "%12.4f" % this_value,
                                            if scenario == tree_node._scenarios[-1]:
                                                if output_only_statistics:
                                                    # there technically isn't any good reason not to always report
                                                    # the min and max; the only reason we're not doing this currently
                                                    # is to avoid updating our regression test baseline output.
                                                    print "    Min=%12.4f" % (minimum_value),
                                                    print "    Avg=%12.4f" % (average_value),
                                                    print "    Max=%12.4f" % (maximum_value),
                                                else:
                                                    print "    Max-Min=%12.4f" % (maximum_value-minimum_value),
                                                    print "    Avg=%12.4f" % (average_value),
                                                print ""
                                    if output_weights:
                                        print "\t\t\t\tWeights: ",
                                        for scenario in tree_node._scenarios:
                                            instance = self._instances[scenario._name]
                                            print "%12.4f" % value(getattr(instance,weight_parameter_name)[index]),
                                            if scenario == tree_node._scenarios[-1]:
                                                print ""

                                    if output_averages:
                                        print "\t\t\t\tAverage: %12.4f" % (average_value)

            if num_outputs_this_stage == 0:
                print "\t\tNo non-converged variables in stage"

            # cost variables aren't blended, so go through the gory computation of min/max/avg.
            # we currently always print these.
            cost_variable_name = stage._cost_variable[0].name
            cost_variable_index = stage._cost_variable[1]
            if cost_variable_index is None:
                print "\t\tCost Variable=" + cost_variable_name
            else:
                print "\t\tCost Variable=" + cost_variable_name + indexToString(cost_variable_index)
            for tree_node in stage._tree_nodes:
                print "\t\t\tTree Node=" + tree_node._name,
                if output_only_statistics is False:
                    print "\t\t (Scenarios: ",
                    for scenario in tree_node._scenarios:
                        print scenario._name," ",
                        if scenario == tree_node._scenarios[-1]:
                            print ")"
                maximum_value = 0.0
                minimum_value = 0.0
                sum_values = 0.0
                num_values = 0
                first_time = True
                if output_only_statistics is False:
                    print "\t\t\tValues: ",
                else:
                    print "\t\t\t",
                for scenario in tree_node._scenarios:
                    instance = self._instances[scenario._name]
                    this_value = getattr(instance,cost_variable_name)[cost_variable_index].value
                    if output_only_statistics is False:
                        if this_value is not None:
                            print "%12.4f" % this_value,
                        else:
                            # this is a hack, in case the stage cost variables are not returned. ipopt
                            # does this occasionally, for example, if stage cost variables are constrained
                            # to a constant value (and consequently preprocessed out).
                            print "%12s" % "Not Rprted",
                    if this_value is not None:
                        num_values += 1
                        sum_values += this_value
                        if first_time:
                            first_time = False
                            maximum_value = this_value
                            minimum_value = this_value
                        else:
                            if this_value > maximum_value:
                                maximum_value = this_value
                            if this_value < minimum_value:
                                minimum_value = this_value
                    if scenario == tree_node._scenarios[-1]:
                        if num_values > 0:
                            if output_only_statistics:
                                print "    Min=%12.4f" % (minimum_value),
                                print "    Avg=%12.4f" % (sum_values/num_values),
                                print "    Max=%12.4f" % (maximum_value),
                            else:
                                print "    Max-Min=%12.4f" % (maximum_value-minimum_value),
                                print "    Avg=%12.4f" % (sum_values/num_values),
                        print ""
