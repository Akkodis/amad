from cosapp.base import System
from amad.disciplines.mass.systems import AircraftMass
from amad.disciplines.design.systems import GenerateAeroGeom
from amad.disciplines.performance.systems import CruiseFuel
from amad.tools.pullingFilter import pulling_filter


class CalculateAircraft(System):
    def setup(self, airplane_geom: dict):
        """Setup of CalculateAircraft

        Args:
            airplane_geom (dict): aircraft geometry dict
        """
        model_list = [
            GenerateAeroGeom("ac_geom"),
            AircraftMass("mass"),
            CruiseFuel("cruise_fuel", asb_aircraft_geometry=airplane_geom),
        ]

        exceptions = ["m_fuel_cruise", "m_fuel_cruise_out", "x_fuse"]

        for model in model_list:
            self.add_child(
                model,
                pulling=pulling_filter(
                    model.inwards, model.outwards, exceptions=exceptions
                ),
            )

        self.connect(self.ac_geom.geom_out, self.cruise_fuel.geom_in)
        self.connect(self.ac_geom, self.mass, {"x_fuse_out": "x_fuse"})
        # self.connect(self.cruise_fuel, self.mass, {'m_fuel_cruise.mass': 'm_fuel_cruise'})

        self.add_unknown("m_mto", lower_bound=10000.0)
        self.add_equation("m_mto == mass.total_mass")

        # self.connect(self.mass, self.cruise_fuel, mapping={'m_mto': 'm_gross.mass'})
        # self.connect(self.mass, self.cruise_fuel, {'mtow': 'm_gross'})

    def compute(self):
        self.mass.m_fuel_cruise = self.cruise_fuel.m_fuel_cruise.mass
        # self.cruise_fuel.equi.m_fuel_cruise = self.cruise_fuel.m_fuel_cruise.mass


if __name__ == "__main__":
    from cosapp.drivers import NonLinearSolver
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long as airplane_geom,
    )
    from amad.optimization.resources.set_parameters import single_aisle_concept

    def print_msg(ac_sys):
        """Print Routine

        Args:
            ac_sys (obj): summary of aircradft parameters
        """
        msg = (
            f"Span = {ac_sys.x_wing_span[1]}m, "
            + f"Total fuel = {ac_sys.mass.m_fuel_out:.0f}kg, "
            + f"Cruise fuel = {ac_sys.mass.m_fuel_cruise:.0f}kg, "
            + f"Thr v = {ac_sys.cruise_fuel.equi.thrust_vertical:.0f}N, "
            + f"Thr h = {ac_sys.cruise_fuel.equi.thrust_horizontal:.0f}N, "
            + f"Thr delta = {ac_sys.cruise_fuel.equi.thrust_delta:.0f}N, "
            + f"Total lift = {ac_sys.cruise_fuel.equi.lift_aircraft:.0f}N "
            + f"at {ac_sys.cruise_fuel.equi.alpha_aircraft:.3f} deg "
            + f"x_fuse = {ac_sys.mass.fuse.x_fuse:.0f} "
            + f"fuse mass = {ac_sys.mass.fuse.total_mass:.0f} "
            + f"m_mto = {ac_sys.m_mto:.0f} "
            + f"total_mass = {ac_sys.mass.total_mass:.0f} "
            + f"diff_mass = {ac_sys.m_mto - ac_sys.mass.total_mass:.0f} "
            + f"solver code = {calc_perf.drivers['nls'].error_code} "
        )
        print(msg)

    tolerance = 1e-2
    calc_perf_init = CalculateAircraft("calc_perf", airplane_geom=airplane_geom())
    calc_perf = single_aisle_concept(calc_perf_init)
    calc_perf.add_driver(NonLinearSolver("nls", method="POWELL", tol=tolerance))
    calc_perf.m_fuel_climb = 2300.0
    calc_perf.m_fuel_descent = 300.0
    calc_perf.m_fuel_taxi = 500.0
    calc_perf.mass.m_fuel_cruise = 123.0
    calc_perf.z_altitude = 11582.4  # cruise altitude
    calc_perf.mach_current = 0.75  # cruise mach
    calc_perf.thrust_eng = 120000.0
    calc_perf.n_pax = 150
    calc_perf.x_range = 5000 * 1000.0  # 5000km

    calc_perf.run_drivers()
    print_msg(calc_perf)
