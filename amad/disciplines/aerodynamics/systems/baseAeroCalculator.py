import abc
from cosapp.base import System
from amad.disciplines.aerodynamics.ports import AeroPort


class BaseAeroCalculator(System):
    def setup(self):
        # aero 'port' containing ...
        self.add_output(AeroPort, "output")

        # standardized aero inputs
        # TODO replace with dict
        self.add_inward(
            "mach_current",
            0.0,
            dtype=(int, float, list),
            unit="",
            desc="Mach, current aircraft",
        )
        self.add_inward(
            "alpha_aircraft",
            0.0,
            dtype=(int, float, list),
            unit="deg",
            desc="Angle of attack",
        )
        self.add_inward(
            "beta_aircraft",
            0.0,
            dtype=(int, float, list),
            unit="deg",
            desc="Sideslip angle",
        )
        self.add_inward("rate_roll", 0.0, unit="deg/s")
        self.add_inward("rate_pitch", 0.0, unit="deg/s")
        self.add_inward("rate_yaw", 0.0, unit="deg/s")
        self.add_inward("z_altitude", 0.0, dtype=(int, float, list), unit="m")

        # computed outputs
        self.add_outward("L", 0.0, dtype=(list, str, float, int))
        self.add_outward("D", dtype=(list, str, float, int))
        self.add_outward("Y", dtype=(list, str, float, int))
        self.add_outward("l", dtype=(list, str, float, int))
        self.add_outward("m", dtype=(list, str, float, int))
        self.add_outward("n", dtype=(list, str, float, int))
        self.add_outward("CD", dtype=(list, str, float, int))
        self.add_outward("CL", dtype=(list, str, float, int))
        self.add_outward("CY", dtype=(list, str, float, int))
        self.add_outward("Cl", dtype=(list, str, float, int))
        self.add_outward("Cm", dtype=(list, str, float, int))
        self.add_outward("Cn", dtype=(list, str, float, int))

    @abc.abstractmethod
    def compute_aero(self) -> None:
        pass

    def compute(self):
        self.compute_aero()

        # output all computed parameters to aero port
        self.output.L = self.L
        self.output.D = self.D
        self.output.Y = self.Y
        self.output.l = self.l
        self.output.m = self.m
        self.output.n = self.n
        self.output.CD = self.CD
        self.output.CL = self.CL
        self.output.CY = self.CY
        self.output.Cl = self.Cl
        self.output.Cm = self.Cm
        self.output.Cn = self.Cn
