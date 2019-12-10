import os
import unittest
from openmdao.api import SqliteRecorder, CaseReader
from openmdao.test_suite.components.sellar import SellarProblem
from openmdao_extensions.smt_doe_driver import SmtDOEDriver, SmtDoeDriver
from openmdao_extensions.smt_doe_driver import SMT_NOT_INSTALLED
from openmdao.utils.assert_utils import assert_warning


class TestSmtDoeDriver(unittest.TestCase):
    def assert_case_generation(self, n, driver):
        pb = SellarProblem()
        pb.driver = driver
        case_recorder_filename = "test_smt_doe_driver_{}.sqlite".format(n)
        recorder = SqliteRecorder(case_recorder_filename)
        pb.driver.add_recorder(recorder)
        pb.setup()
        pb.run_driver()
        pb.cleanup()

        reader = CaseReader(case_recorder_filename)
        cases = reader.list_cases("driver")
        os.remove(case_recorder_filename)
        self.assertEqual(len(cases), n)
        # for i in range(len(cases)):
        #     case = reader.get_case(cases[i])
        #     print(case)

    @unittest.skipIf(SMT_NOT_INSTALLED, "SMT library is not installed")
    def test_smt_lhs_doe_driver(self):
        n = 10
        self.assert_case_generation(
            n,
            SmtDOEDriver(
                sampling_method_name="LHS",
                n_cases=n,
                sampling_method_options={"criterion": "ese"},
            ),
        )

    @unittest.skipIf(SMT_NOT_INSTALLED, "SMT library is not installed")
    def test_smt_ff_doe_driver(self):
        n = 11
        self.assert_case_generation(
            n, SmtDOEDriver(sampling_method_name="FullFactorial", n_cases=n)
        )

    @unittest.skipIf(SMT_NOT_INSTALLED, "SMT library is not installed")
    def test_smt_rand_doe_driver(self):
        n = 12
        self.assert_case_generation(
            n, SmtDOEDriver(sampling_method_name="Random", n_cases=n)
        )

    @unittest.skipIf(SMT_NOT_INSTALLED, "SMT library is not installed")
    def test_deprecated(self):
        msg = "'SmtDoeDriver' is deprecated; " "use 'SmtDOEDriver' instead."
        with assert_warning(DeprecationWarning, msg):
            SmtDoeDriver()


if __name__ == "__main__":
    unittest.main()
