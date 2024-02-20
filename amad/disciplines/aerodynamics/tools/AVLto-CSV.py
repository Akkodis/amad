from amad.disciplines.aerodynamics.systems import AeroCalculateAVL
from amad.disciplines.design.resources.aircraft_geometry_library import (
    ac_narrow_body_long_opti as airplane_geom,
)
import time
import numpy
import pandas

aercal_avl = AeroCalculateAVL(
    "aercal_avl",
    asb_aircraft_geometry=airplane_geom(),
    debug=False,
)
alpha_list = list(numpy.arange(-6, 12, 2))
mach_list = list(numpy.arange(0, 0.92, 0.04))
aercal_avl.alpha_aircraft = alpha_list
aercal_avl.beta_aircraft = 0.0

results = []

for mach in mach_list:
    aercal_avl.mach_current = mach

    for altitude in range(0, 14000, 500):
        aercal_avl.z_altitude = altitude  # list(numpy.linspace(0.0, 14000.0, 29))
        start_time = time.perf_counter()
        aercal_avl.run_drivers()
        end_time = time.perf_counter()
        total_time = end_time - start_time
        time_per_case = total_time / (
            len(alpha_list) * len(aercal_avl.z_altitude) * len(aercal_avl.mach_current)
        )

        result_df = pandas.DataFrame.from_dict(aercal_avl.raw_parameters).transpose()

        results.append(result_df)
