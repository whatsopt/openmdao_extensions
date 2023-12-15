"""
Driver for running model on design of experiments cases using egobox LHS method
"""
import numpy as np

from openmdao.api import DOEDriver
from openmdao.drivers.doe_generators import DOEGenerator

EGOBOX_NOT_INSTALLED = False
try:
    import egobox as egx
except ImportError:
    EGOBOX_NOT_INSTALLED = True


class EgoboxDOEGenerator(DOEGenerator):
    def __init__(self, n_cases, **kwargs):
        super(EgoboxDOEGenerator, self).__init__(**kwargs)

        if EGOBOX_NOT_INSTALLED:
            raise RuntimeError(
                "egobox library is not installed. Run `pip install egobox` to do so."
            )

        # number of cases
        self.n_cases = n_cases

    def __call__(self, design_vars, model=None):
        x_specs = []
        for name, meta in design_vars.items():
            infos = model.get_io_metadata(includes=name)
            dvs_int = {}
            for absname in infos:
                if name == infos[absname]["prom_name"] and (
                    infos[absname]["tags"] & {"wop:int"}
                ):
                    dvs_int[name] = egx.XType.INT

            size = meta["size"]
            meta_low = meta["lower"]
            meta_high = meta["upper"]

            print(name)
            for j in range(size):
                if isinstance(meta_low, np.ndarray):
                    p_low = meta_low[j]
                else:
                    p_low = meta_low

                if isinstance(meta_high, np.ndarray):
                    p_high = meta_high[j]
                else:
                    p_high = meta_high

                if name in dvs_int:
                    x_specs.append(egx.XSpec(egx.XType.INT, [p_low, p_high]))
                else:
                    x_specs.append(egx.XSpec(egx.XType.FLOAT, [p_low, p_high]))
        cases = egx.lhs(x_specs, self.n_cases)
        sample = []
        for i in range(cases.shape[0]):
            j = 0
            for name, meta in design_vars.items():
                size = meta["size"]
                sample.append((name, cases[i, j : j + size]))
                j += size
            yield sample


class EgoboxDOEDriver(DOEDriver):
    """
    Baseclass for egobox design-of-experiments LHS driver.
    """

    def __init__(self, **kwargs):
        super().__init__()

        if EGOBOX_NOT_INSTALLED:
            raise RuntimeError(
                "egobox library is not installed. Run `pip install egobox` to do so."
            )

        self.options.declare(
            "n_cases", types=int, default=2, desc="number of sample to generate"
        )
        self.options.update(kwargs)
        n_cases = self.options["n_cases"]
        self.options["generator"] = EgoboxDOEGenerator(n_cases=n_cases)

    def _set_name(self):
        self._name = "egobox_DOE_LHS"
