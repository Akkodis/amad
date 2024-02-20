import abc
from cosapp.base import System
from amad.disciplines.aerodynamics.ports import AeroPort


class BaseAeroCalculator(System):
    """
    A class representing a Base Aero Calculator.

    Parameters
    ----------
    setup : None
        Sets up the Aero Calculator.
    compute_aero : None
        Performs the calculation of aerodynamic forces and moments.
    compute : None
        Calls the compute_aero method and assigns the output values.

    Attributes
    ----------
    output : AeroPort
        The output port.
    mach_current : int, float, or list
        The current aircraft Mach number.
    alpha_aircraft : int, float, or list
        The angle of attack of the aircraft.
    beta_aircraft : int, float, or list
        The sideslip angle of the aircraft.
    rate_roll : float
        The roll rate of the aircraft.
    rate_pitch : float
        The pitch rate of the aircraft.
    rate_yaw : float
        The yaw rate of the aircraft.
    z_altitude : int, float, or list
        The altitude of the aircraft.
    L : list, str, float, or int
        The lift forces.
    D : list, str, float, or int
        The drag forces.
    Y : list, str, float, or int
        The side forces.
    l : list, str, float, or int
        The roll moments.
    m : list, str, float, or int
        The pitch moments.
    n : list, str, float, or int
        The yaw moments.
    CD : list, str, float, or int
        The drag coefficient.
    CL : list, str, float, or int
        The lift coefficient.
    CY : list, str, float, or int
        The side force coefficient.
    Cl : list, str, float, or int
        The roll moment coefficient.
    Cm : list, str, float, or int
        The pitch moment coefficient.
    Cn : list, str, float, or int
        The yaw moment coefficient.
    """
    def setup(self):
        # aero 'port' containing ...
        """
        Set up the inputs and outputs for the AeroPort component.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Inputs
        ------
        mach_current : int, float, or list
            Mach, current aircraft.
        alpha_aircraft : int, float, or list
            Angle of attack.
        beta_aircraft : int, float, or list
            Sideslip angle.
        rate_roll : float
            Roll rate in degrees per second.
        rate_pitch : float
            Pitch rate in degrees per second.
        rate_yaw : float
            Yaw rate in degrees per second.
        z_altitude : int, float, or list
            Altitude in meters.

        Outputs
        -------
        output : AeroPort object
            The output AeroPort object.
        L : list, str, float, or int
            Lift forces.
        D : list, str, float, or int
            Drag forces.
        Y : list, str, float, or int
            Side forces.
        l : list, str, float, or int
            Roll moments.
        m : list, str, float, or int
            Pitch moments.
        n : list, str, float, or int
            Yaw moments.
        CD : list, str, float, or int
            Drag coefficients.
        CL : list, str, float, or int
            Lift coefficients.
        CY : list, str, float, or int
            Side force coefficients.
        Cl : list, str, float, or int
            Roll moment coefficients.
        Cm : list, str, float, or int
            Pitch moment coefficients.
        Cn : list, str, float, or int
            Yaw moment coefficients.

        Raises
        ------
        None
        """
        self.add_output(AeroPort, "output")

        # standardized aero inputs
        # TODO replace with dict
        self.add_inward(
            "mach_current",
            0.0,
            dtype=(int, float, list),
            unit="",
            desc="Mach, current aircraft",
        )
        self.add_inward(
            "alpha_aircraft",
            0.0,
            dtype=(int, float, list),
            unit="deg",
            desc="Angle of attack",
        )
        self.add_inward(
            "beta_aircraft",
            0.0,
            dtype=(int, float, list),
            unit="deg",
            desc="Sideslip angle",
        )
        self.add_inward("rate_roll", 0.0, unit="deg/s")
        self.add_inward("rate_pitch", 0.0, unit="deg/s")
        self.add_inward("rate_yaw", 0.0, unit="deg/s")
        self.add_inward("z_altitude", 0.0, dtype=(int, float, list), unit="m")

        # computed outputs
        self.add_outward("L", 0.0, dtype=(list, str, float, int))
        self.add_outward("D", dtype=(list, str, float, int))
        self.add_outward("Y", dtype=(list, str, float, int))
        self.add_outward("l", dtype=(list, str, float, int))
        self.add_outward("m", dtype=(list, str, float, int))
        self.add_outward("n", dtype=(list, str, float, int))
        self.add_outward("CD", dtype=(list, str, float, int))
        self.add_outward("CL", dtype=(list, str, float, int))
        self.add_outward("CY", dtype=(list, str, float, int))
        self.add_outward("Cl", dtype=(list, str, float, int))
        self.add_outward("Cm", dtype=(list, str, float, int))
        self.add_outward("Cn", dtype=(list, str, float, int))

    @abc.abstractmethod
    def compute_aero(self) -> None:
        """
        Compute the aero parameter.

        Raises
        ------
        NotImplementedError
            This method must be implemented by a subclass.
        """
        pass

    def compute(self):
        """
        Compute the output variables for a given input.

        This method computes the values of various output variables based on the input values.

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
        self.compute_aero()

        # output all computed parameters to aero port
        self.output.L = self.L
        self.output.D = self.D
        self.output.Y = self.Y
        self.output.l = self.l
        self.output.m = self.m
        self.output.n = self.n
        self.output.CD = self.CD
        self.output.CL = self.CL
        self.output.CY = self.CY
        self.output.Cl = self.Cl
        self.output.Cm = self.Cm
        self.output.Cn = self.Cn
