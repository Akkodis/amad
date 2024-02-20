import math
from typing import Dict
from amad.disciplines.mass.systems import (
    AbstractMassComponent,
    BaseMassClass,
    SpecifiedMass,
)
from amad.tools.unit_conversion import lb2kg, n2lb, m2ft


class FLOPS(AbstractMassComponent):
    """
    FLOPS Nacelle Mass estimation method for various aircraft

    Parameters
    ----------
    tech_center_eng : float
        The distance from the aircraft centerline to the center of the engine.
    n_eng : int
        The number of engines on the aircraft.
    d_nacelle : float
        The diameter of the nacelle.
    x_nacelle : float
        The axial distance between the aircraft centerline and the nacelle centerline.
    thrust_eng : float
        The thrust of the engine.
    """

    def setup(self):
        """
        Sets up the object with the necessary attributes and configurations.

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
        """
        Compute the mass of a nacelle.

        Parameters
        ----------
        self : object
            The instance of the class.

        Returns
        -------
        None

        Raises
        ------
        None
        """
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
    """
    Torenbeek Nacelle Mass estimation method for transport aircraft

    Influencing Parameters:
        r_bypass:
            - Type: float
            - Description: The bypass ratio of the engine
        thrust_eng:
            - Type: float
            - Description: The thrust of each engine
        n_eng:
            - Type: int
            - Description: The number of engines
    """

    def setup(self):
        """
        Set up the object with necessary attributes.

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
        """
        Calculate the mass of a component.

        This method calculates the mass of a component, given certain inputs.

        Parameters
        ----------
        self : object
            The instance of the class calling this method.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.k_nac = 0.055 if self.r_bypass <= 2.5 else 0.065
        self.thrust_total = n2lb(force=(self.thrust_eng * self.n_eng))

        # calculate mass
        self.m_nacelle = self.k_nac * self.thrust_total
        self.total_mass = lb2kg(mass=(self.m_nacelle))


class NacelleMass(BaseMassClass):
    """
    Nacelle Mass model

    Parameters
    ----------
    name : str
        System name
    model : str
        Computation algorithm. Options are:
        - torenbeek: Egbeert Torenbeek
        - flops: NASA FLOPS
        - specified: User-specified mass

    Children
    --------
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
            The name of the model to be set up.

        **parameters : dict
            Additional parameters specific to the model. These parameters will be passed to the parent class setup method.

        Raises
        ------
        None

        Returns
        -------
        None
        """
        super().setup(model=model, **parameters)

    @classmethod
    def models(cls) -> Dict[str, type]:
        """
        Dictionary of available models
        """
        return {
            "torenbeek": Torenbeek,
            "flops": FLOPS,
            "specified": SpecifiedMass,
        }
