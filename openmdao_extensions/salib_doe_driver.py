"""
Driver for running model on design of experiments cases using Salib sampling methods
"""
from __future__ import print_function
from six import itervalues, iteritems, reraise
from six.moves import range

import numpy as np

from openmdao.api import DOEDriver, ListGenerator
from openmdao.core.driver import Driver, RecordingDebugging
from openmdao.drivers.doe_generators import DOEGenerator
from openmdao.utils.general_utils import warn_deprecation

SALIB_NOT_INSTALLED = False
try:
    from SALib.sample import morris as ms
except ImportError:
    SALIB_NOT_INSTALLED = True

class SalibMorrisDOEGenerator(DOEGenerator):

    def __init__(self, n_trajs=100, n_levels=4, grid_step_size=2):
        super(SalibMorrisDOEGenerator, self).__init__()

        if SALIB_NOT_INSTALLED:
            raise RuntimeError('SALib library is not installed. \
                                cf. https://salib.readthedocs.io/en/latest/getting-started.html')

        # number of trajectories to apply morris method
        self.n_trajs = n_trajs
        # number of grid levels
        self.n_levels = n_levels
        # grid jump size
        self.grid_step_size = grid_step_size        

    def __call__(self, design_vars, model=None):
        bounds=[]
        names=[]
        for name, meta in iteritems(design_vars):
            size = meta['size']
            meta_low = meta['lower']
            meta_high = meta['upper']
            for j in range(size):
                if isinstance(meta_low, np.ndarray):
                    p_low = meta_low[j]
                else:
                    p_low = meta_low

                if isinstance(meta_high, np.ndarray):
                    p_high = meta_high[j]
                else:
                    p_high = meta_high
                    
                display_name = name.split('.')[-1]
                if size>1:
                    display_name += str(j)
                names.append(display_name)
                bounds.append((p_low, p_high))

        self._pb = {'num_vars': len(names), 
                    'names': names, 
                    'bounds': bounds, 'groups': None}
        cases = ms.sample(self._pb, self.n_trajs, self.n_levels, self.grid_step_size)
        sample = []
        for i in range(cases.shape[0]):
            j=0
            for name, meta in iteritems(design_vars):
                size = meta['size']
                sample.append((name, cases[i, j:j + size]))
                j += size
            yield sample

class SalibMorrisDOEDriver(DOEDriver):
    """
    Baseclass for SALib design-of-experiments Drivers
    """

    def __init__(self, **kwargs):
        super(SalibMorrisDOEDriver, self).__init__()

        if SALIB_NOT_INSTALLED:
            raise RuntimeError('SALib library is not installed. \
                                cf. https://salib.readthedocs.io/en/latest/getting-started.html')

        self.options.declare('n_trajs', types=int, default=100,
                             desc='number of trajectories to apply morris method')
        self.options.declare('n_levels', types=int, default=4,
                             desc='number of grid levels')
        self.options.declare('grid_step_size', types=int , default=2,
                             desc='grid jump size')
        self.options.update(kwargs)
        n_trajs = self.options['n_trajs']
        n_levels = self.options['n_levels']
        grid_step_size = self.options['grid_step_size']
        self.options['generator'] = SalibMorrisDOEGenerator(n_trajs, n_levels, grid_step_size)

class SalibDoeDriver(SalibMorrisDOEDriver):
    """
    Deprecated. Use SalibMorrisDOEDriver.
    """
    def __init__(self, **kwargs):
        super(SalibDoeDriver, self).__init__()
        warn_deprecation("'SalibDoeDriver' is deprecated"
                         "; use 'SalibMorrisDOEDriver' instead.")

