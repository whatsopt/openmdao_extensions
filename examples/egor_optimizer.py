import openmdao.api as om
from openmdao.test_suite.components.sellar_feature import SellarMDA
from openmdao_extensions.egobox_egor_driver import EgoboxEgorDriver

import egobox as egx

# To display Egor optimizer traces
# import logging
# logging.basicConfig(level=logging.INFO)

prob = om.Problem()
prob.model = SellarMDA()

prob.model.add_design_var("x", lower=0, upper=10)
prob.model.add_design_var("z", lower=0, upper=10)
prob.model.add_objective("obj")
prob.model.add_constraint("con1", upper=0)
prob.model.add_constraint("con2", upper=0)

prob.driver = EgoboxEgorDriver()

# To display available options
# help(egx.Egor)
prob.driver.opt_settings["maxiter"] = 20
prob.driver.opt_settings["infill_strategy"] = egx.InfillStrategy.WB2
prob.driver.opt_settings["infill_optimizer"] = egx.InfillOptimizer.SLSQP

prob.setup()
prob.set_solver_print(level=0)

prob.run_driver()

print("minimum found at")
print(prob.get_val("x")[0])
print(prob.get_val("z"))

print("minimum objective")
print(prob.get_val("obj")[0])
