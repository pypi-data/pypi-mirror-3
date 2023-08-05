import pyutilib
import sys
import os
import time
import traceback
import copy
import gc
import weakref

from coopr.pysp.scenariotree import *
from coopr.pysp.convergence import *
from coopr.pysp.ph import *
from coopr.pysp.phutils import *

from coopr.pyomo.base import *
from coopr.pyomo.io import *

from coopr.pyomo.base.var import _VarValue, _VarBase

from coopr.opt.results.solution import Solution

#
# a routine to create the extensive form, given an input scenario tree and instances.
# IMPT: unlike scenario instances, the extensive form instance is *not* self-contained.
#       in particular, it has binding constraints that cross the binding instance and
#       the scenario instances. it is up to the caller to keep track of which scenario
#       instances are associated with the extensive form. this might be something we
#       encapsulate at some later time.
# NOTE: if cvar terms are generated, then the input scenario tree is modified accordingly,
#       i.e., with the addition of the "eta" variable at the root node and the excess
#       variables at (for lack of a better place - they are per-scenario, but are not
#       blended) the second stage.
#

def create_ef_instance(scenario_tree, scenario_instances,
                       verbose_output = False, skip_canonical_repn = False,
                       generate_weighted_cvar = False, cvar_weight = None, risk_alpha = None,
                       cc_indicator_var_name=None, cc_alpha=0.0 ): 

    #
    # we're adding concrete components, and given that the instance is already constructed, make sure it is treated as a concrete instance.
    #
    for scenario_name, scenario_instance in scenario_instances.items():
        scenario_instance.concrete_mode()

    #
    # validate cvar options, if specified.
    #
    if generate_weighted_cvar is True:
        if (cvar_weight is None) or (cvar_weight < 0.0):
            raise RuntimeError, "Weight of CVaR term must be >= 0.0 - value supplied="+str(cvar_weight)
        if (risk_alpha is None) or (risk_alpha <= 0.0) or (risk_alpha >= 1.0):
            raise RuntimeError, "CVaR risk alpha must be between 0 and 1, exclusive - value supplied="+str(risk_alpha)

        if verbose_output is True:
            print "Writing CVaR weighted objective"
            print "CVaR term weight="+str(cvar_weight)
            print "CVaR alpha="+str(risk_alpha)
            print ""

        # create the eta and excess variable on a per-scenario basis,
        # in addition to the constraint relating to the two.
        for scenario_name, scenario_instance in scenario_instances.items():

            cvar_excess_variable_name = "CVAR_EXCESS"
            cvar_excess_variable = Var(name=cvar_excess_variable_name, domain=NonNegativeReals)
            setattr(scenario_instance, cvar_excess_variable_name, cvar_excess_variable)

            cvar_eta_variable_name = "CVAR_ETA"
            cvar_eta_variable = Var(name=cvar_eta_variable_name)
            setattr(scenario_instance, cvar_eta_variable_name, cvar_eta_variable)

            compute_excess_expression = cvar_excess_variable
            for node in scenario_tree._scenario_map[scenario_name]._node_list:
                (cost_variable, cost_variable_idx) = node._stage._cost_variable
                compute_excess_expression -= getattr(scenario_instance, cost_variable.name)[cost_variable_idx]
            compute_excess_expression += cvar_eta_variable

            def makeExcessRule(expression):
                def excessRule(model):
                    return (0.0, expression, None)
                return excessRule

            compute_excess_constraint_name = "COMPUTE_SCENARIO_EXCESS"
            compute_excess_constraint = Constraint(name=compute_excess_constraint_name, rule=makeExcessRule(compute_excess_expression))
            setattr(scenario_instance, compute_excess_constraint_name, compute_excess_constraint)

            # re-process the scenario instance due to the newly added constraints/variables associated
            # with CVaR. a complete preprocess is overkill, of course - the correct approach would be
            # to just preprocess those newly added variables and constraints.
            scenario_instance.preprocess()

        # update the scenario tree with cvar-specific variable names, so
        # they will get cloned accordingly in the master instance.
        first_stage = scenario_tree._stages[0]
        second_stage = scenario_tree._stages[1]
        root_node = first_stage._tree_nodes[0]

        # NOTE: because we currently don't have access to the reference
        #       instance in this method, temporarily (and largely orphaned)
        #       variables are constructed to supply to the scenario tree.
        #       this decision should be ultimately revisited.
        cvar_eta_variable_name = "CVAR_ETA"
        cvar_eta_variable = Var(name=cvar_eta_variable_name)

        first_stage.add_variable(cvar_eta_variable, "*", scenario_instances)

        cvar_excess_variable_name = "CVAR_EXCESS"
        cvar_excess_variable = Var(name=cvar_excess_variable_name)

        second_stage.add_variable(cvar_excess_variable, "*", scenario_instances)

    #
    # create the new and empty binding instance.
    #

    binding_instance = ConcreteModel()
    binding_instance.name = "MASTER"

    # the individual scenario instances are sub-blocks of the binding instance.
    for scenario_name, scenario_instance in scenario_instances.items():
        binding_instance._add_component(scenario_name, scenario_instance)

    # walk the scenario tree - create variables representing the common values for all scenarios
    # associated with that node, along with equality constraints to enforce non-anticipativity.
    # also create expected cost variables for each node, to be computed via constraints/objectives
    # defined in a subsequent pass. master variables are created for all nodes but those in the
    # last stage. expected cost variables are, for no particularly good reason other than easy
    # coding, created for nodes in all stages.
    if verbose_output is True:
        print "Creating variables for master binding instance"

    for stage in scenario_tree._stages:

        # first loop is to create master (blended) variables across all stages but the last.
        for stage_variable_name, (stage_reference_variable, index_templates) in stage._variables.iteritems():

            if verbose_output is True:
                print "Creating master variable and blending constraints for decision variable="+stage_reference_variable.name+", indices=",
                for index_template in index_templates:
                   print indexToString(index_template)+" ",
                print ""

            for tree_node in stage._tree_nodes:

                if stage != scenario_tree._stages[-1]:

                    stage_variable_indices = tree_node._variable_indices[stage_variable_name]

                    master_variable_name = tree_node._name + "_" + stage_variable_name

                    # because there may be a single stage variable and multiple indices, check
                    # for the existence of the variable at this node - if you don't, you'll
                    # inadvertently over-write what was there previously!
                    master_variable = None
                    try:
                        master_variable = getattr(binding_instance, master_variable_name)
                    except:
                        new_master_variable_index = getattr(scenario_instances[tree_node._scenarios[0]._name], stage_variable_name)._index
                        new_master_variable = None
                        if (len(new_master_variable_index) is 1) and (None in new_master_variable_index):
                            new_master_variable = Var(name=master_variable_name)
                        else:
                            new_master_variable = Var(new_master_variable_index, name=master_variable_name)
                        setattr(binding_instance, master_variable_name, new_master_variable)

                        master_variable = new_master_variable

                    # TBD: we should create a doubly in indexed constraint here, and then add entries within the loop.
                    # TBD: NOTE - JUST DEFINE THE CONSTRAINT HERE, ADDING IT TO THE MODEL - BUT USING THE noruleinit=True
                    #      KEYWORD - THEN, ADD EXPRESSIONS FOR VALID INDICES. SHOULD BE DOUBLY (OR MORE) INDEXED - BY
                    #      VARIABLE INDEX AND BY SCENARIO.
                    for index in stage_variable_indices:

                        is_used = True # until proven otherwise
                        for scenario in tree_node._scenarios:
                            instance = scenario_instances[scenario._name]
                            if getattr(instance,stage_variable_name)[index].status == VarStatus.unused:
                                is_used = False

                        is_fixed = False # until proven otherwise
                        for scenario in tree_node._scenarios:
                            instance = scenario_instances[scenario._name]
                            if getattr(instance,stage_variable_name)[index].fixed is True:
                                is_fixed = True

                        if (is_used is True) and (is_fixed is False):

                            for scenario in tree_node._scenarios:

                                scenario_instance = scenario_instances[scenario._name]
                                scenario_variable = getattr(scenario_instance, stage_variable_name)

                                def makeEqualityRule(master_variable, scenario_variable, index):
                                    def equalityRule(model):
                                        return (0.0, master_variable[index] - scenario_variable[index], 0.0)
                                    return equalityRule

                                new_constraint_name = scenario._name + "_" + stage_variable_name + "_" + str(index)
                                new_constraint = Constraint(name=new_constraint_name, rule=makeEqualityRule(master_variable, scenario_variable, index))
                                setattr(binding_instance, new_constraint_name, new_constraint)

        # the second loop is for creating the stage cost variable in each tree node.
        for tree_node in stage._tree_nodes:

            # create a variable to represent the expected cost at this node -
            # the constraint to compute this comes later.
            expected_cost_variable_name = "EXPECTED_COST_" + tree_node._name
            expected_cost_variable = Var(name=expected_cost_variable_name)
            setattr(binding_instance, expected_cost_variable_name, expected_cost_variable)

    if generate_weighted_cvar is True:

        cvar_cost_variable_name = "CVAR_COST_" + root_node._name
        cvar_cost_variable = Var(name=cvar_cost_variable_name)
        setattr(binding_instance, cvar_cost_variable_name, cvar_cost_variable)

    if skip_canonical_repn is True:
        binding_instance.skip_canonical_repn = True
    else:
        binding_instance.preprocess()

    # ditto above for the (non-expected) cost variable.
    for stage in scenario_tree._stages:

        (cost_variable,cost_variable_index) = stage._cost_variable

        if verbose_output is True:
            print "Creating master variable and blending constraints for cost variable="+cost_variable.name+", index="+str(cost_variable_index)

        for tree_node in stage._tree_nodes:

            # TBD - the following is bad - check to see if it's already there (I suspect some of them are!!!)

            # this is undoubtedly wasteful, in that a cost variable for each tree node is created with *all* indices.
            new_cost_variable_name = tree_node._name + "_" + cost_variable.name
            new_cost_variable_index = cost_variable._index
            new_cost_variable = None
            if (len(new_cost_variable_index) is 1) and (None in new_cost_variable_index):
                new_cost_variable = Var(name=new_cost_variable_name)
            else:
                new_cost_variable = Var(new_cost_variable_index, name=new_cost_variable_name)
            setattr(binding_instance, new_cost_variable_name, new_cost_variable)

            # the following is necessary, specifically to get the name - deepcopy won't reset these attributes.
            new_cost_variable[cost_variable_index].component = weakref.ref(new_cost_variable)
            if cost_variable_index is not None:
                # if the variable index is None, the variable is derived from a VarValue, so the name gets updated automagically.
                # TBD: the following is problematic, as we effectively get the tree node name twice...
                new_cost_variable[cost_variable_index].name = tree_node._name + "_" + new_cost_variable[cost_variable_index].name

            for scenario in tree_node._scenarios:

                scenario_instance = scenario_instances[scenario._name]
                scenario_cost_variable = getattr(scenario_instance, cost_variable.name)

                def makeEqualityRule(new_cost_variable, scenario_cost_variable, index):
                    def equalityRule(model):
                        return (0.0, new_cost_variable[cost_variable_index] - scenario_cost_variable[cost_variable_index], 0.0)
                    return equalityRule

                new_constraint_name = scenario._name + "_" + new_cost_variable_name + "_" + str(cost_variable_index)
                new_constraint = Constraint(name=new_constraint_name, rule=makeEqualityRule(new_cost_variable, scenario_cost_variable, cost_variable_index))
                setattr(binding_instance, new_constraint_name, new_constraint)

    # create the constraints for computing the master per-node cost variables,
    # i.e., the current node cost and the expected cost of the child nodes.
    # if the root, then the constraint is just the objective.
    for stage in scenario_tree._stages:

        (stage_cost_variable,stage_cost_variable_index) = stage._cost_variable

        for tree_node in stage._tree_nodes:

            node_expected_cost_variable_name = "EXPECTED_COST_" + tree_node._name
            node_expected_cost_variable = getattr(binding_instance, node_expected_cost_variable_name)

            node_cost_variable_name = tree_node._name + "_" + stage_cost_variable.name
            node_cost_variable = getattr(binding_instance, node_cost_variable_name)

            constraint_expr = node_expected_cost_variable - node_cost_variable[stage_cost_variable_index]
            for child_node in tree_node._children:
                child_node_expected_cost_variable_name = "EXPECTED_COST_" + child_node._name
                child_node_expected_cost_variable = getattr(binding_instance, child_node_expected_cost_variable_name)
                constraint_expr = constraint_expr - (child_node._conditional_probability * child_node_expected_cost_variable)

            def makeEqualityRule(expression):
                def equalityRule(model):
                    return (0.0, expression, 0.0)
                return equalityRule

            new_constraint_name = "COST" + "_" + node_cost_variable_name + "_" + str(cost_variable_index)
            new_constraint = Constraint(name=new_constraint_name, rule=makeEqualityRule(constraint_expr))
            setattr(binding_instance, new_constraint_name, new_constraint)

            if tree_node._parent is None:

                an_instance = scenario_instances[scenario_instances.keys()[0]]
                an_objective = an_instance.active_components(Objective)
                opt_sense = an_objective[an_objective.keys()[0]].sense

                opt_expression = node_expected_cost_variable

                if generate_weighted_cvar is True:
                    cvar_cost_variable_name = "CVAR_COST_" + tree_node._name
                    cvar_cost_variable = getattr(binding_instance, cvar_cost_variable_name)
                    if cvar_weight == 0.0:
                        # if the cvar weight is 0, then we're only doing cvar - no mean.
                        opt_expression = cvar_cost_variable
                    else:
                        opt_expression += cvar_weight * cvar_cost_variable

                new_objective = Objective(name="MASTER", sense=opt_sense, expr=opt_expression)
                setattr(binding_instance, "MASTER", new_objective)

    # CVaR requires the addition of a variable per scenario to represent the cost excess,
    # and a constraint to compute the cost excess relative to eta. we also replicate (following
    # what we do for node cost variables) an eta variable for each scenario instance, and
    # require equality with the master eta variable via constraints.
    if generate_weighted_cvar is True:

        # add the constraint to compute the master CVaR variable value. iterate
        # over scenario instances to create the expected excess component first.
        cvar_cost_variable_name = "CVAR_COST_" + root_node._name
        cvar_cost_variable = getattr(binding_instance, cvar_cost_variable_name)
        cvar_eta_variable_name = root_node._name + "_CVAR_ETA"
        cvar_eta_variable = getattr(binding_instance, cvar_eta_variable_name)

        cvar_cost_expression = cvar_cost_variable - cvar_eta_variable

        for scenario_name, scenario_instance in scenario_instances.items():

            scenario_probability = scenario_tree._scenario_map[scenario_name]._probability

            scenario_excess_variable_name = "CVAR_EXCESS"
            scenario_excess_variable = getattr(scenario_instance, scenario_excess_variable_name)

            cvar_cost_expression = cvar_cost_expression - (scenario_probability * scenario_excess_variable) / (1.0 - risk_alpha)

        def makeExcessRule(expression):
            def excessRule(model):
                return (0.0, expression, 0.0)
            return excessRule

        compute_cvar_cost_constraint_name = "COMPUTE_CVAR_COST"
        compute_cvar_cost_constraint = Constraint(name=compute_cvar_cost_constraint_name, rule=makeExcessRule(cvar_cost_expression))
        setattr(binding_instance, compute_cvar_cost_constraint_name, compute_cvar_cost_constraint)

    if cc_indicator_var_name is not None:
        if verbose_output is True:
            print "Creating chance constraint for indicator variable=",cc_indicator_var_name
            print "with alpha=",cc_alpha
        cc_expression = 0  #??????
        for scenario_name, scenario_instance in scenario_instances.items():
            scenario_probability = scenario_tree._scenario_map[scenario_name]._probability
            cc_var = getattr(scenario_instance, cc_indicator_var_name)

            cc_expression += scenario_probability * cc_var

        def makeCCRule(expression):
            def CCrule(model):
                return(1.0 - cc_alpha, cc_expression, None)
            return CCrule

        cc_constraint_name = "cc_"+cc_indicator_var_name
        cc_constraint = Constraint(name=cc_constraint_name, rule=makeCCRule(cc_expression))
        setattr(binding_instance, cc_constraint_name, cc_constraint)


    # always preprocess the binding instance, so that it is ready for solution.
    binding_instance.preprocess()

    return binding_instance

#
# write the EF binding instance and all sub-instances. 
#

def write_ef(binding_instance, scenario_instances, output_filename): 

    # determine the output file type, and invoke the appropriate writer. 
    pieces = output_filename.rsplit(".",1)
    if len(pieces) != 2:
       raise RuntimeError, "Could not determine suffix from output filename="+output_filename
    ef_output_file_suffix = pieces[1]

    # create the output file.
    if ef_output_file_suffix == "lp":

       problem_writer = cpxlp.ProblemWriter_cpxlp()
       output_file = open(output_filename,"w")
       symbol_map = problem_writer._print_model_LP(binding_instance, output_file, lambda x:True)  
       output_file.close()

    elif ef_output_file_suffix == "nl":

       scenario_instances[binding_instance.name] = binding_instance    
       problem_writer = ampl.ProblemWriter_nl()                                
       output_file = open(output_filename,'w')                              
       # we're ignoring the symbol map, because we don't know where to put it.
       symbol_map = problem_writer._print_model_NL(binding_instance, output_file, lambda x:True)  
#       symbol_map = problem_writer._print_model_NL(scenario_instances, output_file, lambda x:True)  
       output_file.close()                                                  

    else:
       raise RuntimeError, "Unknown file suffix="+ef_output_file_suffix+" specified when writing extensive form"    

    return symbol_map

#
# the main extensive-form writer routine - including read of scenarios/etc.
# returns a triple consisting of the scenario tree, master binding instance, and scenario instance map
#

def write_ef_from_scratch(model_directory, instance_directory, output_filename,
                          verbose_output, linearize_expressions, tree_downsample_fraction, tree_random_seed,
                          generate_weighted_cvar, cvar_weight, risk_alpha, cc_indicator_var_name, cc_alpha):

    start_time = time.time()

    scenario_data_directory_name = instance_directory

    # if we're dealing with NL files, we don't have to worry about generating the canonical expression.
    pieces = output_filename.rsplit(".",1)
    if len(pieces) != 2:
        raise RuntimeError, "Could not determine suffix from output filename="+output_filename
    output_file_suffix = pieces[1]

    print "Loading scenario and instance data"

    #
    # create and populate the core model
    #
    master_scenario_model = None
    master_scenario_instance = None

    if verbose_output:
        print "Constructing reference model and instance"

    try:

        reference_model_filename = model_directory+os.sep+"ReferenceModel.py"
        modelimport = pyutilib.misc.import_file(reference_model_filename)
        if "model" not in dir(modelimport):
            print ""
            print "Exiting ef module: No 'model' object created in module "+reference_model_filename
            sys.exit(0)
        if modelimport.model is None:
            print ""
            print "Exiting ef module: 'model' object equals 'None' in module "+reference_model_filename
            sys.exit(0)

        master_scenario_model = modelimport.model

    except IOError, exception:

        print "***ERROR: Failed to load scenario reference model from file="+reference_model_filename+"; Source error="+str(exception)
        return None, None, None, None

    try:

        reference_scenario_filename = instance_directory+os.sep+"ReferenceModel.dat"
        master_scenario_instance = master_scenario_model.create(reference_scenario_filename, preprocess=False)

    except IOError, exception:

        print "***ERROR: Failed to load scenario reference instance data from file="+reference_scenario_filename+"; Source error="+str(exception)
        return None, None, None, None

    #
    # create and populate the scenario tree model
    #

    from coopr.pysp.util.scenariomodels import scenario_tree_model

    if verbose_output:
        print "Constructing scenario tree instance"

    scenario_tree_instance = scenario_tree_model.create(instance_directory+os.sep+"ScenarioStructure.dat")

    #
    # construct the scenario tree
    #
    if verbose_output:
        print "Constructing scenario tree object"

    scenario_tree = ScenarioTree(scenarioinstance=master_scenario_instance,
                                 scenariotreeinstance=scenario_tree_instance)

    #
    # compress/down-sample the scenario tree, if operation is required.
    #
    if tree_downsample_fraction < 1.0:

        scenario_tree.downsample(tree_downsample_fraction, tree_random_seed, verbose_output)

    #
    # print the input tree for validation/information purposes.
    #
    if verbose_output is True:
        scenario_tree.pprint()

    #
    # validate the tree prior to doing anything serious
    #
    if scenario_tree.validate() is False:
        print "***Scenario tree is invalid****"
        sys.exit(1)
    else:
        if verbose_output is True:
            print "Scenario tree is valid!"

    #
    # construct instances for each scenario
    #

    # the construction of instances takes little overhead in terms of
    # memory potentially lost in the garbage-collection sense (mainly
    # only that due to parsing and instance simplification/prep-processing).
    # to speed things along, disable garbage collection if it enabled in
    # the first place through the instance construction process.
    # IDEA: If this becomes too much for truly large numbers of scenarios,
    #       we could manually collect every time X instances have been created.

    re_enable_gc = False
    if gc.isenabled() is True:
        re_enable_gc = True
        gc.disable()

    scenario_instances = {}

    if scenario_tree._scenario_based_data == 1:
        if verbose_output is True:
            print "Scenario-based instance initialization enabled"
    else:
        if verbose_output is True:
            print "Node-based instance initialization enabled"

    for scenario in scenario_tree._scenarios:

        scenario_instance = construct_scenario_instance(scenario_tree,
                                                        instance_directory,
                                                        scenario._name,
                                                        master_scenario_model,
                                                        verbose=verbose_output,
                                                        preprocess=False,
                                                        linearize=linearize_expressions)

        if output_file_suffix == "nl":
            scenario_instance.skip_canonical_repn = True
        else:
            scenario_instance.preprocess()            

        scenario_instances[scenario._name] = scenario_instance
        # name each instance with the scenario name, so the prefixes in the EF make sense.
        scenario_instance.name = scenario._name

    if re_enable_gc is True:
        gc.enable()

    # with the scenario instances now available, have the scenario tree compute the
    # variable match indices at each node.
    scenario_tree.defineVariableIndexSets(scenario_instances)

    scenario_instance_construction_time = time.time()
    print "Time to construct scenario instances=%.2f seconds" %(scenario_instance_construction_time - start_time)    

    print "Creating extensive form binding instance"

    binding_instance = create_ef_instance(scenario_tree, scenario_instances,
                                          verbose_output = verbose_output,
                                          skip_canonical_repn = (output_file_suffix == "nl"),
                                          generate_weighted_cvar = generate_weighted_cvar,
                                          cvar_weight = cvar_weight,
                                          risk_alpha = risk_alpha,
                                          cc_indicator_var_name = cc_indicator_var_name,
                                          cc_alpha = cc_alpha)

    binding_instance_construction_time = time.time()
    print "Time to construct extensive form instance=%.2f seconds" %(binding_instance_construction_time - scenario_instance_construction_time)        

    print "Starting to write extensive form"

    symbol_map = write_ef(binding_instance, scenario_instances, output_filename)

    print "Output file written to file=",output_filename

    print "Time to write output file=%.2f seconds" %(time.time() - binding_instance_construction_time)

    return scenario_tree, binding_instance, scenario_instances, symbol_map

#
# does what it says, with the added functionality of returning the master binding instance.
#

def create_and_write_ef(scenario_tree, scenario_instances, output_filename):

    start_time = time.time()

    binding_instance = create_ef_instance(scenario_tree, scenario_instances)

    print "Starting to write extensive form"

    symbol_map = write_ef(binding_instance, scenario_instances, output_filename)

    print "Output file written to file=",output_filename

    end_time = time.time()

    print "Total execution time=%8.2f seconds" %(end_time - start_time)

    return binding_instance, symbol_map
