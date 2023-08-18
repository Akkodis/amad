from typing import Dict
import math
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass
from amad.tools.unit_conversion import kg2lb, lb2kg, n2lb, sqm2sqft
from amad.disciplines.design.tools.liftingArea import lifting_area


class Combined(AbstractMassComponent):
    """
    Completion mass estimation of the paint, flight crew and unusable fuel mass.
    """

    def setup(self):
        inward_list = [
            "x_wing_span",
            "r_wing_taper",
            "chord_wing_root",
            "x_htail_span",
            "r_htail_taper",
            "chord_htail_root",
            "x_vtail_span",
            "r_vtail_taper",
            "chord_vtail_root",
            "h_fuse",
            "w_fuse",
            "x_fuse",
            "n_flcr",
            "n_flatt",
            "n_eng",
            "thrust_eng",
            "n_fuel_tanks",
            "m_fuel",
        ]
        super().setup(inward_list)

        # computed variables
        # TODO: Create a surface area system (design?) to calculate this
        self.add_outward("a_surface_aircraft")
        self.add_outward("m_paint")
        self.add_outward("m_flight_crew")
        self.add_outward("m_unusable_fuel")

    def compute_mass(self):
        # compute wing area
        a_wing = lifting_area(self.x_wing_span, self.r_wing_taper, self.chord_wing_root)

        # tail areas
        a_htail = lifting_area(
            self.x_htail_span, self.r_htail_taper, self.chord_htail_root
        )
        a_vtail = lifting_area(
            self.x_vtail_span, self.r_vtail_taper, self.chord_vtail_root
        )

        # AC surface area
        self.a_surface_aircraft = (
            (
                math.pi * ((self.h_fuse + self.w_fuse) / 2) * self.x_fuse
            )  # fuselage surface area
            + (2 * a_wing)  # wing area
            + (2 * a_htail)  # horizontal tail area
            + (2 * a_vtail)  # vertical tail area
        )

        # Crew weights
        self.m_flight_crew = (self.n_flcr * 95.255) + (  # 190lb pilot + 20lb flight bag
            self.n_flatt * 86.183
        )  # 180lb FA + 10lb kit

        # Paint weight
        self.m_paint = self.a_surface_aircraft * 0.150

        # Unusable fuel weight
        self.m_unusable_fuel = lb2kg(
            (11.5 * self.n_eng * (n2lb(self.thrust_eng) ** 0.2))
            + (0.07 * sqm2sqft(a_wing))
            + (1.6 * self.n_fuel_tanks * (kg2lb(self.m_fuel) ** 0.28))
        )

        # calculate total completion mass
        self.total_mass = self.m_flight_crew + self.m_paint + self.m_unusable_fuel


class CompletionMass(BaseMassClass):
    """Completion Mass model to Operating Empty Weight (OWE)
    Includes Paint, Crew, Operating Items

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
            "combined": Combined,
            "specified": SpecifiedMass,
        }
