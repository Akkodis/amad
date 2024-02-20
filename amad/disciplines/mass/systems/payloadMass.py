from typing import Dict
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass
from amad.tools.unit_conversion import lb2kg


class Internal(AbstractMassComponent):
    """
    Internally-created model
    """

    def setup(self):
        """
        Initialize the class and set up the inward and outward attributes.

        Parameters
        ----------
        self : object
            The class object.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        inward_list = [
            "n_pax",
            "m_cargo",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("m_check_in")
        self.add_outward("m_pax")

    def compute_mass(self):
        """
        Compute the total mass of an object.

        This function calculates the total mass of an object using the following formula:
        total_mass = m_pax + m_check_in + m_cargo

        Parameters
        ----------
        self : object
            The object containing the necessary attributes to calculate the mass.

        Returns
        -------
        None

        Attributes Modified
        -------------------
        self.m_pax : float
            The mass of the passengers.
        self.m_check_in : float
            The mass of the checked-in items.
        self.total_mass : float
            The total mass of the object.

        Raises
        ------
        None
        """
        self.m_pax = self.n_pax * lb2kg(195)  # pax weight including carry-on
        self.m_check_in = self.n_pax * lb2kg(30)

        # calculate total payload mass
        self.total_mass = self.m_pax + self.m_check_in + self.m_cargo


class PayloadMass(BaseMassClass):
    """
    Payload Mass model to Operating Empty Weight (OWE)

    Parameters
    ----------
    name : str
        System name.
    model : str
        Computation algorithm. Options are:
        - torenbeek: Egbeert Torenbeek

    Attributes
    ----------
    model : AbstractMassComponent
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        """
        Set up the model with the specified parameters.

        Parameters
        ----------
        model : str
            The name of the model to set up.
        **parameters : keyword arguments
            Additional parameters to pass to the model setup.

        Raises
        ------
        TypeError
            If an invalid parameter is provided.

        Returns
        -------
        None
            This function does not return anything.

        Note
        ----
        This function calls the superclass's setup method and passes the specified model and parameters.
        """
        super().setup(model=model, **parameters)

    @classmethod
    def models(cls) -> Dict[str, type]:
        """
        Dictionary of available models
        """
        return {
            "internal": Internal,
            "specified": SpecifiedMass,
        }
