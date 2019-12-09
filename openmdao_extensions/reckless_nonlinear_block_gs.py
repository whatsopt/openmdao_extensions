"""Define the NonlinearBlockGS class."""

import os
import numpy as np

from openmdao.core.analysis_error import AnalysisError
from openmdao.recorders.recording_iteration_stack import Recording
from openmdao.api import NonlinearBlockGS


class RecklessNonlinearBlockGS(NonlinearBlockGS):
    """
    Extends Nonlinear block Gauss-Seidel solver with convergence variables options.
    Those options allows to focus on a subset of variables to drive the convergence.
    It allows to get quickest convergence by ignoring 'noise' coming highly non linear
    variables. Obviously the user has to know what he/she is doing because
    in that case some of the variables may not be converged properly
    (hence the 'reckless' prefix in the name).

    Attributes
    ----------
    _convrg_vars: list of string
        List of absolute variable names used to compute relative error and control
        solver convergence.
    _convrg_rtols: list of float
        List of relative error tolerance values for each variables of _convrg_vars. If not set, rtol
        value is used for all specified variables. Only used if _convrg_vars is set.
    """

    SOLVER = "NL: RNLBGS"

    def __init__(self, **kwargs):
        """
        Initialize all attributes.

        Parameters
        ----------
        **kwargs : dict
            options dictionary.
        """
        super(RecklessNonlinearBlockGS, self).__init__(**kwargs)

        self._convrg_vars = None
        self._convrg_rtols = None

    def _declare_options(self):
        """
        Declare options before kwargs are processed in the init method.
        """
        super(RecklessNonlinearBlockGS, self)._declare_options()
        self.options.declare(
            "convrg_vars",
            types=list,
            default=[],
            desc="list of variables (names) used by relative error criterium.",
        )
        self.options.declare(
            "convrg_rtols",
            types=list,
            default=[],
            desc="list of relative error tolerances corresponding to each"
            " variable specified in convrg_vars option (rtol is used otherwise)",
        )

    def _solve(self):
        """
        Run the iterative solver.

        Overrides opendmao/solvers/solver.py to implement _is_rtol_converged
        """
        maxiter = self.options["maxiter"]
        atol = self.options["atol"]
        iprint = self.options["iprint"]

        self._mpi_print_header()

        self._iter_count = 0
        norm0, norm = self._iter_initialize()

        self._norm0 = norm0

        self._mpi_print(self._iter_count, norm, norm / norm0)

        is_rtol_converged = self._is_rtol_converged(norm, norm0)
        while self._iter_count < maxiter and norm > atol and not is_rtol_converged:
            with Recording(type(self).__name__, self._iter_count, self) as rec:
                self._single_iteration()
                self._iter_count += 1
                self._run_apply()
                norm = self._iter_get_norm()
                # With solvers, we want to record the norm AFTER the call, but the call needs to
                # be wrapped in the with for stack purposes, so we locally assign  norm & norm0
                # into the class.
                rec.abs = norm
                rec.rel = norm / norm0

            if norm0 == 0:
                norm0 = 1
            self._mpi_print(self._iter_count, norm, norm / norm0)
            is_rtol_converged = self._is_rtol_converged(norm, norm0)

        if self._system.comm.rank == 0 or os.environ.get("USE_PROC_FILES"):
            prefix = self._solver_info.prefix + self.SOLVER
            is_rtol_converged = self._is_rtol_converged(norm, norm0)
            if (
                np.isinf(norm)
                or np.isnan(norm)
                or (norm > atol and not is_rtol_converged)
            ):
                if iprint > -1:
                    msg = " Failed to Converge in {} iterations".format(
                        self._iter_count
                    )
                    print(prefix + msg)

                # Raise AnalysisError if requested.
                if self.options["err_on_maxiter"]:
                    msg = "Solver '{}' on system '{}' failed to converge."
                    raise AnalysisError(msg.format(self.SOLVER, self._system.pathname))

            elif iprint == 1:
                print(prefix + " Converged in {} iterations".format(self._iter_count))
            elif iprint == 2:
                print(prefix + " Converged")

    def _iter_initialize(self):
        """
        Perform any necessary pre-processing operations.

        Returns
        -------
        float
            initial error.
        float
            error at the first iteration.
        """
        self._convrg_vars = self.options["convrg_vars"]
        if self._convrg_vars and not self.options["convrg_rtols"]:
            rtol = self.options["rtol"]
            self._convrg_rtols = rtol * np.ones(len(self._convrg_vars))
        else:
            self._convrg_rtols = self.options["convrg_rtols"]
            if len(self._convrg_rtols) != len(self._convrg_vars):
                raise RuntimeError(
                    "Convergence rtols bad size : should be {}, "
                    "found {}.".format(len(self._convrg_vars), len(self._convrg_rtols))
                )

        return super(RecklessNonlinearBlockGS, self)._iter_initialize()

    def _is_rtol_converged(self, norm, norm0):
        """
        Check convergence regarding relative error tolerance.

        Parameters
        ----------
        norm : float
            error (residuals norm)
        norm0 : float
            initial error

        Returns
        -------
        bool
            whether convergence is reached regarding relative error tolerance
        """
        if self._convrg_vars:
            nbvars = len(self._convrg_vars)
            rerrs = np.ones(nbvars)
            outputs = np.ones(nbvars)
            for i, name in enumerate(self._convrg_vars):
                outputs[i] = self._system._outputs._views[name]
                residual = self._system._residuals._views[name]
                rerrs[i] = np.linalg.norm(residual) / np.linalg.norm(outputs[i])
            is_rtol_converged = (rerrs < self._convrg_rtols).all()
        else:
            is_rtol_converged = norm / norm0 < self.options["rtol"]
        return is_rtol_converged

    def _iter_get_norm(self):
        """
        Return the norm of the residual regarding convergence variable settings.

        Returns
        -------
        float
            norm.
        """
        if self._convrg_vars:
            total = []
            for name in self._convrg_vars:
                total.append(self._system._residuals._views_flat[name])
            norm = np.linalg.norm(np.concatenate(total))
        else:
            norm = super(RecklessNonlinearBlockGS, self)._iter_get_norm()
        return norm
