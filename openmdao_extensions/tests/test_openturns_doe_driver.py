import unittest
from openmdao.api import IndepVarComp, Problem, SqliteRecorder, CaseReader
from openmdao.test_suite.components.sellar import SellarProblem
from openmdao_extensions.openturns_doe_driver import OpenturnsDOEDriver
from openmdao_extensions.openturns_doe_driver import OPENTURNS_NOT_INSTALLED
import openturns as ot


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

    @unittest.skipIf(OPENTURNS_NOT_INSTALLED, "OpenTURNS not installed")
    def test_openturns_doe_driver(self):
        ns = 100
        driver = OpenturnsDOEDriver(n_samples=ns)
        TestOpenturnsDoeDriver.run_driver("mc", driver)
        cases = driver.get_cases()
        self.assertEqual((100, 3), cases.shape)

    @unittest.skipIf(OPENTURNS_NOT_INSTALLED, "OpenTURNS not installed")
    def test_openturns_doe_driver_with_dist(self):
        ns = 100
        dists = [ot.Normal(2, 1), ot.Normal(5, 1), ot.Normal(2, 1)]
        driver = OpenturnsDOEDriver(
            n_samples=ns, distribution=ot.ComposedDistribution(dists)
        )
        TestOpenturnsDoeDriver.run_driver("mc", driver)
        cases = driver.get_cases()
        self.assertEqual((100, 3), cases.shape)

    @unittest.skipIf(OPENTURNS_NOT_INSTALLED, "OpenTURNS not installed")
    def test_bad_dist(self):
        ns = 100
        dists = [ot.Normal(2, 1), ot.Normal(5, 1)]
        driver = OpenturnsDOEDriver(
            n_samples=ns, distribution=ot.ComposedDistribution(dists)
        )

        with self.assertRaises(RuntimeError):
            TestOpenturnsDoeDriver.run_driver("mc", driver)


if __name__ == "__main__":
    unittest.main()
