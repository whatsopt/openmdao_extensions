import numpy as np
import traceback

from openmdao.core.driver import Driver, RecordingDebugging
from openmdao.core.analysis_error import AnalysisError

ONERASEGO_NOT_INSTALLED = False
try:
    from segomoe.sego_defs import get_sego_options, ExitStatus
    from segomoe.constraint import Constraint
    from segomoe.sego import Sego
except ImportError:
    ONERASEGO_NOT_INSTALLED = True


def to_list(lst, size):
    if not (isinstance(lst, np.ndarray) or isinstance(lst, list)):
        return [lst] * size
    diff_len = len(lst) - size
    if diff_len > 0:
        return lst[0:size]
    elif diff_len < 0:
        return [lst[0]] * size
    else:
        return lst


class OneraSegoDriver(Driver):
    """
    OpenMDAO driver for ONERA SEGOMOE optimizer
    """

    def __init__(self, **kwargs):
        """
        Initialize the driver with the following option.
        """
        super(OneraSegoDriver, self).__init__(**kwargs)

        if ONERASEGO_NOT_INSTALLED:
            raise RuntimeError("Onera SEGOMOE library is not installed.")

        # What we support
        self.supports["optimization"] = True
        self.supports["inequality_constraints"] = True
        self.supports["equality_constraints"] = True
        self.supports["two_sided_constraints"] = True
        self.supports["linear_constraints"] = True

        # What we don't support
        self.supports["multiple_objectives"] = False
        self.supports["active_set"] = False
        self.supports["integer_design_vars"] = False
        self.supports["simultaneous_derivatives"] = False
        self.supports["total_jac_sparsity"] = False
        self.supports["gradients"] = False
        self.supports._read_only = True

        self.opt_settings = {}

    def _declare_options(self):
        self.options.declare(
            "optimizer",
            default="SEGOMOE",
            values=["SEGOMOE"],
            desc="Name of optimizers to use",
        )

    def _setup_driver(self, problem):
        super(OneraSegoDriver, self)._setup_driver(problem)

        self.comm = None

    def run(self, path_hs="", eq_tol={}, ieq_tol={}):
        """
        Optimize the problem using SEGOMOE.

        Parameters
        ----------
        problem : Problem object
            An optimization problem of OpenMDAO framework
        path_hs: string, optional
            path to a directory storing hot_start data
        eq_tol: dict
            Dictionary to define specific tolerance for eq constraints
            {'[groupName]': [tol]} Default tol = 1e-5
        ieq_tol: dict
            Dictionary to define specific tolerance for ieq constraints
            {'[groupName]': [tol]} Default tol = 1e-5
        """
        model = self._problem().model

        path_hs = ""
        self.eq_tol = eq_tol
        self.ieq_tol = ieq_tol
        self.iter_count = 0
        self.name = f"onera_optimizer_{self.options['optimizer'].lower()}"
        self._sego_vars = []
        self._sego_cons = []
        self._map_con = {}
        self._n_mapped_con = 0

        # Initial Run
        with RecordingDebugging(
            self.options["optimizer"], self.iter_count, self
        ) as rec:
            # Initial Run
            model.run_solve_nonlinear()
            rec.abs = 0.0
            rec.rel = 0.0
        self.iter_count += 1

        # Format design variables to suit segomoe implementation
        self._initialize_vars()

        # Format constraints to suit segomoe implementation
        self._initialize_cons()

        # Format option dictionary to suit SEGO implementation
        optim_settings = {}
        for opt, opt_dict in get_sego_options().items():
            optim_settings[opt] = opt_dict["default"]
        n_iter = self.opt_settings["maxiter"]
        optim_settings.update(
            {k: v for k, v in self.opt_settings.items() if k != "maxiter"}
        )

        # In OpenMDAO context, obj and constraints are always evaluated together
        optim_settings["grouped_eval"] = True

        # default model
        mod_obj = {"corr": "squar_exp", "regr": "constant", "normalize": True}

        dim = 0
        for name, meta in self._designvars.items():
            dim += meta["size"]
        print("Designvars dimension: ", dim)
        if dim > 10:
            n_components = 3
            mod_obj["n_components"] = n_components
            mod_obj["name"] = "KPLS" if dim > 20 else "KPLSK"
        else:
            n_components = dim
            mod_obj["name"] = "KRG"
        mod_obj["theta0"] = [1.0] * n_components
        mod_obj["thetaL"] = [0.1] * n_components
        mod_obj["thetaU"] = [10.0] * n_components

        optim_settings["model_type"] = {"obj": mod_obj, "con": mod_obj}

        print(optim_settings)
        # Instanciate a SEGO optimizer
        sego = Sego(
            self._objfunc,
            self._sego_vars,
            const=self._sego_cons,
            optim_settings=optim_settings,
            path_hs=path_hs,
            comm=self.comm,
        )

        # Run the optim
        # exit_flag, x_best, obj_best, dt_opt = sego.run_optim(
        exit_flag, x_best, _, _ = sego.run_optim(n_iter=n_iter)

        # Set optimal parameters
        i = 0
        for name, meta in self._designvars.items():
            size = meta["size"]
            self.set_design_var(name, x_best[0][i : i + size])
            i += size

        with RecordingDebugging(
            self.options["optimizer"], self.iter_count, self
        ) as rec:
            model.run_solve_nonlinear()
            rec.abs = 0.0
            rec.rel = 0.0
        self.iter_count += 1

        self.exit_flag = (exit_flag == ExitStatus.valid_sol) or (
            exit_flag == ExitStatus.solution_reached
        )

        return self.exit_flag

    def _initialize_vars(self):
        variables = []
        param_meta = self._designvars
        for name, meta in param_meta.items():
            if meta["size"] > 1:
                if np.isscalar(meta["lower"]):
                    variables += [
                        {
                            "name": name + "_" + str(i),
                            "lb": meta["lower"],
                            "ub": meta["upper"],
                        }
                        for i in range(meta["size"])
                    ]
                else:
                    variables += [
                        {
                            "name": name + "_" + str(i),
                            "lb": meta["lower"][i],
                            "ub": meta["lower"][i],
                        }
                        for i in range(meta["size"])
                    ]
            else:
                variables += [{"name": name, "lb": meta["lower"], "ub": meta["upper"]}]
        self._sego_vars = variables

    def _initialize_cons(self, eq_tol=None, ieq_tol=None):
        """
        Format OpenMDAO constraints to suit SEGOMOE implementation

        Parameters
        ----------
        eq_tol: dict
            Dictionary to define specific tolerance for eq constraints
            {'[groupName]': [tol]} Default tol = 1e-5
        ieq_tol: dict
            Dictionary to define specific tolerance for ieq constraints
            {'[groupName]': [tol]} Default tol = 1e-5
        """

        # for short
        add_con = self._sego_cons.append

        # Start at 1 -> obj first
        eval_index = 1

        con_meta = self._cons
        eq_cons = {name: con for name, con in con_meta.items() if con["equals"]}
        ieq_cons = {name: con for name, con in con_meta.items() if not con["equals"]}

        # Equality constraints
        for name in eq_cons.keys():
            meta = con_meta[name]
            size = meta["size"]
            equals = to_list(meta["equals"], size)
            tol = to_list(eq_tol[name] if name in self.eq_tol else 1e-4, size)

            for k in range(size):
                add_con(
                    Constraint("=", equals[k], name=(name + "_" + str(k)), tol=tol[k])
                )
            # Map eq constraints - range to allow double-sided constraint support
            self._map_con[name] = range(eval_index, eval_index + size)
            eval_index += size
            self._n_mapped_con += size

        # Inequality constraints
        for name in ieq_cons.keys():
            meta = con_meta[name]
            size = meta["size"]
            # Bounds - double sided is supported
            lower = to_list(meta["lower"], size)
            upper = to_list(meta["upper"], size)
            tol = to_list(ieq_tol[name] if name in self.ieq_tol else 1e-4, size)
            # Index list is updated for each real constraint to handle double sided constraints
            index_list = []

            for k in range(size):
                if lower[k] is None or lower[k] < -1e29:
                    # g(x) < upper
                    add_con(
                        Constraint(
                            "<", upper[k], name=(name + "_" + str(k)), tol=tol[k]
                        )
                    )
                    index_list.append(eval_index)
                    eval_index += 1
                    self._n_mapped_con += 1
                elif upper[k] is None or upper[k] > 1e29:
                    # g(x) > lower
                    add_con(
                        Constraint(
                            ">", lower[k], name=(name + "_" + str(k)), tol=tol[k]
                        )
                    )
                    index_list.append(eval_index)
                    eval_index += 1
                    self._n_mapped_con += 1
                else:
                    # lower < g(x) < upper
                    # Split is currently required for sego
                    add_con(
                        Constraint(
                            "<", upper[k], name=(name + "_" + str(k) + "<"), tol=tol[k]
                        )
                    )
                    add_con(
                        Constraint(
                            ">", lower[k], name=(name + "_" + str(k) + ">"), tol=tol[k]
                        )
                    )
                    index_list.append([eval_index, eval_index + 1])
                    eval_index += 2
                    self._n_mapped_con += 2
            self._map_con[name] = index_list

    def _objfunc(self, point):
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
        fail = False
        res = np.zeros(1 + self._n_mapped_con)
        model = self._problem().model

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
                    model._solve_nonlinear()

                # Let the optimizer try to handle the error
                except AnalysisError:
                    model._clear_iprint()
                    fail = True

            # Get the objective function evaluation - single obj support
            for name, obj in self.get_objective_values().items():
                res[0] = obj

            # Get the constraint evaluations:
            for name, con_res in self.get_constraint_values().items():
                # Make sure con_res is array_like
                con_res = to_list(con_res, len(self._map_con[name]))
                # Perform mapping
                for i, con_index in enumerate(self._map_con[name]):
                    if isinstance(con_index, list):
                        # Double sided inequality constraint -> duplicate response
                        for k in con_index:
                            res[k] = con_res[i]
                    else:
                        res[con_index] = con_res[i]

        except Exception as msg:
            tb = traceback.format_exc()

            # Exceptions seem to be swallowed by the C code, so this
            # should give the user more info than the dreaded "segfault"
            print("Exception: %s" % str(msg))
            print(70 * "=", tb, 70 * "=")
            fail = True

        return res, fail
