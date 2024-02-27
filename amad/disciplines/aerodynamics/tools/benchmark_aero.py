import time
import numpy
from amad.disciplines.aerodynamics.systems import AeroCalculateASB, AeroCalculateAVL
from amad.disciplines.design.resources.aircraft_geometry_library import (
    ac_narrow_body_long as airplane_geom,
)
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane

alt = 10000.0
mach = list(numpy.linspace(0.6, 0.8, 50))
alpha = -1.185


def benchmark_aero_flightpoint_asb():
    """
    Benchmark the performance of the AeroCalculateASB function for multiple flight points.

    Returns the total execution time for the benchmark.

    Returns
    -------
    float
        The total execution time of the benchmark.

    Note
    ----
    This function requires the `AeroCalculateASB` class from the `aerocalc` module.

    Raises
    ------
    None
    """
    method = "AVL"
    aercal = AeroCalculateASB(
        "aercal",
        asb_aircraft_geometry=airplane_geom(),
        option_method=method,
        init_altitude=alt,
        debug=False,
        option_optimization=False,
    )
    aercal.z_altitude = alt
    aercal.alpha_aircraft = alpha

    start_time = time.perf_counter()

    for m in mach:
        aercal.mach_current = m
        aercal.run_once()

    end_time = time.perf_counter()

    return end_time - start_time


def benchmark_aero_flightpoint_avl():
    """
    Benchmark the performance of the AeroCalculateAVL function.

    Returns the runtime in seconds of the AeroCalculateAVL function.

    Parameters
    ----------
    None

    Returns
    -------
    float
        The runtime in seconds of the AeroCalculateAVL function.

    Raises
    ------
    None
    """
    aercal_avl = AeroCalculateAVL(
        "aercal_avl",
        asb_aircraft_geometry=airplane_geom(),
        debug=False,
        working_directory="amad/disciplines/aerodynamics/temp/avl/",
    )
    aercal_avl.alpha_aircraft = alpha
    aercal_avl.beta_aircraft = 0.0
    aercal_avl.z_altitude = alt
    aercal_avl.mach_current = mach

    start_time = time.perf_counter()
    aercal_avl.run_drivers()
    end_time = time.perf_counter()

    return end_time - start_time


def benchmark_aero_create_vehicle():
    """
    Benchmark the performance of the `CreateAirplane` function for generating airplanes.

    This function measures the time it takes to generate a specified number of airplanes using the `CreateAirplane` class.
    It uses the `airplane_geom` function to obtain the geometry necessary for generating the airplanes.

    Returns
    -------
    None

    Notes
    -----
    The performance benchmark is performed by executing the `generate` method of the `CreateAirplane` instance 10 times,
    and measuring the total time taken for the generation.

    The time taken is printed to the console in seconds.

    Example
    -------
    >>> benchmark_aero_create_vehicle()
    time needed = 2.54321 seconds
    """
    geometry = airplane_geom()
    generator = CreateAirplane(aero_geom=geometry)

    start_time = time.perf_counter()

    for i in range(1, 11):
        generator.generate()

    end_time = time.perf_counter()
    print(f"time needed = {end_time - start_time} seconds")


if __name__ == "__main__":
    time_avl = benchmark_aero_flightpoint_avl()
    time_asb = benchmark_aero_flightpoint_asb()

    print(f"time AVL:{time_avl:.2f} time ASB:{time_asb:.2f}")
    print(f"AVL takes {100 * time_avl / time_asb:.0f}% of the time")
