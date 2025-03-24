import os
import unittest
from openmdao.api import (
    Problem,
    SqliteRecorder,
    CaseReader,
)
from openmdao.test_suite.components.sellar_feature import SellarMDA
from openmdao_extensions.onera_sego_driver import OneraSegoDriver
from openmdao_extensions.onera_sego_driver import ONERASEGO_NOT_INSTALLED

from openmdao_extensions.tests.functions_test import BraninMDA, AckleyMDA


class TestSegoMoe(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass  # os.remove(self.case_recorder_filename)

    @unittest.skipIf(ONERASEGO_NOT_INSTALLED, "SEGOMOE is not installed")
    def test_sellar(self):
        self.pb = pb = Problem(SellarMDA())
        pb.model.add_design_var("x", lower=0, upper=10)
        pb.model.add_design_var("z", lower=0, upper=10)
        pb.model.add_objective("obj")
        pb.model.add_constraint("con1", upper=0)
        pb.model.add_constraint("con2", upper=0)
        pb.driver = OneraSegoDriver(optimizer="SEGOMOE")
        pb.driver.opt_settings["maxiter"] = 10
        pb.setup()

        self.case_recorder_filename = "{}/test_segomoe_driver_sellar.sqlite".format(
            pb.get_outputs_dir()
        )
        recorder = SqliteRecorder(self.case_recorder_filename)
        pb.model.add_recorder(recorder)
        self.pb.run_driver()

        self.assertTrue(os.path.exists(self.case_recorder_filename))
        reader = CaseReader(self.case_recorder_filename)
        for case_id in reader.list_cases():
            case = reader.get_case(case_id)
            print(case.outputs["obj"])

    @unittest.skipIf(ONERASEGO_NOT_INSTALLED, "SEGOMOE is not installed")
    def test_branin(self):
        self.pb = pb = Problem(BraninMDA())
        pb.model.add_design_var("x1", lower=-5, upper=10)
        pb.model.add_design_var("x2", lower=0, upper=15)
        pb.model.add_objective("obj")
        pb.model.add_constraint("con", upper=0)
        case_recorder_filename = "test_segomoe_driver_branin.sqlite"
        self._check_recorder_file(pb, cstr=True, filename=case_recorder_filename)

    @unittest.skipIf(ONERASEGO_NOT_INSTALLED, "SEGOMOE is not installed")
    def test_ackley(self):
        self.pb = pb = Problem(AckleyMDA())
        pb.model.add_design_var("x", lower=-32.768, upper=32.768)
        pb.model.add_objective("obj")
        case_recorder_filename = "test_segomoe_driver_ackley.sqlite"
        self._check_recorder_file(pb, cstr=False, filename=case_recorder_filename)

    def _check_recorder_file(self, pb, cstr, filename):
        pb.driver = OneraSegoDriver()
        pb.driver.options["optimizer"] = "SEGOMOE"
        pb.driver.opt_settings["maxiter"] = 10
        # default model
        n_var = 2
        mod_obj = {
            "name": "KRG",
            "corr": "squar_exp",
            "regr": "constant",
            "theta0": [1.0] * n_var,
            "thetaL": [0.1] * n_var,
            "thetaU": [10.0] * n_var,
            "normalize": True,
        }
        model_type = {"obj": mod_obj}
        if cstr:
            model_type["con"] = mod_obj
        pb.driver.opt_settings["model_type"] = model_type
        pb.setup()

        self.case_recorder_file_name = "{}/{}".format(pb.get_outputs_dir(), filename)
        recorder = SqliteRecorder(self.case_recorder_filename)
        pb.model.add_recorder(recorder)

        self.pb.run_driver()
        self.assertTrue(os.path.exists(self.case_recorder_filename))
        reader = CaseReader(self.case_recorder_filename)
        for case_id in reader.list_cases():
            case = reader.get_case(case_id)
            print(case.outputs["obj"])


if __name__ == "__main__":
    unittest.main()
