import scipy
import zlib
from cosapp.base import System
from amad.disciplines.design.ports import AsbGeomPort
from amad.disciplines.aerodynamics.systems import AeroCalculateAVL


class TakeOffLift(System):
    """
    Very Basic Lift Off point calculation (no equilibrium calc): no conf, no L/G, no TOD integration, etc.
    """

    def setup(
        self, asb_aircraft_geometry: dict, aero_calculator=AeroCalculateAVL, **kwargs
    ):
        self.add_input(AsbGeomPort, "geom_in")

        # aero_calculator can be substited at runtime with alternative calculation methods
        aero_calc_initialized = aero_calculator(
            "aero_calculator", asb_aircraft_geometry=asb_aircraft_geometry, debug=False
        )
        self.add_property("aero_calculator", aero_calc_initialized)

        # define inwards
        self.add_inward(
            "mach_takeoff", 0.0, dtype=(float, list), unit="", desc="Mach, takeoff"
        )
        self.add_inward("z_altitude_takeoff", 0.0, dtype=(int, float, list), unit="m")
        self.add_inward("alpha_takeoff", 0.0, dtype=(int, float, list), unit="m")

        # define outwards (calculated parameters within this system)
        self.add_outward("f_lift_takeoff", unit="kg")
        self.add_outward("f_drag_takeoff", unit="kg")
        self.add_outward("cache", {})

    def launch_avl_calc(self):
        self.aero_calculator.alpha_aircraft = [self.alpha_takeoff]
        self.aero_calculator.beta_aircraft = [0.0]
        self.aero_calculator.z_altitude = [self.z_altitude_takeoff]
        self.aero_calculator.mach_current = [self.mach_takeoff]

        self.aero_calculator.run_once()

        return self.aero_calculator.L, self.aero_calculator.D

    def compute(self):
        # send incoming geometry to aero calc
        self.aero_calculator.geom_in.asb_aircraft_geometry = (
            self.geom_in.asb_aircraft_geometry
        )

        # create a checksum from the geometry
        check_string = (
            str(self.geom_in.asb_aircraft_geometry)
            + str(self.mach_takeoff)
            + str(self.z_altitude_takeoff)
        )

        checksum = zlib.adler32(check_string.encode("utf-8"))

        # check cache file to see if lift/drag values exist
        try:
            lift = self.cache[checksum]["lift"]
            drag = self.cache[checksum]["drag"]
        except KeyError:
            # run AVL and get lift/drag for the given takeoff config
            (
                lift,
                drag,
            ) = self.launch_avl_calc()

            # store them in the cache for later use
            self.cache[checksum] = {"lift": lift, "drag": drag}

        self.f_lift_takeoff = lift / scipy.constants.g
        self.f_drag_takeoff = drag / scipy.constants.g


if __name__ == "__main__":
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long as airplane_geom,
    )

    """
    Problem Set-up
    """
    liftoff = TakeOffLift(
        "liftoff",
        asb_aircraft_geometry=airplane_geom(),
        working_directory="amad/disciplines/aerodynamics/temp/avl",
    )
    liftoff.z_altitude_takeoff = 0.0
    liftoff.alpha_takeoff = 0.0
    liftoff.mach_takeoff = 0.41

    """
    System Performance Calculation
    """

    liftoff.run_drivers()
    print(f"Takeoff lift: {liftoff.f_lift_takeoff:.0f}kg")

    liftoff.mach_takeoff = 0.40
    liftoff.run_drivers()
    print(f"Takeoff lift: {liftoff.f_lift_takeoff:.0f}kg")

    liftoff.mach_takeoff = 0.39
    liftoff.run_drivers()
    print(f"Takeoff lift: {liftoff.f_lift_takeoff:.0f}kg")
