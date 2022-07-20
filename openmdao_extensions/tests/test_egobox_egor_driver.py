import os
import unittest
from openmdao.api import (
    Problem,
    SqliteRecorder,
    CaseReader,
)
from openmdao.test_suite.components.sellar_feature import SellarMDA
from openmdao_extensions.egobox_egor_driver import EgoboxEgorDriver
from openmdao_extensions.egobox_egor_driver import EGOBOX_NOT_INSTALLED

from openmdao_extensions.tests.functions_test import BraninMDA, AckleyMDA


class TestEgor(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(EGOBOX_NOT_INSTALLED, "egobox is not installed")
    def test_sellar(self):
        self.pb = pb = Problem(SellarMDA())
        pb.model.add_design_var("x", lower=0, upper=10)
        pb.model.add_design_var("z", lower=0, upper=10)
        pb.model.add_objective("obj")
        pb.model.add_constraint("con1", upper=0)
        pb.model.add_constraint("con2", upper=0)
        pb.driver = EgoboxEgorDriver(optimizer="EGOR")
        pb.driver.opt_settings["maxiter"] = 10
        self.case_recorder_filename = "test_egobox_driver_sellar.sqlite"
        recorder = SqliteRecorder(self.case_recorder_filename)
        pb.model.add_recorder(recorder)
        pb.setup()
        self.pb.run_driver()
        self.assertTrue(os.path.exists(self.case_recorder_filename))
        reader = CaseReader(self.case_recorder_filename)
        for case_id in reader.list_cases():
            case = reader.get_case(case_id)
            print(case.outputs["obj"])

    @unittest.skipIf(EGOBOX_NOT_INSTALLED, "egobox is not installed")
    def test_branin(self):
        self.pb = pb = Problem(BraninMDA())
        pb.model.add_design_var("x1", lower=-5, upper=10)
        pb.model.add_design_var("x2", lower=0, upper=15)
        pb.model.add_objective("obj")
        pb.model.add_constraint("con", upper=0)
        self.case_recorder_filename = "test_egobox_driver_branin.sqlite"
        self._check_recorder_file(pb, cstr=True, filename=self.case_recorder_filename)

    @unittest.skipIf(EGOBOX_NOT_INSTALLED, "egobox is not installed")
    def test_ackley(self):
        self.pb = pb = Problem(AckleyMDA())
        pb.model.add_design_var("x", lower=-32.768, upper=32.768)
        pb.model.add_objective("obj")
        self.case_recorder_filename = "test_egobox_driver_ackley.sqlite"
        self._check_recorder_file(pb, cstr=False, filename=self.case_recorder_filename)

    def _check_recorder_file(self, pb, cstr, filename):
        pb.driver = EgoboxEgorDriver()
        pb.driver.options["optimizer"] = "EGOR"
        pb.driver.opt_settings["maxiter"] = 10
        recorder = SqliteRecorder(self.case_recorder_filename)
        pb.model.add_recorder(recorder)
        pb.setup()
        self.pb.run_driver()
        self.assertTrue(os.path.exists(self.case_recorder_filename))
        reader = CaseReader(self.case_recorder_filename)
        for case_id in reader.list_cases():
            case = reader.get_case(case_id)
            print(case.outputs["obj"])


if __name__ == "__main__":
    unittest.main()
