import os
import unittest
from openmdao.api import IndepVarComp, Problem, Group, SqliteRecorder, CaseReader, DOEDriver, FullFactorialGenerator
from openmdao.test_suite.components.sellar import SellarProblem
from openmdao_extensions.salib_doe_driver import SalibMorrisDOEDriver, SalibMorrisDOEGenerator, SalibDoeDriver
from openmdao_extensions.salib_doe_driver import SALIB_NOT_INSTALLED

class TestSalibDoeDriver(unittest.TestCase):

    def setUp(self):
        self.pb = SellarProblem()        
        self.case_recorder_filename = 'test_salib_doe_driver.sqlite'
        self.recorder = SqliteRecorder(self.case_recorder_filename)
        
    def tearDown(self):
        if os.path.exists(self.case_recorder_filename):
            os.remove(self.case_recorder_filename)
        
    @unittest.skipIf(SALIB_NOT_INSTALLED, 'SALib library is not installed')
    def test_salib_doe_driver(self):
        pb = self.pb
        pb.driver = SalibMorrisDOEDriver()
        pb.driver.add_recorder(self.recorder)
        pb.setup()
        self.pb.run_driver()
        self.pb.cleanup()
        assert os.path.exists(self.case_recorder_filename)
        reader = CaseReader(self.case_recorder_filename)
        cases = reader.list_cases('driver')
        self.assertEqual(len(cases), 8)
        for i in range(len(cases)):
            case = reader.get_case(cases[i])

    @unittest.skipIf(SALIB_NOT_INSTALLED, 'SALib library is not installed')
    def test_doe_run(self): 
        # create a list of DOE cases
        pb = self.pb
        pb.driver = DOEDriver(SalibMorrisDOEGenerator())
        pb.driver.add_recorder(self.recorder)
        pb.setup()

        self.pb.run_driver()
        self.pb.cleanup()
        assert os.path.exists(self.case_recorder_filename)
        reader = CaseReader(self.case_recorder_filename)
        cases = reader.list_cases('driver')
        self.assertEqual(len(cases), 8)
        for i in range(len(cases)):
            case = reader.get_case(cases[i])

    def test_deprecated(self):
        driver = SalibDoeDriver()

if __name__ == '__main__':
    unittest.main()
