import math
import numpy
import scipy
import zlib
from cosapp.base import System
from amad.disciplines.design.ports import AsbGeomPort
from amad.disciplines.aerodynamics.systems import AeroCalculateAVL


class CrzEquiPoint(System):
    """
    A class representing a system for calculating the equilibrium point of a CRZ aircraft.
    
    Parameters
    ----------
    asb_aircraft_geometry : dict
        A dictionary containing the aircraft geometry parameters.
    aero_calculator : object, optional
        An instance of the AeroCalculateAVL class used for aerodynamic calculations.
        Default is AeroCalculateAVL.
    option_optimization : bool, optional
        A boolean indicating whether optimization should be enabled or not.
        Default is True.
    kwargs : dict
        Additional keyword arguments.

    Attributes
    ----------
    m_mto : float
        The mass of the aircraft at takeoff.
    m_fuel_cruise : float
        The mass of fuel during cruise.
    geom_in : AsbGeomPort object
        The input for the aircraft geometry.
    aero_calculator : object
        An instance of the AeroCalculateAVL class used for aerodynamic calculations.
    n_alpha_samples : int
        The number of alpha samples to use in calculations.
    range_alpha : int
        The range of alpha values to use in calculations.
    phi_thrust_eng : float
        The inclination angle of the aircraft's engines.
    mach_current : float or list
        The current Mach number of the aircraft.
    z_altitude : int, float, or list
        The altitude of the aircraft.
    lift_int : scipy.interpolate.interp1d
        An interpolated function for lift.
    drag_int : scipy.interpolate.interp1d
        An interpolated function for drag.
    cl_int : scipy.interpolate.interp1d
        An interpolated function for lift coefficient.
    cd_int : scipy.interpolate.interp1d
        An interpolated function for drag coefficient.
    thrust_required : float
        The thrust required for the equilibrium point.
    thrust_delta : float
        The difference between horizontal and vertical thrust.
    thrust_horizontal : float
        The horizontal thrust component.
    thrust_vertical : float
        The vertical thrust component.
    lift_aircraft : float
        The lift at the equilibrium point.
    drag_aircraft : float
        The drag at the equilibrium point.
    alpha_aircraft : float
        The alpha value at the equilibrium point.
    ac_weight_force : float
        The weight force of the aircraft.
    v_tas : float
        The true airspeed of the aircraft.
    cache : dict
        A dictionary for caching calculation results.

    Methods
    -------
    setup(asb_aircraft_geometry: dict, aero_calculator=AeroCalculateAVL, option_optimization=True, **kwargs)
        Set up the system.
    launch_avl_calc(min_alpha, max_alpha)
        Launch AVL calculations for a range of alpha values.
    clear_cache()
        Clear the cache.
    _calc_t_h(alpha)
        Calculate the horizontal thrust component.
    _calc_t_v(alpha)
        Calculate the vertical thrust component.
    _calc_thrust(alpha)
        Calculate the total thrust.
    compute()
        Perform the computation for the equilibrium point.
    """    
    def setup(
        self,
        asb_aircraft_geometry: dict,
        aero_calculator=AeroCalculateAVL,
        option_optimization=True,
        **kwargs,
    ):
        """
        Initialize the aircraft analysis setup.

        Parameters
        ----------
        asb_aircraft_geometry : dict
            Dictionary containing aircraft geometry data.
        aero_calculator : class, optional
            Aero calculator class to be used for analysis (default is AeroCalculateAVL).
        option_optimization : bool, optional
            Flag indicating whether optimization is enabled (default is True).
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None

        Notes
        -----
        This method initializes the aircraft analysis setup by:
        - Adding inward and input properties related to aircraft mass, fuel, geometry, etc.
        - Initializing the aero calculator.
        - Adding properties related to alpha samples, alpha range, etc.
        - Adding inward properties related to engine inclination angle, Mach number, altitude, etc.
        - Adding outward properties related to lift, drag, CL, CD, thrust, etc.
        - Adding cache property.

        All properties are added to the setup object.
        """        
        self.add_inward("m_mto", 1, unit="kg")
        self.add_inward("m_fuel_cruise", 0, unit="kg")
        self.add_input(AsbGeomPort, "geom_in")

        # aero_calculator can be substituted at runtime with alternative calculation methods
        aero_calc_initialized = aero_calculator(
            "aero_calculator", asb_aircraft_geometry=asb_aircraft_geometry, debug=False
        )
        self.add_property("aero_calculator", aero_calc_initialized)
        self.add_property("n_alpha_samples", 4)
        self.add_property("range_alpha", 10)

        # define inwards
        self.add_inward("phi_thrust_eng", 0.0, desc="aircraft engine inclination angle")
        self.add_inward(
            "mach_current",
            0.0,
            dtype=(float, list),
            unit="",
            desc="Mach, current aircraft",
        )
        self.add_inward("z_altitude", 0.0, dtype=(int, float, list), unit="m")

        # define outwards (calculated parameters within this system)
        self.add_outward("lift_int")
        self.add_outward("drag_int")
        self.add_outward("cl_int")
        self.add_outward("cd_int")
        self.add_outward("thrust_required")
        self.add_outward("thrust_delta")
        self.add_outward(
            "thrust_horizontal"
        )  # thrust required to balance horizontal forces
        self.add_outward(
            "thrust_vertical"
        )  # thrust requried to balance vertical forces
        self.add_outward("lift_aircraft")
        self.add_outward("drag_aircraft")
        self.add_outward("alpha_aircraft")
        self.add_outward("ac_weight_force")
        self.add_outward("v_tas")
        self.add_outward("cache", {})  # cache object to store lift/drag polars

    def launch_avl_calc(self, min_alpha, max_alpha):
        """
        Calculate the lift, drag, lift coefficient, drag coefficient, and alpha_aircraft values for a given range of alpha values.

        Parameters
        ----------
        min_alpha : float
            The minimum alpha value.
        max_alpha : float
            The maximum alpha value.

        Returns
        -------
        tuple
            A tuple containing the following values:
            - L: The lift.
            - D: The drag.
            - CL: The lift coefficient.
            - CD: The drag coefficient.
            - alpha_aircraft: The alpha values.

        Raises
        ------
        None
        """        
        sac = self.aero_calculator
        sac.alpha_aircraft = list(
            numpy.linspace(min_alpha, max_alpha, num=self.n_alpha_samples)
        )
        sac.beta_aircraft = [0.0]
        sac.z_altitude = [self.z_altitude]
        sac.mach_current = [self.mach_current]

        sac.run_once()

        return sac.L, sac.D, sac.CL, sac.CD, sac.alpha_aircraft

    def clear_cache(self):
        """
        Clear the cache.

        This method clears the cache of the object.

        Parameters
        ----------
        self : object
            The object on which the method is called.

        Returns
        -------
        None

        Raises
        ------
        None
        """        
        self.cache.clear()

    def _calc_t_h(self, alpha):
        # horizontal force calculation
        # compute angles
        """
        Calculate the horizontal thrust component.

        Parameters
        ----------
        self : object
            The instance of the class.
        alpha : float
            The angle of attack in degrees.

        Returns
        -------
        float
            The horizontal thrust component.

        Raises
        ------
        None

        Notes
        -----
        This function internally calls the `lift_int` and `drag_int` methods from the class.

        The angle `alpha` is converted to radians before further calculations.

        The horizontal thrust component is calculated using the lift and drag coefficients, as well as the angle of attack.

        This function assumes that the instance has attributes `phi_thrust_eng` (the angle of the thrust engine in degrees), `lift_int` (method to calculate the lift coefficient), and `drag_int` (method to calculate the drag coefficient).
        """        
        alpha_rad = math.radians(alpha)
        angle_thrust_rad = math.radians(self.phi_thrust_eng) + alpha_rad

        # Horizontal forces:
        t_h = (
            self.lift_int(alpha) * math.sin(alpha_rad)
            + self.drag_int(alpha) * math.cos(alpha_rad)
        ) / math.cos(angle_thrust_rad)

        return t_h

    def _calc_t_v(self, alpha):
        # vertical force calculation
        # compute angles
        """
        Calculate the thrust-to-weight ratio for a given angle of attack.

        Parameters
        ----------
        alpha : float
            The angle of attack in degrees.

        Returns
        -------
        float
            The thrust-to-weight ratio.

        Notes
        -----
        This method assumes that `alpha` is given in degrees and converts it to radians using `math.radians`.

        The thrust-to-weight ratio (`t_v`) is calculated using the formula:
        t_v = (drag_int(alpha) * sin(alpha_rad) + ac_weight_force - lift_int(alpha) * cos(alpha_rad)) / sin(angle_thrust_rad)

        Raises
        ------
        None
        """        
        alpha_rad = math.radians(alpha)
        angle_thrust_rad = math.radians(self.phi_thrust_eng) + alpha_rad

        # Vertical forces:
        t_v = (
            self.drag_int(alpha) * math.sin(alpha_rad)
            + self.ac_weight_force
            - self.lift_int(alpha) * math.cos(alpha_rad)
        ) / math.sin(angle_thrust_rad)

        return t_v

    def _calc_thrust(self, alpha):
        """
        Calculate the thrust difference between horizontal and vertical components.

        Parameters
        ----------
        alpha : float
            The angle of attack in degrees.

        Returns
        -------
        float
            The thrust difference.
        """        
        return self._calc_t_h(alpha) - self._calc_t_v(alpha)

    def compute(self):
        # send incoming geometry to aero calc
        """
        Compute various aerodynamic parameters for an aircraft.

        Raises
        ------
        ValueError
            If an error occurs during the computation.

        Notes
        -----
        This function performs multiple calculations and assignments to various attributes of the `self` object. It updates the `aero_calculator`, `ac_weight_force`, `lift_int`, `drag_int`, `cl_int`, `cd_int`, `thrust_required`, `thrust_delta`, `thrust_horizontal`, `thrust_vertical`, `lift_aircraft`, `drag_aircraft`, and `alpha_aircraft` attributes.

        This function uses the `geom_in`, `m_mto`, `m_fuel_cruise`, `phi_thrust_eng`, `mach_current`, `z_altitude`, `range_alpha`, `_calc_thrust`, `_calc_t_h`, `_calc_t_v`, `launch_avl_calc`, `interp1d`, `bounds_error`, `cache`, `v_tas`, `optimize`, `brentq`, and `nan` attributes from the `self` object.

        The computation involves setting the `ac_weight_force` attribute, calculating a checksum with `zlib.adler32`, caching and retrieving values from the `cache` dictionary, interpolating values with `interp1d`, optimizing using `brentq`, and assigning various attributes.

        This function is specifically designed for use in conjunction with certain attributes and methods. It may raise a `ValueError` if an exception occurs during the computation.
        """        
        self.aero_calculator.geom_in.asb_aircraft_geometry = (
            self.geom_in.asb_aircraft_geometry
        )

        # calc weight force
        # TODO: work only with current weight as input - not MTO
        self.ac_weight_force = (
            self.m_mto - 0.5 * self.m_fuel_cruise
        ) * scipy.constants.g

        # create a checksum from a composite of geometry and input parameters
        check_string = (
            str(self.geom_in.asb_aircraft_geometry)
            + str(self.phi_thrust_eng)
            + str(self.mach_current)
            + str(self.z_altitude)
        )
        checksum = zlib.adler32(check_string.encode("utf-8"))

        # check cache file to see if lift/drag values exist
        try:
            self.lift_int = self.cache[checksum]["lift_int"]
            self.drag_int = self.cache[checksum]["drag_int"]
            self.cl_int = self.cache[checksum]["cl_int"]
            self.cd_int = self.cache[checksum]["cd_int"]

        except KeyError:
            # run AVL and get lists of lift/drag across the alpha range
            lift, drag, cl, cd, alpha = self.launch_avl_calc(
                min_alpha=-self.range_alpha, max_alpha=self.range_alpha
            )

            # create interpolators for lift/drag/cl/cd
            self.lift_int = scipy.interpolate.interp1d(
                alpha, lift, kind="linear", bounds_error=False
            )
            self.drag_int = scipy.interpolate.interp1d(
                alpha, drag, kind="cubic", bounds_error=False
            )
            self.cl_int = scipy.interpolate.interp1d(
                alpha, cl, kind="linear", bounds_error=False
            )
            self.cd_int = scipy.interpolate.interp1d(
                alpha, cd, kind="cubic", bounds_error=False
            )

            # store them in the cache for later use
            self.cache[checksum] = {
                "lift_int": self.lift_int,
                "drag_int": self.drag_int,
                "cl_int": self.cl_int,
                "cd_int": self.cd_int,
            }

        # calculate equilibrium alpha
        # find valid alpha ranges by root of a function calculation using Brent's method
        alpha_equilib = numpy.nan
        minmax_alpha = [
            [-self.range_alpha, -1e-10],
            [1e-10, self.range_alpha],
            [-1e-10, 1e-10],
        ]
        for minmax in minmax_alpha:
            try:
                alpha_equilib = scipy.optimize.brentq(
                    self._calc_thrust, minmax[0], minmax[1]
                )
                break
            except ValueError:
                pass

        v_tas = self.aero_calculator.v_tas
        self.v_tas = v_tas[0] if type(v_tas) is list else v_tas

        self.thrust_required = max(
            self._calc_t_h(alpha_equilib), self._calc_t_v(alpha_equilib)
        )
        self.thrust_delta = abs(
            self._calc_t_h(alpha_equilib) - self._calc_t_v(alpha_equilib)
        )
        self.thrust_horizontal = self._calc_t_h(alpha_equilib)
        self.thrust_vertical = self._calc_t_v(alpha_equilib)
        self.lift_aircraft = self.lift_int(alpha_equilib)
        self.drag_aircraft = self.drag_int(alpha_equilib)
        self.alpha_aircraft = alpha_equilib


if __name__ == "__main__":
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long as airplane_geom,
    )
    from amad.disciplines.powerplant.systems import EnginePerfoMattingly
    import time
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    """
    Problem Set-up
    """
    equi = CrzEquiPoint(
        "equi",
        asb_aircraft_geometry=airplane_geom(),
        option_optimization=False,
        working_directory="amad/disciplines/aerodynamics/temp/avl/",
    )
    equi.z_altitude = 8000.8
    equi.m_mto = 50000.0
    equi.mach_current = 0.75

    """
    System Performance Calculation
    """
    start_time = time.perf_counter()
    equi.run_drivers()
    end_time = time.perf_counter()
    # nb: 15 seconds for this run case
    debug_message = (
        f"time={end_time - start_time:.1f} "
        + f"alpha={equi.alpha_aircraft:.5f} "
        + f"l/d={equi.lift_aircraft / equi.drag_aircraft:.1f} "
        + f"t_h= {equi.thrust_horizontal:.0f} "
        + f"t_v= {equi.thrust_vertical:.0f} "
        + f"lift={equi.lift_aircraft:.0f} "
        + f"drag={equi.drag_aircraft:.0f}"
    )
    # TODO: print in logging
    print(debug_message)

    """
    Lift / drag / Delta thrust equilibrium
    """

    lift_int = equi.lift_int
    drag_int = equi.drag_int

    alpha_list = numpy.linspace(-10.0, 10.0, 1000)
    lift_list = lift_int(alpha_list)
    drag_list = drag_int(alpha_list)
    th_list = []
    tv_list = []
    delta_thrust = []
    for alpha in alpha_list:
        th = equi._calc_t_h(alpha)
        tv = equi._calc_t_v(alpha)
        th_list.append(th)
        tv_list.append(tv)
        delta_thrust.append(th - tv)

    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(
        go.Scatter(x=alpha_list, y=lift_list, name="Lift Force (N)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=alpha_list, y=drag_list, name="Drag Force (N)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=alpha_list, y=th_list, name="Thrust Horizontal Force (N)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=alpha_list, y=tv_list, name="Thrust Vertical Force (N)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=alpha_list, y=delta_thrust, name="Delta Thrust Force (N)"),
        secondary_y=False,
    )

    fig.update_xaxes(title_text="Alpha (deg)")
    fig.update_yaxes(title_text="Force (N)")

    fig.update_layout(template="plotly_white")

    fig.show()

    """
    Economic Speed Calculation
    """
    min_mach = 0.4
    max_mach = 0.9

    mach_list = numpy.linspace(min_mach, max_mach, 6)
    mach_list_fine = numpy.linspace(min_mach, max_mach, 1000)
    thr_req_list = []
    fc_list = []

    epm = EnginePerfoMattingly("epm", altitude=equi.z_altitude, dISA=0.0)
    epm.thrust_eng = 120000

    for m in mach_list:
        print(f"calculating thrust for mach {m}")
        equi.mach_current = m
        epm.mach_current = m
        equi.run_drivers()
        epm.run_once()
        thrust = equi.thrust_required
        fc_sec = thrust * epm.SFC  # kg / second
        fc_dist = 1000 * fc_sec / equi.v_tas  # kg / km

        thr_req_list.append(equi.thrust_required)
        fc_list.append(fc_dist)

    int_fc = scipy.interpolate.interp1d(
        mach_list, fc_list, kind="cubic", bounds_error=False
    )
    fc_int_list = [int_fc(m) for m in mach_list_fine]

    mach_opt = scipy.optimize.minimize_scalar(
        int_fc, bounds=(min_mach, max_mach), method="bounded"
    )
    print(f"mach optimum = {mach_opt.x:.3f}")

    fig2 = make_subplots(specs=[[{"secondary_y": False}]])

    fig2.add_trace(
        go.Scatter(
            x=mach_list_fine,
            y=fc_int_list,
            name="Range-specific Fuel Consumption (kg/km)",
        ),
        secondary_y=False,
    )

    fig2.add_trace(
        go.Scatter(x=[mach_opt.x], y=[int_fc(mach_opt.x)], name="Optimum mach"),
        secondary_y=False,
    )

    fig2.show()

    """
    Lift / drag / debug
    """

    lift_int = equi.lift_int
    drag_int = equi.drag_int

    alpha_list = numpy.linspace(-10.0, 10.0, 1000)
    lift_list = lift_int(alpha_list)
    drag_list = drag_int(alpha_list)

    equi.run_drivers()

    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(
        go.Scatter(x=alpha_list, y=lift_list, name="Lift Force orig (N)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=alpha_list, y=drag_list, name="Drag Force orig (N)"),
        secondary_y=False,
    )

    fig.show()
