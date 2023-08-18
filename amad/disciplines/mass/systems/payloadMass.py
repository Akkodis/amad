from typing import Dict
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass
from amad.tools.unit_conversion import lb2kg


class Internal(AbstractMassComponent):
    """Internally-created model"""

    def setup(self):
        inward_list = [
            "n_pax",
            "m_cargo",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("m_check_in")
        self.add_outward("m_pax")

    def compute_mass(self):
        self.m_pax = self.n_pax * lb2kg(195)  # pax weight including carry-on
        self.m_check_in = self.n_pax * lb2kg(30)

        # calculate total payload mass
        self.total_mass = self.m_pax + self.m_check_in + self.m_cargo


class PayloadMass(BaseMassClass):
    """Payload Mass model to Operating Empty Weight (OWE)
    Includes Passenger, baggage, fuel and cargo weight

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
            "internal": Internal,
            "specified": SpecifiedMass,
        }
