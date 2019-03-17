import os
import unittest
from six import itervalues
import tempfile
from openmdao.api import IndepVarComp, Problem, Group, SqliteRecorder, CaseReader, DOEDriver, FullFactorialGenerator
from openmdao.test_suite.components.sellar import SellarProblem
from openmdao_extensions.salib_doe_driver import SalibMorrisDOEDriver, SalibMorrisDOEGenerator, SalibDoeDriver
from openmdao_extensions.salib_doe_driver import SALIB_NOT_INSTALLED
from openmdao.utils.assert_utils import assert_warning
class TestSalibDoeDriver(unittest.TestCase):
        
    def assert_case_generation(self, nt, driver):
        pb = SellarProblem()        
        case_recorder_filename = "test_salib_doe_{}.sqlite".format(nt)
        recorder = SqliteRecorder(case_recorder_filename)
        pb.driver = driver
        pb.driver.add_recorder(recorder)
        pb.setup()
        pb.run_driver()
        pb.cleanup()

        assert os.path.exists(case_recorder_filename)
        reader = CaseReader(case_recorder_filename)
        cases = reader.list_cases('driver')
        os.remove(case_recorder_filename)
        n = sum(data['size'] for data in itervalues(pb.model.get_design_vars()))
        self.assertEqual(len(cases), (n+1)*nt)

    @unittest.skipIf(SALIB_NOT_INSTALLED, 'SALib library is not installed')
    def test_salib_doe_driver(self):
        nt = 4
        self.assert_case_generation(nt, SalibMorrisDOEDriver(n_trajs=nt))

    @unittest.skipIf(SALIB_NOT_INSTALLED, 'SALib library is not installed')
    def test_doe_generator(self): 
        nt = 5
        self.assert_case_generation(nt, DOEDriver(SalibMorrisDOEGenerator(n_trajs=nt)))

    @unittest.skipIf(SALIB_NOT_INSTALLED, 'SALib library is not installed')
    def test_deprecated(self):
        msg = "'SalibDoeDriver' is deprecated; " \
                "use 'SalibMorrisDOEDriver' instead."
        with assert_warning(DeprecationWarning, msg):
            SalibDoeDriver()

if __name__ == '__main__':
    unittest.main()
