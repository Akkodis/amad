from typing import Dict
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass
from amad.tools.unit_conversion import lb2kg, sqm2sqft, m2ft, ms2kt


class FLOPS(AbstractMassComponent):
    """FLOPS Fuselage Mass estimation method for various aircraft

    Influencing Parameters:
        x_fuse
        w_fuse
        h_fuse
        n_eng_fuse
        tech_cargo_floor
        n_fuse
    """

    def setup(self):
        inward_list = [
            "x_fuse",
            "w_fuse",
            "h_fuse",
            "n_eng_fuse",
            "tech_cargo_floor",
            "n_fuse",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("coeff_cargo")
        self.add_outward("dav")
        self.add_outward("m_fuselage")

    def compute_mass(self):
        # calculate intermediates
        self.coeff_cargo = 1.0 if self.tech_cargo_floor == "True" else 0.0
        self.dav = (m2ft(length=self.h_fuse) + m2ft(length=self.w_fuse)) / 2

        # calculate fuselage mass
        self.m_fuselage = (
            1.35
            * ((m2ft(length=self.x_fuse) * self.dav) ** 1.28)
            * (1 + (0.05 * self.n_eng_fuse))
            * (1 + (0.38 * self.coeff_cargo))
            * self.n_fuse
        )
        self.total_mass = lb2kg(mass=(self.m_fuselage))


class Torenbeek(AbstractMassComponent):
    """Torenbeek Fuselage Mass estimation method for transport aircraft

    Influencing Parameters:
        a_fuselage
        x_wing_tail_chord
        w_fuse
        h_fuse
        tech_pressurized_fuse
        tech_attached_gear
        tech_cargo_floor
    """

    def setup(self):
        inward_list = [
            "a_fuselage",
            "x_fuse",
            "x_wing_tail_chord",
            "w_fuse",
            "h_fuse",
            "tech_pressurized_fuse",
            "tech_attached_gear",
            "tech_cargo_floor",
            "v_dive",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("coeff_K_f")
        self.add_outward("m_fuselage")

    def compute_mass(self):
        # unit conversions
        self.a_fuselage = sqm2sqft(self.a_fuselage)
        x_wing_tail_chord = m2ft((self.x_fuse / 2) - 1.005)
        self.w_fuse = m2ft(self.w_fuse)
        self.h_fuse = m2ft(self.h_fuse)

        # calculate intermediates
        self.coeff_K_f = (
            (1.08 if self.tech_pressurized_fuse == "True" else 1.0)
            * (1.07 if self.tech_attached_gear == "True" else 1.0)
            * (1.10 if self.tech_cargo_floor == "True" else 1.0)
        )

        # calculate fuselage mass
        self.m_fuselage = (
            0.021
            * self.coeff_K_f
            * (
                (ms2kt(self.v_dive) * x_wing_tail_chord / (self.w_fuse + self.h_fuse))
                ** 0.5
            )
            * (self.a_fuselage**1.2)
        )
        self.total_mass = lb2kg(mass=(self.m_fuselage))


class FuselageMass(BaseMassClass):
    """Fuselage Mass model

    Constructor arguments:
    ----------------------
    - name [str]: System name
    - model [str]: Computation algorithm. Options are:
        - torenbeek: Egbeert Torenbeek

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
