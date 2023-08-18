from typing import Dict
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass


class Standard(AbstractMassComponent):
    """
    Fuel mass calculation
    """

    def setup(self):
        inward_list = [
            "m_fuel_climb",
            "m_fuel_cruise",
            "m_fuel_descent",
            "m_fuel_taxi",
        ]
        super().setup(inward_list)

        self.add_outward("m_fuel_out")

    def compute_mass(self):
        # TODO: addition of Reserves and Alternate Fuel
        # calculate total completion mass
        self.m_fuel_out = (
            self.m_fuel_climb
            + self.m_fuel_cruise
            + self.m_fuel_descent
            + self.m_fuel_taxi
        )
        self.total_mass = self.m_fuel_out


class FuelMass(BaseMassClass):
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
            "standard": Standard,
            "specified": SpecifiedMass,
        }
