import os
import unittest
from openmdao.api import SqliteRecorder, CaseReader
from openmdao.test_suite.components.sellar import SellarProblem
from openmdao_extensions.egobox_doe_driver import EgoboxDOEDriver
from openmdao_extensions.egobox_doe_driver import EGOBOX_NOT_INSTALLED


class TestEgoboxDoeDriver(unittest.TestCase):
    def assert_case_generation(self, n, driver):
        pb = SellarProblem()
        pb.driver = driver
        case_recorder_filename = "test_egobox_doe_driver_{}.sqlite".format(n)
        recorder = SqliteRecorder(case_recorder_filename)
        pb.driver.add_recorder(recorder)
        pb.setup()
        pb.run_driver()
        pb.cleanup()

        reader = CaseReader(case_recorder_filename)
        cases = reader.list_cases("driver")
        os.remove(case_recorder_filename)
        self.assertEqual(len(cases), n)
        for i in range(len(cases)):
            case = reader.get_case(cases[i])
            print(case)

    @unittest.skipIf(EGOBOX_NOT_INSTALLED, "EGOBOX library is not installed")
    def test_egobox_lhs_doe_driver(self):
        n = 10
        self.assert_case_generation(
            n,
            EgoboxDOEDriver(n_cases=n),
        )


if __name__ == "__main__":
    unittest.main()
