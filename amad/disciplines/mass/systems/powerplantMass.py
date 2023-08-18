import math
from typing import Dict
from amad.disciplines.mass.systems import (
    AbstractMassComponent,
    BaseMassClass,
    SpecifiedMass,
)
from amad.tools.unit_conversion import lb2kg, n2lb, m2ft


class ModRaymer(AbstractMassComponent):
    """Engine Mass estimation method for modern (>1980) turbofan engines
    Raymer method is used with coefficients re-optimized.
    FLOPS methods are used for engine control and starting masses

    Influencing Parameters:
        r_bypass
        n_eng
        thrust_eng
        mach_mo
        d_nacelle
    """

    def setup(self):
        inward_list = [
            "r_bypass",
            "n_eng",
            "thrust_eng",
            "mach_mo",
            "d_nacelle",
        ]
        super().setup(inward_list)

        # model constants
        self.add_inward("Eng_K_1", 3.6033e1)
        self.add_inward("Eng_K_2", 8.4568e-1)
        self.add_inward("Eng_K_3", 2.2827e-2)

        self.add_outward("m_eng")
        self.add_outward("m_eng_starter")
        self.add_outward("m_eng_ctrl")

    def compute_mass(self):
        # calculate engine mass
        self.m_eng = (
            self.Eng_K_1
            * ((self.thrust_eng / 1000) ** self.Eng_K_2)
            * math.exp(self.Eng_K_3 * self.r_bypass)
        )

        # calculate controls and starters (FLOPS)
        self.m_eng_ctrl = lb2kg(mass=(0.26 * (n2lb(force=self.thrust_eng) ** 0.5)))
        self.m_eng_starter = lb2kg(
            mass=(11.0 * (self.mach_mo**0.32) * (m2ft(length=self.d_nacelle) ** 1.6))
        )

        # calculate total powerplant mass
        self.total_mass = self.n_eng * (
            self.m_eng + self.m_eng_ctrl + self.m_eng_starter
        )


class PowerplantMass(BaseMassClass):
    """Engine mass model. Estimates only the engine part

    Model List:
    ----------------------
    - name [str]: System name
    - model [str]: Computation algorithm. Options are:
        - cairns: Statistical model using thrust and bypass ratio
        - specified: User-specified mass

    Children:
    ---------
    - model:
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        super().setup(model=model, **parameters)

    @classmethod
    def models(cls) -> Dict[str, type]:
        """Dictionary of available models"""
        return {
            "mod-raymer": ModRaymer,
            "specified": SpecifiedMass,
        }
