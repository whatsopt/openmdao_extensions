import os
import unittest
from six import itervalues
from openmdao.api import IndepVarComp, Problem, SqliteRecorder, CaseReader, DOEDriver
from openmdao.test_suite.components.sellar import SellarProblem
from openmdao_extensions.openturns_doe_driver import OpenturnsDOEDriver
from openmdao_extensions.openturns_doe_driver import OPENTURNS_NOT_INSTALLED


class TestOpenturnsDoeDriver(unittest.TestCase):
    @staticmethod
    def run_driver(name, driver):
        pb = SellarProblem()
        case_recorder_filename = "test_openturns_doe_{}.sqlite".format(name)
        recorder = SqliteRecorder(case_recorder_filename)
        pb.driver = driver
        pb.driver.add_recorder(recorder)
        pb.setup()
        pb.run_driver()
        pb.cleanup()
        return pb, case_recorder_filename

    def test_openturns_doe_driver(self):
        ns = 100
        driver = OpenturnsDOEDriver(n_samples=ns)
        TestOpenturnsDoeDriver.run_driver("mc", driver)
        ot_cases = driver.get_cases()
        self.assertTrue(len(ot_cases) > 0)


if __name__ == "__main__":
    unittest.main()
