"""
Driver for running model on design of experiments cases using OpenTURNS sampling methods
"""
from __future__ import print_function
import numpy as np
from six import iteritems

from openmdao.api import DOEDriver, OptionsDictionary
from openmdao.drivers.doe_generators import DOEGenerator

OPENTURNS_NOT_INSTALLED = False
try:
    import openturns as ot
except ImportError:
    OPENTURNS_NOT_INSTALLED = True


class OpenturnsMonteCarloDOEGenerator(DOEGenerator):
    LIMIT = 1e12

    def __init__(self, n_samples=10, dist=None):
        super(OpenturnsMonteCarloDOEGenerator, self).__init__()

        self.n_samples = n_samples
        self.distribution = dist
        self.called = False

    def __call__(self, uncertain_vars, model=None):
        if self.distribution is None:
            dists = []
            for name, meta in iteritems(uncertain_vars):
                size = meta["size"]
                meta_low = meta["lower"]
                meta_high = meta["upper"]
                for j in range(size):
                    if isinstance(meta_low, np.ndarray):
                        p_low = meta_low[j]
                    else:
                        p_low = meta_low
                    p_low = max(p_low, -self.LIMIT)

                    if isinstance(meta_high, np.ndarray):
                        p_high = meta_high[j]
                    else:
                        p_high = meta_high
                    p_high = min(p_high, self.LIMIT)

                    dists.append(ot.Uniform(p_low, p_high))
            self.distribution = ot.ComposedDistribution(dists)
        else:
            size = 0
            for name, meta in iteritems(uncertain_vars):
                size += meta["size"]
            if (size) != (self.distribution.getDimension()):
                raise RuntimeError(
                    "Bad distribution dimension: should be equal to uncertain variables size {} "
                    ", got {}".format(size, self.distribution.getDimension())
                )
        samples = self.distribution.getSample(self.n_samples)
        self._cases = np.array(samples)
        self.called = True
        sample = []
        for i in range(self._cases.shape[0]):
            j = 0
            for name, meta in iteritems(uncertain_vars):
                size = meta["size"]
                sample.append((name, self._cases[i, j : j + size]))
                j += size
            yield sample

    def get_cases(self):
        if not self.called:
            raise RuntimeError("Have to run the driver before getting cases")
        return self._cases


class OpenturnsDOEDriver(DOEDriver):
    """
    Baseclass for OpenTURNS design-of-experiments Drivers
    """

    def __init__(self, **kwargs):
        super(OpenturnsDOEDriver, self).__init__()

        self.options.declare(
            "distribution",
            types=ot.ComposedDistribution,
            default=None,
            allow_none=True,
            desc="Joint distribution of uncertain variables",
        )
        self.options.declare(
            "n_samples", types=int, default=2, desc="number of sample to generate"
        )
        self.options.update(kwargs)

        self.options["generator"] = OpenturnsMonteCarloDOEGenerator(
            self.options["n_samples"], self.options["distribution"]
        )

    def _set_name(self):
        self._name = "OpenTURNS_DOE_MonteCarlo"

    def get_cases(self):
        return self.options["generator"].get_cases()
