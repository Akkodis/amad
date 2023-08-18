import math
import numpy
import scipy
import zlib
from cosapp.base import System
from amad.disciplines.design.ports import AsbGeomPort
from amad.disciplines.aerodynamics.systems import AeroCalculateAVL


class CrzEquiPoint(System):
    def setup(
        self,
        asb_aircraft_geometry: dict,
        aero_calculator=AeroCalculateAVL,
        option_optimization=True,
        **kwargs,
    ):
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
        self.cache.clear()

    def _calc_t_h(self, alpha):
        # horizontal force calculation
        # compute angles
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
        return self._calc_t_h(alpha) - self._calc_t_v(alpha)

    def compute(self):
        # send incoming geometry to aero calc
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
