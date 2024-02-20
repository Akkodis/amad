from cosapp.base import System
from amad.disciplines.mass.ports import MassPort
from amad.disciplines.powerplant.systems import EnginePerfoMattingly
from amad.disciplines.flight_dynamics.systems import CrzEquiPoint


class CruiseFuel(System):
    """
    A class representing a cruise fuel system.

    Parameters
    ----------
    asb_aircraft_geometry : AircraftGeometry
        The geometry of the aircraft.
    equi_calculator : Callable, optional
        The function used to calculate the equilibrium point. Default is CrzEquiPoint.
    ff_calculator : Callable, optional
        The function used to calculate the fuel flow. Default is EnginePerfoMattingly.
    **kwargs : dict, optional
        Additional keyword arguments to pass to the ff_calculator.

    Attributes
    ----------
    m_fuel_cruise : MassPort
        The mass port representing the cruise fuel mass.
    equi : EquiPoint
        The equilibrium point calculator.
    ff : EnginePerfoMattingly
        The fuel flow calculator.
    x_range : float
        The design range in meters.

    Methods
    -------
    setup(asb_aircraft_geometry, equi_calculator, ff_calculator, **kwargs)
        Sets up the cruise fuel system.
    compute()
        Computes the fuel consumption during cruise.
    """
    def setup(
        self,
        asb_aircraft_geometry,
        equi_calculator=CrzEquiPoint,
        ff_calculator=EnginePerfoMattingly,
        **kwargs,
    ):
        # self.add_outward('m_fuel_cruise_out', unit='kg')
        """
        Initialize the object and set up the calculations for aircraft performance and fuel flow.

        Parameters
        ----------
        asb_aircraft_geometry : object
            An object representing the aircraft geometry.
        equi_calculator : object, optional
            An object representing the equipment calculator. Default is CrzEquiPoint.
        ff_calculator : object, optional
            An object representing the fuel flow calculator. Default is EnginePerfoMattingly.
        **kwargs : dict
            Additional keyword arguments for the ff_calculator.

        Returns
        -------
        None

        Notes
        -----
        This function sets up the object by adding the necessary outputs, children, and inwards.

        The following children are added:
        - An instance of the equi_calculator class, named 'equi', with the specified parameters.
        - An instance of the ff_calculator class, named 'ff', with the specified parameters.

        The following outputs are added:
        - An instance of the MassPort class, named 'm_fuel_cruise'.

        The following inwards are added:
        - An inward named 'x_range', with a default value of 0.0 meters and a unit of 'm'. This represents the design range.

        Examples
        --------
        >>> obj = setup(asb_aircraft_geometry, equi_calculator=CrzEquiPoint, ff_calculator=EnginePerfoMattingly)
        """
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
        """
        Compute the fuel consumption during cruise.

        Raises
        ------
        None

        Returns
        -------
        None
        """
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
