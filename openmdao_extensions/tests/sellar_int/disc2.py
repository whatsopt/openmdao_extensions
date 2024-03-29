"""
  disc2.py generated by WhatsOpt 1.25.1
"""
from .disc2_base import Disc2Base


class Disc2(Disc2Base):
    """A class to encapsulate Disc2 discipline"""

    def compute(self, inputs, outputs):
        """Disc2 computation"""
        # Here one can implement discipline resolution code
        # (python function or module, external software calls...)

        y1 = inputs["y1"]  # shape: 1, type: Float
        z = inputs["z"]  # shape: (2,), type: Float

        if y1.real < 0.0:
            y1 *= -1

        outputs["y2"] = y1**0.5 + z[0] + z[1]
