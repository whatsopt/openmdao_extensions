import os
import unittest
from openmdao.api import IndepVarComp, Problem, Group, SqliteRecorder, CaseReader
from openmdao.test_suite.components.sellar_feature import SellarDis1, SellarDis2, SellarMDA
from openmdao_extensions.smt_doe_driver import SmtDoeDriver
from openmdao_extensions.smt_doe_driver import SMT_NOT_INSTALLED

class TestSmtDoeDriver(unittest.TestCase):

    def setUp(self):
        self.pb = pb = Problem(SellarMDA())
        pb.driver = SmtDoeDriver(sampling_method='LHS', n_cases=10)
        
        self.case_recorder_filename = 'test_smt_doe_driver.sqlite'
        recorder = SqliteRecorder(self.case_recorder_filename)

        pb.model.add_recorder(recorder)
        pb.model.nonlinear_solver.add_recorder(recorder)
        
        pb.setup()
        
    def tearDown(self):
        if os.path.exists(self.case_recorder_filename):
            os.remove(self.case_recorder_filename)
        
    @unittest.skipIf(SMT_NOT_INSTALLED, 'SMT library is not installed')
    def test_doe_run(self):
        self.pb.run_driver()
        self.pb.cleanup()
        assert os.path.exists(self.case_recorder_filename)
        reader = CaseReader(self.case_recorder_filename)
        cases = reader.list_cases('root')
        for i in range(len(cases)):
            case = reader.get_case(cases[i])
            print(case.inputs['x'])
            print(case.inputs['z'])
            print(case.outputs['y1'])
            print(case.outputs['y2'])
            print(case.outputs['con1'])
            print(case.outputs['con2'])
            print(case.outputs['obj'])

if __name__ == '__main__':
    unittest.main()
