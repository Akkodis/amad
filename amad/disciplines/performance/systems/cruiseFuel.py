from cosapp.base import System
from amad.disciplines.mass.ports import MassPort
from amad.disciplines.powerplant.systems import EnginePerfoMattingly
from amad.disciplines.flight_dynamics.systems import CrzEquiPoint


class CruiseFuel(System):
    def setup(
        self,
        asb_aircraft_geometry,
        equi_calculator=CrzEquiPoint,
        ff_calculator=EnginePerfoMattingly,
        **kwargs,
    ):
        # self.add_outward('m_fuel_cruise_out', unit='kg')
        self.add_output(MassPort, "m_fuel_cruise")

        pulling_equi = [
            "m_mto",
            "phi_thrust_eng",
            "mach_current",
            "z_altitude",
            "thrust_required",
            "v_tas",
            "geom_in",
        ]

        self.add_child(
            equi_calculator(
                "equi",
                asb_aircraft_geometry=asb_aircraft_geometry,
                init_altitude=8000.0,
                option_optimization=True,
            ),
            pulling=pulling_equi,
        )

        self.add_child(ff_calculator("ff", **kwargs), pulling=["SFC", "inwards"])
        self.add_inward("x_range", 0.0, unit="m", desc="Design range")

    def compute(self):
        # time taken to complete cruise segment (assumes zero wind speed)
        time_crz = self.x_range / self.equi.v_tas

        # fuel for cruise segment
        self.m_fuel_cruise.mass = max(
            1, self.ff.SFC * self.equi.thrust_required * time_crz
        )


if __name__ == "__main__":
    from cosapp.drivers import NonLinearSolver
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long as airplane_geom,
    )
    import time

    crzfuel = CruiseFuel("crzfuel", asb_aircraft_geometry=airplane_geom())
    crzfuel.z_altitude = 8000.0
    crzfuel.mach_current = 0.7
    crzfuel.thrust_eng = 120000.0
    crzfuel.x_range = 5000 * 1000.0
    crzfuel.m_mto = 50000.0

    crzfuel.add_driver(NonLinearSolver("nls"))

    st = time.perf_counter()
    crzfuel.run_drivers()
    et = time.perf_counter()

    print(
        f"calculation time={et-st:.1f} alt[ft]={crzfuel.z_altitude / .3048:.0f} cruise segment fuel req [kg] = {crzfuel.m_fuel_cruise.mass:.0f} at vtas [m/s]={crzfuel.v_tas:.1f}"
    )
