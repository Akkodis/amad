import math
from typing import Dict
from amad.disciplines.mass.systems import (
    AbstractMassComponent,
    BaseMassClass,
    SpecifiedMass,
)
from amad.tools.unit_conversion import lb2kg, n2lb, m2ft


class FLOPS(AbstractMassComponent):
    """FLOPS Nacelle Mass estimation method for various aircraft

    Influencing Parameters:
        tech_center_eng
        n_eng
        d_nacelle
        x_nacelle
        thrust_eng
    """

    def setup(self):
        inward_list = [
            "tech_center_eng",
            "n_eng",
            "d_nacelle",
            "x_nacelle",
            "thrust_eng",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("tnac")
        self.add_outward("m_nacelle")

    def compute_mass(self):
        # calculate intermediates
        self.tnac = self.n_eng + 0.5 * (self.n_eng - (2 * math.floor(self.n_eng / 2)))

        # calculate mass
        self.m_nacelle = (
            0.25
            * self.tnac
            * m2ft(length=self.d_nacelle)
            * m2ft(length=self.x_nacelle)
            * (n2lb(self.thrust_eng) ** 0.36)
        )
        self.total_mass = lb2kg(mass=(self.m_nacelle))


class Torenbeek(AbstractMassComponent):
    """Torenbeek Nacelle Mass estimation method for transport aircraft

    Influencing Parameters:
        r_bypass
        thrust_eng
        n_eng
    """

    def setup(self):
        inward_list = [
            "r_bypass",
            "thrust_eng",
            "n_eng",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("k_nac")
        self.add_outward("thrust_total")
        self.add_outward("m_nacelle")

    def compute_mass(self):
        # calculate intermediates
        self.k_nac = 0.055 if self.r_bypass <= 2.5 else 0.065
        self.thrust_total = n2lb(force=(self.thrust_eng * self.n_eng))

        # calculate mass
        self.m_nacelle = self.k_nac * self.thrust_total
        self.total_mass = lb2kg(mass=(self.m_nacelle))


class NacelleMass(BaseMassClass):
    """Nacelle Mass model

    Constructor arguments:
    ----------------------
    - name [str]: System name
    - model [str]: Computation algorithm. Options are:
        - torenbeek: Egbeert Torenbeek
        - flops: NASA FLOPS
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
            "torenbeek": Torenbeek,
            "flops": FLOPS,
            "specified": SpecifiedMass,
        }
