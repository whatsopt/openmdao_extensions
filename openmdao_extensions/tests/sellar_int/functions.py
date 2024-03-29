"""
  functions.py generated by WhatsOpt 1.25.1
"""
from .functions_base import FunctionsBase
from math import exp


class Functions(FunctionsBase):
    """A class to encapsulate Functions discipline"""

    def compute(self, inputs, outputs):
        """Functions computation"""
        # Here one can implement discipline resolution code
        # (python function or module, external software calls...)

        x = inputs["x"]  # shape: 1, type: Integer
        y1 = inputs["y1"]  # shape: 1, type: Float
        y2 = inputs["y2"]  # shape: 1, type: Float
        z = inputs["z"]  # shape: (2,), type: Float

        outputs["f"] = x**2 + z[1] + y1 + exp(-y2)
        outputs["g1"] = 3.16 - y1
        outputs["g2"] = y2 - 24.0
