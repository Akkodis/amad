from cosapp.base import System
from amad.disciplines.mass.ports import MassPort
import numpy


class WingMassSimpleAC(System):
    """
    A class representing a simplified wing mass estimation for an aircraft.

    Parameters
    ----------
    S : float
        The wing surface area.
    V_f_fuse : float
        The volume of fuel in the fuselage, in cubic meters.
    W : float
        The total aircraft weight, in Newtons.
    AR : float
        The aspect ratio of the wing.
    W_W_coeff1 : float, optional
        The wing weight coefficient 1. Default value is 2e-05.
    W_W_coeff2 : float, optional
        The wing weight coefficient 2. Default value is 60.0.
    tau : float, optional
        The airfoil thickness to chord ratio. Default value is 0.12.
    N_ult : float, optional
        The ultimate load factor. Default value is 3.3.
    W_0 : float, optional
        The aircraft empty weight excluding wing, in Newtons. Default value is 6250.
    rho_f : float, optional
        The density of fuel, in kg/m^3. Default value is 817.
    g : float, optional
        The gravitational acceleration, in m/s^2. Default value is 9.81.

    Attributes
    ----------
    W_w_surf : float
        The weight of the wing surface area.
    W_w_strc : float
        The weight of the wing structure.
    total.mass : float
        The total mass of the wing.

    Notes
    -----
    This class assumes a simplified calculation for wing mass estimation, based on the given input parameters.
    The wing mass is calculated using the wing weight coefficients, aspect ratio, airfoil thickness to chord ratio,
    ultimate load factor, total aircraft weight, wing surface area, volume of fuel in the fuselage,
    aircraft empty weight excluding wing, density of fuel and gravitational acceleration.
    """
    def setup(self):
        # weight 'port'
        """
        Set up the aircraft weight calculation.

        Parameters
        ----------
        self : object
            The object instance.

        Returns
        -------
        None

        Adds the following outputs to the object instance
        ----------
        total : MassPort
            The total mass output of the aircraft.

        Adds the following inputs to the object instance
        ----------
        S : float
            Wing surface area in square meters.
        V_f_fuse : float
            Fuel volume in the fuselage in cubic meters.
        W : float
            Total aircraft weight in Newtons.
        AR : float
            Aspect ratio.
        W_W_coeff1 : float, default 2e-05
            Wing weight coefficient 1.
        W_W_coeff2 : float, default 60.0
            Wing weight coefficient 2.
        tau : float, default 0.12
            Airfoil thickness to chord ratio.
        N_ult : float, default 3.3
            Ultimate load factor.
        W_0 : float, default 6250
            Aircraft empty weight excluding wing in Newtons.
        rho_f : float, default 817
            Density of fuel in kilograms per cubic meter.
        g : float, default 9.81
            Gravitational acceleration in meters per square second.

        Adds the following outputs to the object instance
        ----------
        W_w_surf : MassPort
            The surface weight of the wings.
        W_w_strc : MassPort
            The structural weight of the wings.
        """
        self.add_output(MassPort, "total")

        # free variables
        self.add_inward("S", desc="wing surface area")
        self.add_inward("V_f_fuse", desc="fuel volume in the fuselage, m^3")
        self.add_inward("W", desc="total aircraft weight, N")
        self.add_inward("AR", desc="aspect ratio")

        # constants
        self.add_inward("W_W_coeff1", 2e-5, desc="wing weight coefficient 1")
        self.add_inward("W_W_coeff2", 60.0, desc="wing weight coefficient 2")
        self.add_inward("tau", 0.12, desc="airfoil thickness to chord ratio")
        self.add_inward("N_ult", 3.3, desc="ultimate load factor")
        self.add_inward("W_0", 6250, desc="aircraft empty weight excluding wing, N")
        self.add_inward("rho_f", 817, desc="density of fuel, kg/m^3")
        self.add_inward("g", 9.81, desc="gravitational acceleration, m/s^2")

        # computed variables
        self.add_outward("W_w_surf")
        self.add_outward("W_w_strc")

    def compute(self):
        # compute variables
        """
        Compute the total mass of an aircraft.

        Calculates the total mass of an aircraft using specified coefficients, parameters, and properties.

        Attributes
        ----------
        W_w_surf : float
            Wing weight due to surface area.
        W_w_strc : float
            Wing weight due to structure.
        total.mass : float
            Total mass of the aircraft.

        Parameters
        ----------
        W_W_coeff1 : float
            Coefficient 1 for calculating wing weight due to structure.
        W_W_coeff2 : float
            Coefficient 2 for calculating wing weight due to surface area.
        tau : float
            Wing thickness-to-chord ratio.
        N_ult : float
            Ultimate load factor.
        AR : float
            Aspect ratio.
        W_0 : float
            Initial weight of the aircraft.
        V_f_fuse : float
            Fuel volume fraction in the fuselage.
        g : float
            Acceleration due to gravity.
        rho_f : float
            Density of the fuel.
        W : float
            Wing loading.
        S : float
            Wing surface area.

        Raises
        ------
        None
        """
        self.W_w_surf = self.W_W_coeff2 * self.S
        self.W_w_strc = (
            self.W_W_coeff1
            / self.tau
            * self.N_ult
            * (self.AR**1.5)
            * numpy.sqrt(
                (self.W_0 + self.V_f_fuse * self.g * self.rho_f) * self.W * self.S
            )
        )

        # output wing mass
        self.total.mass = self.W_w_surf + self.W_w_strc
