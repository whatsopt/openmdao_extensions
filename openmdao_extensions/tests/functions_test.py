import numpy as np
from math import cos, sin, pi
from openmdao.api import (
    IndepVarComp,
    Group,
    ExplicitComponent,
)


class Branin(ExplicitComponent):
    def setup(self):
        self.add_input("x1", val=1.0)
        self.add_input("x2", val=1.0)
        self.add_output("obj", val=1.0)
        self.add_output("con", val=1.0)

    @staticmethod
    def compute(inputs, outputs):
        x_1 = inputs["x1"][0]
        x_2 = inputs["x2"][0]
        # obj
        part1 = (x_2 - (5.1 * x_1 ** 2) / (4.0 * pi ** 2) + 5.0 * x_1 / pi - 6.0) ** 2
        part2 = 10.0 * ((1.0 - 1.0 / (8.0 * pi)) * cos(x_1) + 1.0)
        part3 = (5.0 * x_1 + 25.0) / 15.0
        outputs["obj"] = part1 + part2 + part3

        # con
        x_g1 = (x_1 - 2.5) / 7.5
        x_g2 = (x_2 - 7.5) / 7.5
        part1 = (4.0 - 2.1 * x_g1 ** 2 + (x_g1 ** 4) / 3.0) * x_g1 ** 2
        part2 = x_g1 * x_g2
        part3 = (4.0 * x_g2 ** 2 - 4.0) * x_g2 ** 2
        part4 = 3.0 * sin(6.0 * (1.0 - x_g1))
        part5 = 3.0 * sin(6.0 * (1.0 - x_g2))
        outputs["con"] = -(part1 + part2 + part3 + part4 + part5 - 6.0)


class BraninMDA(Group):
    def setup(self):
        indeps = self.add_subsystem("indeps", IndepVarComp(), promotes=["*"])
        indeps.add_output("x1", 9.1)
        indeps.add_output("x2", 4.75)

        self.add_subsystem("Branin", Branin(), promotes=["*"])


class Ackley(ExplicitComponent):
    def setup(self):
        self.add_input("x", val=[1.0, 1.0])
        self.add_output("obj", val=1.0)

    @staticmethod
    def compute(inputs, outputs):
        dim = 2
        a = 20.0
        b = 0.2
        c = 2 * np.pi
        point = inputs["x"]
        outputs["obj"] = (
            -a * np.exp(-b * np.sqrt(1.0 / dim * np.sum(point ** 2)))
            - np.exp(1.0 / dim * np.sum(np.cos(c * point)))
            + a
            + np.exp(1)
        )


class AckleyMDA(Group):
    def setup(self):
        indeps = self.add_subsystem("indeps", IndepVarComp(), promotes=["*"])
        indeps.add_output("x", [1.0, 1.0])

        self.add_subsystem("Ackley", Ackley(), promotes=["*"])
