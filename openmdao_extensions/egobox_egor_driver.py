import numpy as np
import traceback

from openmdao.core.driver import Driver, RecordingDebugging
from openmdao.core.analysis_error import AnalysisError

EGOBOX_NOT_INSTALLED = False
try:
    import egobox as egx
    from egobox import Egor
except ImportError:
    EGOBOX_NOT_INSTALLED = True


def to_list(l, size):
    if not (isinstance(l, np.ndarray) or isinstance(l, list)):
        return [l] * size
    diff_len = len(l) - size
    if diff_len > 0:
        return l[0:size]
    elif diff_len < 0:
        return [l[0]] * size
    else:
        return l


class EgoboxEgorDriver(Driver):
    """OpenMDAO driver for egobox optimizer"""

    def __init__(self, **kwargs):
        """Initialize the driver with the given options."""
        super(EgoboxEgorDriver, self).__init__(**kwargs)

        if EGOBOX_NOT_INSTALLED:
            raise RuntimeError("egobox library is not installed.")

        # What we support
        self.supports["inequality_constraints"] = True
        self.supports["linear_constraints"] = True
        self.supports["integer_design_vars"] = True

        # What we don't support
        self.supports["equality_constraints"] = False
        self.supports["two_sided_constraints"] = False
        self.supports["multiple_objectives"] = False
        self.supports["active_set"] = False
        self.supports["simultaneous_derivatives"] = False
        self.supports["total_jac_sparsity"] = False
        self.supports["gradients"] = False

        self.opt_settings = {}

    def _declare_options(self):
        self.options.declare(
            "optimizer",
            default="EGOR",
            values=["EGOR"],
            desc="Name of optimizer to use",
        )

    def _setup_driver(self, problem):
        super(EgoboxEgorDriver, self)._setup_driver(problem)

        self.comm = None

    def run(self):
        model = self._problem().model

        self.iter_count = 0
        self.name = f"onera_optimizer_{self.options['optimizer'].lower()}"

        # Initial Run
        with RecordingDebugging(self.name, self.iter_count, self) as rec:
            # Initial Run
            model._solve_nonlinear()
            rec.abs = 0.0
            rec.rel = 0.0
        self.iter_count += 1

        # Format design variables to suit segomoe implementation
        self.xspecs = self._initialize_vars(model)

        # Format constraints to suit segomoe implementation
        self.n_cstr = self._initialize_cons()

        # Format option dictionary to suit Egor implementation
        optim_settings = {
            "cstr_tol": 1e-6,
        }
        n_iter = self.opt_settings["maxiter"]
        optim_settings.update(
            {k: v for k, v in self.opt_settings.items() if k != "maxiter"}
        )

        dim = 0
        for name, meta in self._designvars.items():
            dim += meta["size"]
        if dim > 10:
            self.optim_settings["kpls_dim"] = 3

        # Instanciate a SEGO optimizer
        egor = Egor(
            self._objfunc,
            xspecs=self.xspecs,
            n_cstr=self.n_cstr,
            **optim_settings,
        )

        # Run the optim
        res = egor.minimize(n_iter=n_iter)

        # Set optimal parameters
        i = 0
        for name, meta in self._designvars.items():
            size = meta["size"]
            self.set_design_var(name, res.x_opt[i : i + size])
            i += size

        with RecordingDebugging(self.name, self.iter_count, self) as rec:
            model._solve_nonlinear()
            rec.abs = 0.0
            rec.rel = 0.0
        self.iter_count += 1

        return True

    def _initialize_vars(self, model):
        dvs_int = {}
        for name, meta in self._designvars.items():
            infos = model.get_io_metadata(includes=name)
            for absname in infos:
                if name == infos[absname]["prom_name"] and (
                    infos[absname]["tags"] & {"wop:int"}
                ):
                    dvs_int[name] = egx.XType(egx.XType.INT)

        variables = []
        desvars = self._designvars
        for name, meta in desvars.items():
            vartype = dvs_int.get(name, egx.XType(egx.XType.FLOAT))
            if meta["size"] > 1:
                if np.isscalar(meta["lower"]):
                    variables += [
                        egx.XSpec(vartype, [meta["lower"], meta["upper"]])
                        for i in range(meta["size"])
                    ]
                else:
                    variables += [
                        egx.XSpec(vartype, [meta["lower"], meta["upper"]])
                        for i in range(meta["size"])
                    ]
            else:
                variables += [egx.XSpec(vartype, [meta["lower"], meta["upper"]])]
        return variables

    def _initialize_cons(self, eq_tol=None, ieq_tol=None):
        """Format OpenMDAO constraints to suit EGOR implementation

        Parameters
        ----------
        eq_tol: dict
            Dictionary to define specific tolerance for eq constraints
            {'[groupName]': [tol]} Default tol = 1e-5
        """
        con_meta = self._cons

        self.ieq_cons = {
            name: con for name, con in con_meta.items() if not con["equals"]
        }

        # Inequality constraints
        n_cstr = 0
        for name in self.ieq_cons.keys():
            meta = con_meta[name]
            size = meta["size"]
            # Bounds - double sided is supported
            lower = to_list(meta["lower"], size)
            upper = to_list(meta["upper"], size)
            for k in range(size):
                if (lower[k] is None or lower[k] < -1e29) and upper[k] == 0.0:
                    n_cstr += 1
                else:
                    raise ValueError(
                        f"Constraint {lower[k]} < g(x) < {upper[k]} not handled by Egor driver"
                    )
        return n_cstr

    def _objfunc(self, points):
        """
        Function that evaluates and returns the objective function and the
        constraints. This function is called by SEGOMOE

        Parameters
        ----------
        point : numpy.ndarray
            point to evaluate

        Returns
        -------
        func_dict : dict
            Dictionary of all functional variables evaluated at design point.
        fail : int
            0 for successful function evaluation
            1 for unsuccessful function evaluation
        """
        res = np.zeros((points.shape[0], 1 + self.n_cstr))
        model = self._problem().model

        for k, point in enumerate(points):
            try:
                # Pass in new parameters
                i = 0

                for name, meta in self._designvars.items():
                    size = meta["size"]
                    self.set_design_var(name, point[i : i + size])
                    i += size

                # Execute the model
                with RecordingDebugging(
                    self.options["optimizer"], self.iter_count, self
                ) as _:
                    self.iter_count += 1
                    try:
                        model.run_solve_nonlinear()

                    # Let the optimizer try to handle the error
                    except AnalysisError:
                        model._clear_iprint()

                # Get the objective function evaluation - single obj support
                for obj in self.get_objective_values().values():
                    res[k, 0] = obj

                # Get the constraint evaluations
                j = 1
                for con_res in self.get_constraint_values().values():
                    # Make sure con_res is array_like
                    con_res = to_list(con_res, 1)
                    # Perform mapping
                    for i, _ in enumerate(con_res):
                        res[k, j + i] = con_res[i]
                    j += 1

            except Exception as msg:
                tb = traceback.format_exc()
                print("Exception: %s" % str(msg))
                print(70 * "=", tb, 70 * "=")

        return res
