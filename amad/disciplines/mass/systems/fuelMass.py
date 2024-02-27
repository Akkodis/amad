from typing import Dict
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass


class Standard(AbstractMassComponent):
    """
    Fuel mass calculation
    """

    def setup(self):
        """
        Setup the object with the required lists.

        Parameters
        ----------
        self : object
            The object being set up.

        Returns
        -------
        None

        Raises
        ------
        None
        """
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
        """
        Compute the total mass of an object.

        This method calculates the total mass of an object by adding up the masses of its components.
        The fuel masses for climb, cruise, descent, and taxi are added together to obtain the total fuel mass.
        This total fuel mass is then assigned to the `m_fuel_out` attribute, and furthermore, to the `total_mass` attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.m_fuel_out = (
            self.m_fuel_climb
            + self.m_fuel_cruise
            + self.m_fuel_descent
            + self.m_fuel_taxi
        )
        self.total_mass = self.m_fuel_out


class FuelMass(BaseMassClass):
    """
    Completion Mass model to Operating Empty Weight (OWE)
    Includes Paint, Crew, Operating Items

    Parameters:
        name (str): System name
        model (str): Computation algorithm. Options are:
            - torenbeek: Egbeert Torenbeek

    Attributes:
        model: Concrete specialization of `AbstractMassComponent`.
            May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        """
        Set up the model with the specified parameters.

        Parameters
        ----------
        model : str
            The model to be set up.
        **parameters : keyword arguments
            Additional parameters for setting up the model.

        Raises
        ------
        TypeError
            If unsupported keyword arguments are provided.

        Notes
        -----
        This function calls the `setup` method of the superclass, passing the model and parameters as arguments.
        """
        super().setup(model=model, **parameters)

    @classmethod
    def models(cls) -> Dict[str, type]:
        """
        Dictionary of available models.
        """
        return {
            "standard": Standard,
            "specified": SpecifiedMass,
        }
