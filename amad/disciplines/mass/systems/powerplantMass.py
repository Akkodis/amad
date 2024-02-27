import math
from typing import Dict
from amad.disciplines.mass.systems import (
    AbstractMassComponent,
    BaseMassClass,
    SpecifiedMass,
)
from amad.tools.unit_conversion import lb2kg, n2lb, m2ft


class ModRaymer(AbstractMassComponent):
    """
    Engine Mass estimation method for modern (>1980) turbofan engines
    Raymer method is used with coefficients re-optimized.
    FLOPS methods are used for engine control and starting masses

    Parameters
    ----------
    r_bypass : float
        The bypass ratio of the engine.
    n_eng : int
        The number of engines.
    thrust_eng : float
        The thrust of each engine.
    mach_mo : float
        The Mach number.
    d_nacelle : float
        The diameter of the nacelle.
    """

    def setup(self):
        """
        Set up the class instance with predefined parameters and lists.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        This function is intended to be called during the instantiation of the class.

        Example
        -------
        >>> obj = ClassName()
        >>> obj.setup()
        """
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
        """
        Compute the total mass of an engine system.

        Parameters
        ----------
        self : object
            The instance of the `EngineSystem` class.

        Returns
        -------
        None

        Notes
        ------
        This function updates the following attributes of the `EngineSystem` instance:
        - `m_eng`: Mass of the engine itself.
        - `m_eng_ctrl`: Mass of the engine control system.
        - `m_eng_starter`: Mass of the engine starter.
        - `total_mass`: Total mass of the engine system.

        Raises
        ------
        None
        """
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
    """
    Engine mass model. Estimates only the engine part

    Parameters
    ----------
    name : str
        System name
    model : str
        Computation algorithm. Options are:
            - cairns: Statistical model using thrust and bypass ratio
            - specified: User-specified mass

    Children
    --------
    model : AbstractMassComponent
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        """
        Set up the model with the given parameters.

        Parameters
        ----------
        model : str
            The name of the model to set up.

        **parameters : dict
            Additional parameters to pass to the setup function.

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
        Dictionary of available models.
        """
        return {
            "mod-raymer": ModRaymer,
            "specified": SpecifiedMass,
        }
