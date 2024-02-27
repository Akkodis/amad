from typing import Dict
import numpy
import math
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass
from amad.tools.unit_conversion import kg2lb, lb2kg, sqm2sqft, m2ft
from amad.disciplines.design.tools.averageSweep import average_sweep
from amad.disciplines.design.tools.liftingArea import lifting_area


class SimpleAC(AbstractMassComponent):
    """
    Mass estimation method from the SimPleAC project.

    Reference:
    https://github.com/peterdsharpe/AeroSandbox/blob/master/tutorial/02%20-%20Design%20Optimization/03%20-%20Aircraft%20Design%20-%20SimPleAC.ipynb

    Parameters
    ----------
    m_mto : float
        Take-off mass of the aircraft.
    r_wing_taper : float
        Wing taper ratio.
    chord_wing_root : float
        Chord length at the root of the wing.
    v_fuel_fuse : float
        Fuselage volume dedicated to fuel.
    r_wing_aspect : float
        Wing aspect ratio.
    """

    def setup(self):
        """
        Initialize the object and set up the inputs and outputs for the calculation.

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
            "m_mto",
            "r_wing_taper",
            "chord_wing_root",
            "v_fuel_fuse",
            "r_wing_aspect",
            "x_wing_span",
        ]
        super().setup(inward_list)

        # constants
        self.add_inward("W_W_coeff1", 2e-5, desc="wing weight coefficient 1")
        self.add_inward("W_W_coeff2", 60.0, desc="wing weight coefficient 2")
        self.add_inward("tau", 0.12, desc="airfoil thickness to chord ratio")
        self.add_inward("N_ult", 3.3, desc="ultimate load factor")
        self.add_inward("W_0", 6250, desc="aircraft empty weight excluding wing, N")
        self.add_inward("rho_f", 817, desc="density of fuel, kg/m^3")
        self.add_inward("g", 9.81, desc="gravitational acceleration, m/s^2")

        # computed variables
        self.add_outward("W", desc="total aircraft weight, N")
        self.add_outward("W_w_surf")
        self.add_outward("W_w_strc")

    def compute_mass(self):
        # compute wing area
        """
        Compute the total mass of an aircraft.

        Parameters
        ----------
        self : object
            An instance of the Aircraft class.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        a_wing = lifting_area(self.x_wing_span, self.r_wing_taper, self.chord_wing_root)

        # unit conversions
        self.W = self.m_mto * self.g  # convert mass to force

        # compute variables
        self.W_w_surf = self.W_W_coeff2 * a_wing
        self.W_w_strc = (
            self.W_W_coeff1
            / self.tau
            * self.N_ult
            * (self.r_wing_aspect**1.5)
            * numpy.sqrt(
                (self.W_0 + self.v_fuel_fuse * self.g * self.rho_f) * self.W * a_wing
            )
        )

        # output wing mass
        self.total_mass = (self.W_w_surf + self.W_w_strc) / self.g


class Cessna(AbstractMassComponent):
    """
    Mass estimation method for GA aircraft originally from Cessna
    Applicable to small low-speed aircraft (under 200kts max speed)

    Parameters
    ----------
    m_mto : float
        Maximum takeoff mass of the aircraft.
    r_wing_taper : float
        Wing taper ratio.
    chord_wing_root : float
        Chord of the wing root.
    n_ult : float
        Ultimate load factor.
    r_wing_aspect : float
        Wing aspect ratio.
    tech_bracing : str
        Bracing technology used.

    Reference
    ---------
    Roskam, J. (1989). Airplane Design: Part V. Component Weight Estimation.
    """

    def setup(self):
        """
        Set up the configuration.

        Parameters
        ----------
        self : object
            The object being configured.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        inward_list = [
            "m_mto",
            "r_wing_taper",
            "chord_wing_root",
            "n_ult",
            "r_wing_aspect",
            "tech_bracing",
            "x_wing_span",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("m_wing")

    def compute_mass(self):
        # compute wing area
        """
        Compute the mass of an aircraft wing.

        Parameters
        ----------
        self : object
            The instance of the class that contains the input parameters.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        a_wing = lifting_area(self.x_wing_span, self.r_wing_taper, self.chord_wing_root)

        # unit conversions
        a_wing = sqm2sqft(a_wing)

        # compute wing mass
        if self.tech_bracing != "strut":  # cantilever wings
            self.m_wing = (
                0.04674
                * (kg2lb(self.m_mto) ** 0.397)
                * (a_wing**0.360)
                * (self.n_ult**0.397)
                * (self.r_wing_aspect**1.712)
            )

        else:  # strut-braced wings
            self.m_wing = (
                0.002933
                * (a_wing**1.018)
                * (self.r_wing_aspect**2.473)
                * (self.n_ult**0.611)
            )

        # output wing mass with unit conversion
        self.total_mass = lb2kg(mass=self.m_wing)


class Torenbeek(AbstractMassComponent):
    """
    Mass estimation method for GA and transport aircraft.
    Applicable to small low-speed aircraft (<12,500 lb GW) or
    transport aircraft (>12,500lb GW)

    Reference:
    - Torenbeek, E. (1982). Synthesis of subsonic airplane design

    Influencing Parameters:
    - m_mto
    - r_wing_taper
    - chord_wing_root
    - n_ult
    - x_wing_span
    - delta_wing_sweep
    - t_wing_root_chord
    - m_mzf
    """

    def setup(self):
        """
        Set up the inward and outward variables for the class.

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
            "m_mto",
            "r_wing_taper",
            "chord_wing_root",
            "n_ult",
            "x_wing_span",
            "delta_wing_sweep",
            "t_wing_root_chord",
            "m_mzf",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("coeff_size")
        self.add_outward("m_wing")
        self.add_outward("m_ac")

    def compute_mass(self):
        # compute wing area
        """
        Compute the mass of an aircraft wing.

        Parameters
        ----------
        self : object
            The object containing the input parameters for the mass computation.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        a_wing = lifting_area(self.x_wing_span, self.r_wing_taper, self.chord_wing_root)

        # unit conversions
        m_mto = kg2lb(self.m_mto)
        if isinstance(self.x_wing_span, list):
            x_wing_span = m2ft(max(self.x_wing_span))
        else:
            x_wing_span = m2ft(self.x_wing_span)

        # compute sweep
        delta_wing_sweep_av = math.radians(
            average_sweep(spans=self.x_wing_span, sweeps=self.delta_wing_sweep)
        )

        # compute wing mass
        if m_mto < 12500:
            self.coeff_size = 0.00125  # light transport ac
            self.m_ac = m_mto
        else:
            self.coeff_size = 0.00170  # heavier transport ac
            self.m_ac = kg2lb(self.m_mzf)

        # equation terms
        eq1 = (
            self.coeff_size
            * self.m_ac
            * ((x_wing_span / math.cos(delta_wing_sweep_av)) ** 0.75)
        )
        eq2 = 1 + (6.3 * math.cos(delta_wing_sweep_av) / x_wing_span) ** 0.5
        eq3 = self.n_ult**0.55
        eq4 = (
            x_wing_span
            * sqm2sqft(a_wing)
            / (m2ft(self.t_wing_root_chord) * self.m_ac * math.cos(delta_wing_sweep_av))
        ) ** 0.3

        self.m_wing = eq1 * eq2 * eq3 * eq4

        # output wing mass
        self.total_mass = lb2kg(mass=self.m_wing)


class WingMass(BaseMassClass):
    """
    Wing Mass model

    Parameters
    ----------
    name : str
        System name
    model : str
        Computation algorithm. Options are:
            - simpleac: Model proposed by Hoburg et al
            - cessna: Cessna
            - torenbeek: Egbeert Torenbeek
            - specified: Specified Mass by user

    Attributes
    ----------
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
        **parameters : keyword arguments
            Additional parameters to configure the model.

        Raises
        ------
        TypeError
            If an unsupported parameter is provided.

        Notes
        -----
        This method overrides the setup method in the parent class.
        """
        super().setup(model=model, **parameters)

    @classmethod
    def models(cls) -> Dict[str, type]:
        """
        Dictionary of available models.
        """
        return {
            "simpleac": SimpleAC,
            "cessna": Cessna,
            "torenbeek": Torenbeek,
            "specified": SpecifiedMass,
        }
