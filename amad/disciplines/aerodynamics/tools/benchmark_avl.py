import aerosandbox
import time
import sys
from amad.disciplines.design.resources.aircraft_geometry_library import (
    ac_narrow_body_long as airplane_geom,
)
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane


def run_benchmark_avl(avl_location):
    """
    Run a benchmark for AVL analysis on an airplane.

    Parameters
    ----------
    avl_location : str
        The location of the AVL executable.

    Returns
    -------
    None

    Raises
    ------
    None
    """
    generated_airplane = CreateAirplane(aero_geom=airplane_geom())
    generated_airplane.generate()

    operating_point = aerosandbox.OperatingPoint(
        atmosphere=aerosandbox.Atmosphere(altitude=8000.0),
        velocity=200.0,
        alpha=5.0,
        beta=0.0,
        p=0.0,  # The roll rate about the x_b axis. [rad/sec]
        q=0.0,
        r=0.0,
    )

    analysis = aerosandbox.AVL(
        airplane=generated_airplane.airplane,
        op_point=operating_point,
        verbose=False,
        # avl_command=avl_location
    )

    times = []
    for i in range(10):
        start_time = time.perf_counter()
        analysis.run()
        end_time = time.perf_counter()
        unit_time = end_time - start_time
        times.append(unit_time)
        print(f"time to run AVL = {unit_time:.3f} seconds")

    print(f"average time = {sum(times) / len(times)}")


if len(sys.argv) < 2:
    avl_location = "avl"
else:
    avl_location = sys.argv[1]

run_benchmark_avl(avl_location)
