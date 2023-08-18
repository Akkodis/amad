from cosapp.base import System
from amad.disciplines.transverse.ports import VolumePort


class FuelVolume_Weight(System):
    def setup(self):
        # volume 'ports'
        self.add_output(VolumePort, "available")

        # free variables
        self.add_inward("S", unit="m**2", desc="wing surface area")
        self.add_inward("AR", unit="", desc="aspect ratio")
        self.add_inward(
            "V_fuselage",
            unit="m**3",
            desc="Fuselage volume in the  generated aircraft by AeroSandbox",
        )
        self.add_inward(
            "V_f_fuse_ratio",
            0.05,
            unit="",
            desc="Estimated ratio between total fuselage volume and the central fuel tank",
        )

        # constants
        self.add_inward("tau", 0.12, desc="airfoil thickness to chord ratio")
        self.add_inward("rho_f", 817, unit="kg/m**3", desc="density of fuel")

        # computed variables
        self.add_outward("V_f_fuse", unit="m**3", desc="fuel volume in the fuselage")
        self.add_outward("V_f_wing", unit="m**3", desc="fuel volume in the wing")
        self.add_outward(
            "W_f",
            unit="m**3",
            desc="Max fuel weight in AC according to the volume in the AC",
        )

    def compute(self):
        # compute variables
        self.V_f_wing = (
            0.03 * self.S**1.5 / self.AR**0.5 * self.tau
        )  # linear with b and tau, quadratic with chord
        self.V_f_fuse = self.V_fuselage * self.V_f_fuse_ratio

        # output volume
        self.available.volume = self.V_f_wing + self.V_f_fuse

        # output maximum fuel mass
        self.W_f = self.available.volume * self.rho_f
