from cosapp.base import System
from amad.disciplines.mass.ports import MassPort
import numpy


class WingMassSimpleAC(System):
    def setup(self):
        # weight 'port'
        self.add_output(MassPort, "total")

        # free variables
        self.add_inward("S", desc="wing surface area")
        self.add_inward("V_f_fuse", desc="fuel volume in the fuselage, m^3")
        self.add_inward("W", desc="total aircraft weight, N")
        self.add_inward("AR", desc="aspect ratio")

        # constants
        self.add_inward("W_W_coeff1", 2e-5, desc="wing weight coefficient 1")
        self.add_inward("W_W_coeff2", 60.0, desc="wing weight coefficient 2")
        self.add_inward("tau", 0.12, desc="airfoil thickness to chord ratio")
        self.add_inward("N_ult", 3.3, desc="ultimate load factor")
        self.add_inward("W_0", 6250, desc="aircraft empty weight excluding wing, N")
        self.add_inward("rho_f", 817, desc="density of fuel, kg/m^3")
        self.add_inward("g", 9.81, desc="gravitational acceleration, m/s^2")

        # computed variables
        self.add_outward("W_w_surf")
        self.add_outward("W_w_strc")

    def compute(self):
        # compute variables
        self.W_w_surf = self.W_W_coeff2 * self.S
        self.W_w_strc = (
            self.W_W_coeff1
            / self.tau
            * self.N_ult
            * (self.AR**1.5)
            * numpy.sqrt(
                (self.W_0 + self.V_f_fuse * self.g * self.rho_f) * self.W * self.S
            )
        )

        # output wing mass
        self.total.mass = self.W_w_surf + self.W_w_strc
