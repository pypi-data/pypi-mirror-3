#
# Get the directory where this script is defined, and where the baseline
# files are located.
#
import os
import sys
import string
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")

this_test_file_directory = dirname(abspath(__file__))+os.sep

pysp_examples_dir = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))+os.sep+"examples"+os.sep+"pysp"+os.sep

coopr_bin_dir = dirname(dirname(dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))))+os.sep+"bin"+os.sep

#
# Import the testing packages
#
import pyutilib.misc
import pyutilib.th as unittest
import pyutilib.subprocess
from pyutilib.component.executables import *
import coopr.pysp
import coopr.plugins.solvers
import coopr.pysp.phinit
import coopr.pysp.ef_writer_script

def filter_time_and_data_dirs(line):
    return "seconds" in line or line.startswith("Output file written to") or "filename" in line or "directory" in line or "file" in line

# pyro output filtering is complex, due to asynchronous behaviors - filter all blather regarding what Pyro components are doing.
def filter_pyro(line):
    if line.startswith("URI") or line.startswith("Object URI") or line.startswith("Dispatcher Object URI"):
       return True
    elif line.startswith("Applying solver"):
       return True
    elif line.startswith("Attempting to find Pyro dispatcher object"):
       return True   
    elif line.startswith("Getting work from"):
       return True
    elif line.startswith("Listening for work from"):
       return True
    elif line.startswith("Broadcast server"):
       return True
    elif line.startswith("Failed to locate nameserver - trying again"):
       return True
    elif line.startswith("Failed to find dispatcher object from name server - trying again"):
       return True   
    elif line.startswith("Lost connection to"): # happens when shutting down pyro objects
       return True      
    elif line.startswith("WARNING: daemon bound on hostname that resolves"): # happens when not connected to a network.
       return True      
    elif line.startswith("This is worker") or line.startswith("This is client") or line.startswith("Finding Pyro"):
       return True
    elif line.find("Applying solver") != -1:
       return True
    elif line.find("Solve completed") != -1:
       return True
    elif line.startswith("Creating instance"): # non-deterministic order for PH Pyro solver manager
       return True
    elif line.startswith("Exception in thread"): # occasionally raised during Pyro component shutdown
       return True
    elif line.startswith("Traceback"): # occasionally raised during Pyro component shutdown
       return True
    elif line.startswith("File"): # occasionally raised during Pyro component shutdown
       return True               
    return filter_time_and_data_dirs(line)

cplex = None
cplex_available = False
try:
    cplex = coopr.plugins.solvers.CPLEX(keepFiles=True)
    cplex_available = (not cplex.executable() is None) and cplex.available(False)
except pyutilib.common.ApplicationError:
    cplex_available=False

cplex_direct = None
cplex_direct_available = False
try:
    cplex_direct = coopr.plugins.solvers.CPLEXDirect()
    cplex_direct_available = cplex_direct.available(False)
except pyutilib.common.ApplicationError:
    cplex_direct_available=False

gurobi = None
gurobi_available = False
try:
    gurobi = coopr.plugins.solvers.GUROBI(keepFiles=True)
    gurobi_available = (not gurobi.executable() is None) and gurobi.available(False)
except pyutilib.common.ApplicationError:
    gurobi_available=False

gurobi_direct = None
gurobi_direct_available = False
try:
    gurobi_direct = coopr.plugins.solvers.gurobi_direct()
    gurobi_direct_available = gurobi_direct.available(False)
except pyutilib.common.ApplicationError:
    gurobi_direct_available=False

glpk = None
glpk_available = False
try:
    glpk = coopr.plugins.solvers.GLPK(keepFiles=True)
    glpk_available = (not glpk.executable() is None) and glpk.available(False)
except pyutilib.common.ApplicationError:
    glpk_available=False

ipopt = None
ipopt_available = False
try:
    ipopt = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'ipopt'})
    if (ipopt.executable() is not None) and (ipopt.available(False) is True):
        ipopt_available = True
    else:
        ipopt_available = False
except pyutilib.common.ApplicationError:
    ipopt_available=False

mpirun_executable = ExternalExecutable(name="mpirun")
mpirun_available = mpirun_executable.enabled()

#
# Define a testing class, using the unittest.TestCase class.
#

class TestPH(unittest.TestCase):

    def cleanup(self):

        # IMPT: This step is key, as Python keys off the name of the module, not the location.
        #       So, different reference models in different directories won't be detected.
        #       If you don't do this, the symptom is a model that doesn't have the attributes
        #       that the data file expects.
        if "ReferenceModel" in sys.modules:
            del sys.modules["ReferenceModel"]

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_quadratic_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_cplex.out",this_test_file_directory+"farmer_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_quadratic_nonnormalized_termdiff_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --enable-termdiff-convergence --termdiff-threshold=0.01"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_nonnormalized_termdiff_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_nonnormalized_termdiff_cplex.out",this_test_file_directory+"farmer_quadratic_nonnormalized_termdiff_cplex.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not cplex_direct_available, "The 'cplex' python solver is not available")
    def test_farmer_quadratic_cplex_direct(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=cplex --solver-io=python --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_cplex_direct.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_cplex_direct.out",this_test_file_directory+"farmer_quadratic_cplex_direct.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_direct_available, "The 'gurobi' python solver is not available")
    def test_farmer_quadratic_gurobi_direct(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=gurobi --solver-io=python --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_gurobi_direct.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_gurobi_direct.out",this_test_file_directory+"farmer_quadratic_gurobi_direct.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_gurobi.out",this_test_file_directory+"farmer_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_nonnormalized_termdiff_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --enable-termdiff-convergence --termdiff-threshold=0.01"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_nonnormalized_termdiff_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_nonnormalized_termdiff_gurobi.out",this_test_file_directory+"farmer_quadratic_nonnormalized_termdiff_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_gurobi_with_flattening(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --flatten-expressions"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_gurobi_with_flattening.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_gurobi_with_flattening.out",this_test_file_directory+"farmer_quadratic_gurobi_with_flattening.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not ipopt_available, "The 'ipopt' executable is not available")
    def test_farmer_quadratic_ipopt(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=ipopt --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_ipopt.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_ipopt.out",this_test_file_directory+"farmer_quadratic_ipopt.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_maximize_quadratic_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "maxmodels"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_maximize_quadratic_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_maximize_quadratic_gurobi.out",this_test_file_directory+"farmer_maximize_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_with_integers_quadratic_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmerWintegers"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --default-rho=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_with_integers_quadratic_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_integers_quadratic_cplex.out",this_test_file_directory+"farmer_with_integers_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_with_integers_quadratic_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmerWintegers"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --default-rho=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_with_integers_quadratic_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()

        if os.sys.platform == "darwin":
           self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_integers_quadratic_gurobi.out",this_test_file_directory+"farmer_with_integers_quadratic_gurobi_darwin.baseline", filter=filter_time_and_data_dirs)        
        else:
           self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_integers_quadratic_gurobi.out",this_test_file_directory+"farmer_with_integers_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available or not mpirun_available, "Either the 'cplex' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_with_integers_quadratic_cplex_with_pyro_with_postef_solve(self):
        farmer_examples_dir = pysp_examples_dir + "farmerWintegers"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 pyro_mip_server : -np 1 runph --max-iterations=10 --solve-ef --solver=cplex --solver-manager=pyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_with_integers_quadratic_cplex_with_pyro_with_postef_solve.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_integers_quadratic_cplex_with_pyro_with_postef_solve.out",this_test_file_directory+"farmer_with_integers_quadratic_cplex_with_pyro_with_postef_solve.baseline", filter=filter_pyro)                   
    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_quadratic_verbose_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=cplex --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_verbose_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_verbose_cplex.out",this_test_file_directory+"farmer_quadratic_verbose_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_verbose_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver=gurobi --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_verbose_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_verbose_gurobi.out",this_test_file_directory+"farmer_quadratic_verbose_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_quadratic_trivial_bundling_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTrivialBundles"
        argstring = "runph --solver=cplex --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_trivial_bundling_cplex.out")        
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_trivial_bundling_cplex.out",this_test_file_directory+"farmer_quadratic_trivial_bundling_cplex.baseline", filter=filter_time_and_data_dirs)
        
    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_trivial_bundling_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTrivialBundles"
        argstring = "runph --solver=gurobi --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_trivial_bundling_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_trivial_bundling_gurobi.out",this_test_file_directory+"farmer_quadratic_trivial_bundling_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not ipopt_available, "The 'ipopt' executable is not available")
    def test_farmer_quadratic_trivial_bundling_ipopt(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTrivialBundles"
        argstring = "runph --solver=ipopt --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_trivial_bundling_ipopt.out")        
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_trivial_bundling_ipopt.out",this_test_file_directory+"farmer_quadratic_trivial_bundling_ipopt.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_quadratic_basic_bundling_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTwoBundles"
        argstring = "runph --solver=cplex --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_basic_bundling_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_basic_bundling_cplex.out",this_test_file_directory+"farmer_quadratic_basic_bundling_cplex.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_quadratic_basic_bundling_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTwoBundles"
        argstring = "runph --solver=gurobi --solver-manager=serial --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_quadratic_basic_bundling_gurobi.out")        
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_basic_bundling_gurobi.out",this_test_file_directory+"farmer_quadratic_basic_bundling_gurobi.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_with_rent_quadratic_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmerWrent"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_with_rent_quadratic_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_rent_quadratic_cplex.out",this_test_file_directory+"farmer_with_rent_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_with_rent_quadratic_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmerWrent"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_with_rent_quadratic_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_with_rent_quadratic_gurobi.out",this_test_file_directory+"farmer_with_rent_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_farmer_cplex(self):
        if cplex_available:
            solver_string="cplex"
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_cplex.out",this_test_file_directory+"farmer_linearized_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_farmer_maximize_cplex(self):
        if cplex_available:
            solver_string="cplex"
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "maxmodels"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_maximize_linearized_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_maximize_linearized_cplex.out",this_test_file_directory+"farmer_maximize_linearized_cplex.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_linearized_farmer_gurobi(self):
        if gurobi_available:
            solver_string="gurobi"
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_gurobi.out",this_test_file_directory+"farmer_linearized_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_linearized_farmer_maximize_gurobi(self):
        if gurobi_available:
            solver_string="gurobi"
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "maxmodels"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_maximize_linearized_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_maximize_linearized_gurobi.out",this_test_file_directory+"farmer_maximize_linearized_gurobi.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_farmer_nodedata_cplex(self):
        if cplex_available:
            solver_string="cplex"
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_nodedata_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_nodedata_cplex.out",this_test_file_directory+"farmer_linearized_nodedata_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_linearized_farmer_nodedata_gurobi(self):
        if gurobi_available:
            solver_string="gurobi"
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "nodedata"
        argstring = "runph --solver="+solver_string+" --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+" --linearize-nonbinary-penalty-terms=10"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_linearized_nodedata_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_linearized_nodedata_gurobi.out",this_test_file_directory+"farmer_linearized_nodedata_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_quadratic_sizes3_cplex(self):
        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES3"
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=40"+ \
                    " --rho-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"rhosetter.cfg"+ \
                    " --scenario-solver-options=mip_tolerances_integrality=1e-7"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.cfg"+ \
                    " --ww-extension-suffixfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.suffixes"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_quadratic_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_quadratic_cplex.out",this_test_file_directory+"sizes3_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_direct_available, "The 'cplex' python solver is not available")
    def test_quadratic_sizes3_cplex_direct(self):
        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES3"
        argstring = "runph --solver=cplex --solver-io=python --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=40"+ \
                    " --rho-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"rhosetter.cfg"+ \
                    " --scenario-solver-options=mip_tolerances_integrality=1e-7"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.cfg"+ \
                    " --ww-extension-suffixfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.suffixes"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_quadratic_cplex_direct.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_quadratic_cplex_direct.out",this_test_file_directory+"sizes3_quadratic_cplex_direct.baseline", filter=filter_time_and_data_dirs)        

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_quadratic_sizes3_gurobi(self):
        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES3"
        argstring = "runph --solver=gurobi --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=40"+ \
                    " --rho-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"rhosetter.cfg"+ \
                    " --scenario-solver-options=mip_tolerances_integrality=1e-7"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.cfg"+ \
                    " --ww-extension-suffixfile="+sizes_example_dir+os.sep+"config"+os.sep+"wwph.suffixes"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_quadratic_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()

        if os.sys.platform == "darwin":
            self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_quadratic_gurobi.out",this_test_file_directory+"sizes3_quadratic_gurobi_darwin.baseline", filter=filter_time_and_data_dirs)
        else:
            self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_quadratic_gurobi.out",this_test_file_directory+"sizes3_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_sizes10_quadratic_twobundles_cplex(self):
        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES10WithTwoBundles"
        argstring = "runph --solver=cplex --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=10"
        print "Testing command: " + argstring        

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes10_quadratic_twobundles_cplex.out")        
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes10_quadratic_twobundles_cplex.out",this_test_file_directory+"sizes10_quadratic_twobundles_cplex.baseline", filter=filter_time_and_data_dirs)            

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_sizes10_quadratic_twobundles_gurobi(self):
        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES10WithTwoBundles"
        argstring = "runph --solver=gurobi --solver-manager=serial --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=10"
        print "Testing command: " + argstring                

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes10_quadratic_twobundles_gurobi.out")        
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        if os.sys.platform == "darwin":
            self.assertFileEqualsBaseline(this_test_file_directory+"sizes10_quadratic_twobundles_gurobi.out",this_test_file_directory+"sizes10_quadratic_twobundles_gurobi_darwin.baseline", filter=filter_time_and_data_dirs)                        
        else:
            self.assertFileEqualsBaseline(this_test_file_directory+"sizes10_quadratic_twobundles_gurobi.out",this_test_file_directory+"sizes10_quadratic_twobundles_gurobi.baseline", filter=filter_time_and_data_dirs)                        

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_quadratic_networkflow1ef10_cplex(self):
        networkflow_example_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow_example_dir + os.sep + "models"
        instance_dir = networkflow_example_dir + os.sep + "1ef10"
        argstring = "runph --solver=cplex --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=100"+ \
                    " --rho-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"rhosettermixed.cfg"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"wwph-immediatefixing.cfg"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_quadratic_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_quadratic_cplex.out",this_test_file_directory+"networkflow1ef10_quadratic_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_quadratic_networkflow1ef10_gurobi(self):
        networkflow_example_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow_example_dir + os.sep + "models"
        instance_dir = networkflow_example_dir + os.sep + "1ef10"
        argstring = "runph --solver=gurobi --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=100"+ \
                    " --rho-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"rhosettermixed.cfg"+ \
                    " --enable-ww-extensions"+ \
                    " --ww-extension-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"wwph-immediatefixing.cfg"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_quadratic_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        if os.sys.platform == "darwin":
            self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_quadratic_gurobi.out",this_test_file_directory+"networkflow1ef10_quadratic_gurobi_darwin.baseline", filter=filter_time_and_data_dirs)
        else:
            self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_quadratic_gurobi.out",this_test_file_directory+"networkflow1ef10_quadratic_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_networkflow1ef10_cplex(self):
        networkflow_example_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow_example_dir + os.sep + "models"
        instance_dir = networkflow_example_dir + os.sep + "1ef10"
        argstring = "runph --solver=cplex --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=10"+ \
                    " --rho-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"rhosettermixed.cfg"+ \
                    " --linearize-nonbinary-penalty-terms=8"+ \
                    " --bounds-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"xboundsetter.cfg"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_linearized_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_linearized_cplex.out",this_test_file_directory+"networkflow1ef10_linearized_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_linearized_networkflow1ef10_gurobi(self):
        networkflow_example_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow_example_dir + os.sep + "models"
        instance_dir = networkflow_example_dir + os.sep + "1ef10"
        argstring = "runph --solver=gurobi --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=10"+ \
                    " --rho-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"rhosettermixed.cfg"+ \
                    " --linearize-nonbinary-penalty-terms=8"+ \
                    " --bounds-cfgfile="+networkflow_example_dir+os.sep+"config"+os.sep+"xboundsetter.cfg"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_linearized_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()

        if os.sys.platform == "darwin":
            self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_linearized_gurobi.out",this_test_file_directory+"networkflow1ef10_linearized_gurobi_darwin.baseline", filter=filter_time_and_data_dirs)
        else:
            self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_linearized_gurobi.out",this_test_file_directory+"networkflow1ef10_linearized_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_linearized_forestry_cplex(self):
        forestry_example_dir = pysp_examples_dir + "forestry"
        model_dir = forestry_example_dir + os.sep + "models-nb-yr"
        instance_dir = forestry_example_dir + os.sep + "18scenarios"
        argstring = "runph --solver=cplex --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=10" + " --scenario-mipgap=0.05" + " --default-rho=0.001" + \
                    " --rho-cfgfile="+forestry_example_dir+os.sep+"config"+os.sep+"rhosetter.cfg"+ \
                    " --linearize-nonbinary-penalty-terms=2"+ \
                    " --bounds-cfgfile="+forestry_example_dir+os.sep+"config"+os.sep+"boundsetter.cfg" + \
                    " --enable-ww-extension" + " --ww-extension-cfgfile="+forestry_example_dir+os.sep+"config"+os.sep+"wwph.cfg" + \
                    " --ww-extension-suffixfile="+forestry_example_dir+os.sep+"config"+os.sep+"wwph-nb.suffixes" + \
                    " --solve-ef"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"forestry_linearized_cplex.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()

        self.assertFileEqualsBaseline(this_test_file_directory+"forestry_linearized_cplex.out",this_test_file_directory+"forestry_linearized_cplex.baseline", filter=filter_time_and_data_dirs)            

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_linearized_forestry_gurobi(self):
        forestry_example_dir = pysp_examples_dir + "forestry"
        model_dir = forestry_example_dir + os.sep + "models-nb-yr"
        instance_dir = forestry_example_dir + os.sep + "18scenarios"
        argstring = "runph --solver=gurobi --model-directory="+model_dir+" --instance-directory="+instance_dir+ \
                    " --max-iterations=10" + " --scenario-mipgap=0.05" + " --default-rho=0.001" + \
                    " --rho-cfgfile="+forestry_example_dir+os.sep+"config"+os.sep+"rhosetter.cfg"+ \
                    " --linearize-nonbinary-penalty-terms=2"+ \
                    " --bounds-cfgfile="+forestry_example_dir+os.sep+"config"+os.sep+"boundsetter.cfg" + \
                    " --enable-ww-extension" + " --ww-extension-cfgfile="+forestry_example_dir+os.sep+"config"+os.sep+"wwph.cfg" + \
                    " --ww-extension-suffixfile="+forestry_example_dir+os.sep+"config"+os.sep+"wwph-nb.suffixes" + \
                    " --solve-ef"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"forestry_linearized_gurobi.out")
        args = string.split(argstring)
        coopr.pysp.phinit.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()

        if os.sys.platform == "darwin":
            self.assertFileEqualsBaseline(this_test_file_directory+"forestry_linearized_gurobi.out",this_test_file_directory+"forestry_linearized_gurobi_darwin.baseline", filter=filter_time_and_data_dirs)
        else:
            self.assertFileEqualsBaseline(this_test_file_directory+"forestry_linearized_gurobi.out",this_test_file_directory+"forestry_linearized_gurobi.baseline", filter=filter_time_and_data_dirs)

    def test_farmer_ef(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef.out",this_test_file_directory+"farmer_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"farmer_ef.baseline.lp")

    def test_farmer_maximize_ef(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "maxmodels"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"farmer_maximize_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_maximize_ef.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_maximize_ef.out",this_test_file_directory+"farmer_maximize_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"farmer_maximize_ef.baseline.lp")

    def test_farmer_ef_with_flattened_expressions(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_ef_with_flattening.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --flatten-expressions"
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef_with_flattening.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_with_flattening.out",this_test_file_directory+"farmer_ef_with_flattening.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"farmer_ef_with_flattening.baseline.lp")

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_ef_with_solve_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_with_solve_cplex.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --solver=cplex --solve"
        print "Testing command: " + argstring
        
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef_with_solve_cplex.out")        
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_with_solve_cplex.out",this_test_file_directory+"farmer_ef_with_solve_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_farmer_maximize_ef_with_solve_cplex(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "maxmodels"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_maximize_with_solve_cplex.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --solver=cplex --solve"
        print "Testing command: " + argstring
        
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_maximize_ef_with_solve_cplex.out")        
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_maximize_ef_with_solve_cplex.out",this_test_file_directory+"farmer_maximize_ef_with_solve_cplex.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_ef_with_solve_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_with_solve_gurobi.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --solver=gurobi --solve"
        print "Testing command: " + argstring
        
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef_with_solve_gurobi.out")        
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_with_solve_gurobi.out",this_test_file_directory+"farmer_ef_with_solve_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_farmer_maximize_ef_with_solve_gurobi(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "maxmodels"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_maximize_with_solve_gurobi.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --solver=gurobi --solve"
        print "Testing command: " + argstring
        
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_maximize_ef_with_solve_gurobi.out")        
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_maximize_ef_with_solve_gurobi.out",this_test_file_directory+"farmer_maximize_ef_with_solve_gurobi.baseline", filter=filter_time_and_data_dirs)

    @unittest.skipIf(not ipopt_available, "The 'ipopt' executable is not available")
    def test_farmer_ef_with_solve_ipopt(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_with_solve_ipopt.nl"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --solver=ipopt --solve"
        print "Testing command: " + argstring
        
        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef_with_solve_ipopt.out")        
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()

        if os.sys.platform == "darwin":
           self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_with_solve_ipopt.out",this_test_file_directory+"farmer_ef_with_solve_ipopt_darwin.baseline", filter=filter_time_and_data_dirs)                
        else:
           self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_with_solve_ipopt.out",this_test_file_directory+"farmer_ef_with_solve_ipopt.baseline", filter=filter_time_and_data_dirs)                

    def test_hydro_ef(self):
        hydro_examples_dir = pysp_examples_dir + "hydro"
        model_dir = hydro_examples_dir + os.sep + "models"
        instance_dir = hydro_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_hydro_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"hydro_ef.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"hydro_ef.out",this_test_file_directory+"hydro_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"hydro_ef.baseline.lp")

    def test_sizes3_ef(self):
        sizes3_examples_dir = pysp_examples_dir + "sizes"
        model_dir = sizes3_examples_dir + os.sep + "models"
        instance_dir = sizes3_examples_dir + os.sep + "SIZES3"
        ef_output_file = this_test_file_directory+"test_sizes3_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_ef.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_ef.out",this_test_file_directory+"sizes3_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"sizes3_ef.baseline.lp.gz")

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_sizes3_ef_with_solve_cplex(self):
        sizes3_examples_dir = pysp_examples_dir + "sizes"
        model_dir = sizes3_examples_dir + os.sep + "models"
        instance_dir = sizes3_examples_dir + os.sep + "SIZES3"
        ef_output_file = this_test_file_directory+"test_sizes3_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --solver=cplex --solve"
        print "Testing command: " + argstring        

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_ef_with_solve_cplex.out")        
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_ef_with_solve_cplex.out",this_test_file_directory+"sizes3_ef_with_solve_cplex.baseline", filter=filter_time_and_data_dirs)                

    @unittest.skipIf(not gurobi_available, "The 'gurobi' executable is not available")
    def test_sizes3_ef_with_solve_gurobi(self):
        sizes3_examples_dir = pysp_examples_dir + "sizes"
        model_dir = sizes3_examples_dir + os.sep + "models"
        instance_dir = sizes3_examples_dir + os.sep + "SIZES3"
        ef_output_file = this_test_file_directory+"test_sizes3_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file+" --solver=gurobi --solve"
        print "Testing command: " + argstring        

        pyutilib.misc.setup_redirect(this_test_file_directory+"sizes3_ef_with_solve_gurobi.out")        
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()

        if os.sys.platform == "darwin":
           self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_ef_with_solve_gurobi.out",this_test_file_directory+"sizes3_ef_with_solve_gurobi_darwin.baseline", filter=filter_time_and_data_dirs)        
        else:
           self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_ef_with_solve_gurobi.out",this_test_file_directory+"sizes3_ef_with_solve_gurobi.baseline", filter=filter_time_and_data_dirs)        

    def test_forestry_ef(self):
        forestry_examples_dir = pysp_examples_dir + "forestry"
        model_dir = forestry_examples_dir + os.sep + "models-nb-yr"
        instance_dir = forestry_examples_dir + os.sep + "18scenarios"
        ef_output_file = this_test_file_directory+"test_forestry_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"forestry_ef.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"forestry_ef.out",this_test_file_directory+"forestry_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"forestry_ef.baseline.lp.gz")

    def test_networkflow1ef10_ef(self):
        networkflow1ef10_examples_dir = pysp_examples_dir + "networkflow"
        model_dir = networkflow1ef10_examples_dir + os.sep + "models"
        instance_dir = networkflow1ef10_examples_dir + os.sep + "1ef10"
        ef_output_file = this_test_file_directory+"test_networkflow1ef10_ef.lp"
        argstring = "runef --verbose --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"networkflow1ef10_ef.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"networkflow1ef10_ef.out",this_test_file_directory+"networkflow1ef10_ef.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"networkflow1ef10_ef.baseline.lp.gz")

    def test_farmer_ef_cvar(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        ef_output_file = this_test_file_directory+"test_farmer_ef_cvar.lp"
        argstring = "runef --verbose --generate-weighted-cvar --risk-alpha=0.90 --cvar-weight=0.0 --model-directory="+model_dir+" --instance-directory="+instance_dir+" --output-file="+ef_output_file
        print "Testing command: " + argstring

        pyutilib.misc.setup_redirect(this_test_file_directory+"farmer_ef_cvar.out")
        args = string.split(argstring)
        coopr.pysp.ef_writer_script.main(args=args)
        pyutilib.misc.reset_redirect()
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_cvar.out",this_test_file_directory+"farmer_ef_cvar.baseline.out", filter=filter_time_and_data_dirs)
        self.assertFileEqualsBaseline(ef_output_file,this_test_file_directory+"farmer_ef_cvar.baseline.lp")

class TestPHParallel(unittest.TestCase):

    def cleanup(self):

        # IMPT: This step is key, as Python keys off the name of the module, not the location.
        #       So, different reference models in different directories won't be detected.
        #       If you don't do this, the symptom is a model that doesn't have the attributes
        #       that the data file expects.
        if "ReferenceModel" in sys.modules:
            del sys.modules["ReferenceModel"]

    @unittest.skipIf(not cplex_available or not mpirun_available, "Either the 'cplex' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_cplex_with_pyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 pyro_mip_server : -np 1 runph --solver=cplex --solver-manager=pyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_cplex_with_pyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_cplex_with_pyro.out",this_test_file_directory+"farmer_quadratic_cplex_with_pyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not cplex_available or not mpirun_available, "Either the 'cplex' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_cplex_with_phpyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        server1string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=BelowAverageScenario --solver=cplex"
        server2string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=AverageScenario --solver=cplex"
        server3string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=AboveAverageScenario --solver=cplex"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 "+server1string+" : -np 1 "+server2string+" : -np 1 "+server3string+" : -np 1 runph --solver=cplex --solver-manager=phpyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_cplex_with_phpyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_cplex_with_phpyro.out",this_test_file_directory+"farmer_quadratic_cplex_with_phpyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not cplex_available or not mpirun_available, "Either the 'cplex' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_with_bundles_cplex_with_pyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTwoBundles"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 pyro_mip_server : -np 1 runph --solver=cplex --solver-manager=pyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_with_bundles_cplex_with_pyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_with_bundles_cplex_with_pyro.out",this_test_file_directory+"farmer_quadratic_with_bundles_cplex_with_pyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not gurobi_available or not mpirun_available, "Either the 'gurobi' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_gurobi_with_phpyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        server1string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=BelowAverageScenario --solver=gurobi"
        server2string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=AverageScenario --solver=gurobi"
        server3string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=AboveAverageScenario --solver=gurobi"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 "+server1string+" : -np 1 "+server2string+" : -np 1 "+server3string+" : -np 1 runph --solver=gurobi --solver-manager=phpyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_gurobi_with_phpyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_gurobi_with_phpyro.out",this_test_file_directory+"farmer_quadratic_gurobi_with_phpyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not ipopt_available or not mpirun_available, "Either the 'ipopt' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_ipopt_with_pyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 pyro_mip_server : -np 1 runph --solver=ipopt --solver-manager=pyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_ipopt_with_pyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_ipopt_with_pyro.out",this_test_file_directory+"farmer_quadratic_ipopt_with_pyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not ipopt_available or not mpirun_available, "Either the 'ipopt' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_ipopt_with_phpyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        server1string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=BelowAverageScenario --solver=ipopt"
        server2string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=AverageScenario --solver=ipopt"
        server3string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=AboveAverageScenario --solver=ipopt"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 "+server1string+" : -np 1 "+server2string+" : -np 1 "+server3string+" : -np 1 runph --solver=ipopt --solver-manager=phpyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_ipopt_with_phpyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_ipopt_with_phpyro.out",this_test_file_directory+"farmer_quadratic_ipopt_with_phpyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not ipopt_available or not mpirun_available, "Either the 'ipopt' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_trivial_bundling_ipopt_with_phpyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTrivialBundles"
        server1string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --bundle=BelowAverageBundle --solver=ipopt"
        server2string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --bundle=AverageBundle --solver=ipopt"
        server3string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --bundle=AboveAverageBundle --solver=ipopt"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 "+server1string+" : -np 1 "+server2string+" : -np 1 "+server3string+" : -np 1 runph --solver=ipopt --solver-manager=phpyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_trivial_bundling_ipopt_with_phpyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_trivial_bundling_ipopt_with_phpyro.out",this_test_file_directory+"farmer_quadratic_trivial_bundling_ipopt_with_phpyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not ipopt_available or not mpirun_available, "Either the 'ipopt' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_quadratic_bundling_ipopt_with_phpyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodataWithTwoBundles"
        server1string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --bundle=BelowAverageBundle --solver=ipopt"
        server2string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --bundle=OtherBundle --solver=ipopt"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 "+server1string+" : -np 1 "+server2string+" : -np 1 runph --solver=ipopt --solver-manager=phpyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_quadratic_bundling_ipopt_with_phpyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_quadratic_bundling_ipopt_with_phpyro.out",this_test_file_directory+"farmer_quadratic_bundling_ipopt_with_phpyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not cplex_available or not mpirun_available, "Either the 'cplex' executable is not available or the 'mpirun' executable is not available")
    def test_quadratic_sizes3_cplex_with_phpyro(self):
        sizes_example_dir = pysp_examples_dir + "sizes"
        model_dir = sizes_example_dir + os.sep + "models"
        instance_dir = sizes_example_dir + os.sep + "SIZES3"        
        server1string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=Scenario1 --solver=cplex"
        server2string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=Scenario2 --solver=cplex"
        server3string = "phsolverserver -m "+model_dir+" -i "+instance_dir+" --scenario=Scenario3 --solver=cplex"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 "+server1string+" : -np 1 "+server2string+" : -np 1 "+server3string+" : -np 1 runph --solver=cplex --solver-manager=phpyro --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"sizes3_quadratic_cplex_with_phpyro.out"
        print "Testing command: " + argstring

        os.system(argstring)        
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"sizes3_quadratic_cplex_with_phpyro.out",this_test_file_directory+"sizes3_quadratic_cplex_with_phpyro.baseline", filter=filter_pyro)

    @unittest.skipIf(not cplex_available or not mpirun_available, "Either the 'cplex' executable is not available or the 'mpirun' executable is not available")
    def test_farmer_ef_with_solve_cplex_with_pyro(self):
        farmer_examples_dir = pysp_examples_dir + "farmer"
        model_dir = farmer_examples_dir + os.sep + "models"
        instance_dir = farmer_examples_dir + os.sep + "scenariodata"
        argstring = "mpirun -np 1 coopr_ns : -np 1 dispatch_srvr : -np 1 pyro_mip_server : -np 1 runef --verbose --solver=cplex --solver-manager=pyro --solve --shutdown-pyro --model-directory="+model_dir+" --instance-directory="+instance_dir+" >& "+this_test_file_directory+"farmer_ef_with_solve_cplex_with_pyro.out"
        print "Testing command: " + argstring

        os.system(argstring)
        self.cleanup()
        self.assertFileEqualsBaseline(this_test_file_directory+"farmer_ef_with_solve_cplex_with_pyro.out",this_test_file_directory+"farmer_ef_with_solve_cplex_with_pyro.baseline", filter=filter_pyro)                

TestPH = unittest.category('nightly', 'performance')(TestPH)

TestPHParallel = unittest.category('parallel', 'performance')(TestPHParallel)

if __name__ == "__main__":
    unittest.main()
