import os
import unittest
from openmdao.api import SqliteRecorder, CaseReader
from openmdao.test_suite.components.sellar import SellarProblem
from openmdao_extensions.salib_doe_driver import SalibDOEDriver
from openmdao_extensions.salib_doe_driver import SALIB_NOT_INSTALLED


class TestSalibDoeDriver(unittest.TestCase):
    @staticmethod
    def run_driver(name, driver):
        pb = SellarProblem()
        case_recorder_filename = "test_salib_doe_{}.sqlite".format(name)
        recorder = SqliteRecorder(case_recorder_filename)
        pb.driver = driver
        pb.driver.add_recorder(recorder)
        pb.setup()
        pb.run_driver()
        pb.cleanup()
        return pb, case_recorder_filename

    def assert_morris_case_generation(self, nt, driver):
        pb, case_recorder_filename = TestSalibDoeDriver.run_driver(
            "morris" + str(nt), driver
        )

        self.assertTrue(os.path.exists(case_recorder_filename))
        reader = CaseReader(case_recorder_filename)
        cases = reader.list_cases("driver")
        os.remove(case_recorder_filename)
        n = sum(data["size"] for data in pb.model.get_design_vars().values())
        self.assertEqual(len(cases), (n + 1) * nt)

    @unittest.skipIf(SALIB_NOT_INSTALLED, "SALib library is not installed")
    def test_salib_morris_driver(self):
        nt = 4
        driver = SalibDOEDriver(sa_method_name="Morris", sa_doe_options={"n_trajs": nt})
        self.assert_morris_case_generation(nt, driver)
        salib_cases = driver.get_cases()
        self.assertTrue(len(salib_cases) > 0)
        salib_pb = driver.get_salib_problem()
        self.assertTrue(salib_pb)

    @unittest.skipIf(SALIB_NOT_INSTALLED, "SALib library is not installed")
    def test_salib_sobol_driver(self):
        ns = 100
        driver = SalibDOEDriver(
            sa_method_name="Sobol",
            sa_doe_options={"n_samples": ns, "calc_second_order": True},
        )
        TestSalibDoeDriver.run_driver("sobol", driver)
        salib_cases = driver.get_cases()
        self.assertTrue(len(salib_cases) > 0)
        salib_pb = driver.get_salib_problem()
        self.assertTrue(salib_pb)

    # @unittest.skipIf(SALIB_NOT_INSTALLED, 'SALib library is not installed')
    # def test_doe_generator(self):
    #     nt = 5
    #     self.assert_morris_case_generation(nt, DOEDriver(SalibMorrisDOEGenerator(n_trajs=nt, n_levels=4)))


if __name__ == "__main__":
    unittest.main()
