"""
Driver for running model on design of experiments cases using SMT sampling methods
"""
from __future__ import print_function
from six import iteritems
import numpy as np

from openmdao.api import DOEDriver
from openmdao.drivers.doe_generators import DOEGenerator
from openmdao.utils.general_utils import warn_deprecation

SMT_NOT_INSTALLED = False
try:
    from smt.sampling_methods import FullFactorial, LHS, Random
except ImportError:
    SMT_NOT_INSTALLED = False

_sampling_methods = {"FullFactorial": FullFactorial, "LHS": LHS, "Random": Random}


class SmtDOEGenerator(DOEGenerator):
    def __init__(self, sampling_method_name, n_cases, **kwargs):
        super(SmtDOEGenerator, self).__init__()

        if SMT_NOT_INSTALLED:
            raise RuntimeError(
                "SMT library is not installed. cf. https://https://smt.readthedocs.io/en/latest"
            )

        # number of trajectories to apply morris method
        self.sampling_method_name = sampling_method_name
        # number of grid levels
        self.n_cases = n_cases
        # options
        self.sampling_method_opts = kwargs

    def __call__(self, design_vars, model=None):
        xlimits = []
        for name, meta in iteritems(design_vars):
            size = meta["size"]
            meta_low = meta["lower"]
            meta_high = meta["upper"]
            for j in range(size):
                if isinstance(meta_low, np.ndarray):
                    p_low = meta_low[j]
                else:
                    p_low = meta_low

                if isinstance(meta_high, np.ndarray):
                    p_high = meta_high[j]
                else:
                    p_high = meta_high

                xlimits.append((p_low, p_high))

        sampling = _sampling_methods[self.sampling_method_name](
            xlimits=np.array(xlimits), **(self.sampling_method_opts)
        )
        cases = sampling(self.n_cases)
        sample = []
        for i in range(cases.shape[0]):
            j = 0
            for name, meta in iteritems(design_vars):
                size = meta["size"]
                sample.append((name, cases[i, j : j + size]))
                j += size
            yield sample


class SmtDOEDriver(DOEDriver):
    """
    Baseclass for SMT design-of-experiments Drivers.
    """

    def __init__(self, **kwargs):
        super(SmtDOEDriver, self).__init__()

        if SMT_NOT_INSTALLED:
            raise RuntimeError(
                "SMT library is not installed. cf. https://https://smt.readthedocs.io/en/latest"
            )

        self.options.declare(
            "sampling_method_name",
            types=str,
            default="LHS",
            desc="either LHS, FullFactorial or Ramdom",
        )
        self.options.declare(
            "n_cases", types=int, default=2, desc="number of sample to generate"
        )
        self.options.declare(
            "sampling_method_options",
            types=dict,
            default={},
            desc="options for given SMT sampling method",
        )

        self.options.update(kwargs)
        name = self.options["sampling_method_name"]
        n_cases = self.options["n_cases"]
        opts = self.options["sampling_method_options"]
        self.options["generator"] = SmtDOEGenerator(
            sampling_method_name=name, n_cases=n_cases, **opts
        )

    def _set_name(self):
        self._name = "SMT_DOE_" + self.options["sampling_method_name"]

