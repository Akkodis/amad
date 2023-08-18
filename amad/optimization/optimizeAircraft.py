import pandas
import itertools
import numpy
from cosapp.base import System
from cosapp.drivers import Optimizer, NonLinearSolver

# from cosapp.recorders import DataFrameRecorder
from amad.disciplines.performance.systems import CruiseFuel
from amad.disciplines.flight_dynamics.systems import TakeOffLift
from amad.disciplines.mass.systems import AircraftMass
from amad.disciplines.design.systems import GenerateAeroGeom
from amad.disciplines.design.resources.aircraft_geometry_library import (
    ac_narrow_body_long as airplane_geom,
)
from amad.tools.pullingFilter import pulling_filter
from amad.optimization.resources.set_parameters import single_aisle_concept


class OptimizeAircraftMass(System):
    def setup(self):
        model_list = [
            GenerateAeroGeom("ac_geom"),
            AircraftMass("mass"),
            CruiseFuel("cruise_fuel", asb_aircraft_geometry=airplane_geom()),
            TakeOffLift("to_lift", asb_aircraft_geometry=airplane_geom()),
        ]

        exceptions = [
            "m_fuel_cruise",
            "m_fuel_cruise_out",
            "x_fuse",
            "asb_aircraft_geometry_out",
        ]

        for model in model_list:
            self.add_child(
                model,
                pulling=pulling_filter(
                    model.inwards, model.outwards, exceptions=exceptions
                ),
            )

        self.connect(self.ac_geom.geom_out, self.cruise_fuel.geom_in)
        self.connect(self.ac_geom.geom_out, self.to_lift.geom_in)
        self.connect(self.ac_geom, self.mass, {"x_fuse_out": "x_fuse"})

        self.add_inward("sweep_outer")
        self.add_inward("span_outer")

        self.add_unknown("m_mto", lower_bound=10000.0)
        self.add_equation("m_mto == mass.total_mass")

    def compute(self):
        # set geometry params
        inner_sweep = (31.5 / 23.5) * self.sweep_outer
        self.delta_wing_sweep = [inner_sweep, self.sweep_outer]
        self.x_wing_span = [self.x_wing_span[0], self.span_outer]
        self.mass.m_fuel_cruise = self.cruise_fuel.m_fuel_cruise.mass


def optimize_geom():
    # import time
    # timestr = time.strftime("%Y%m%d-%H%M%S")

    opt = single_aisle_concept(OptimizeAircraftMass("opt"))

    # Performance params
    opt.z_altitude = 11000.0  # cruise altitude
    opt.mach_current = 0.78  # cruise mach
    opt.thrust_eng = 120000.0
    opt.x_range = 5000 * 1000.0  # 5000km

    opt.n_pax = 189

    # Fuel params
    opt.m_fuel_climb = 2300.0
    opt.m_fuel_descent = 300.0
    opt.m_fuel_taxi = 500.0

    # opt.to_html('opt.html')

    # Optimization
    optim = opt.add_driver(Optimizer("optim", method="Powell"))
    optim.add_unknown("chord_wing_root", lower_bound=8.2, upper_bound=9.0)
    optim.set_objective("cruise_fuel.m_fuel_cruise.mass")
    optim.add_constraints(["to_lift.f_lift_takeoff > mass.total_mass"])

    optim.add_child(NonLinearSolver("nls", method="NR", tol=1e-2))

    # Add recorder to monitor iterations
    # optim.add_recorder(
    #     DataFrameRecorder(
    #         includes = [
    #             "ac_geom.geom_out.asb_aircraft_geometry",
    #             "to_lift.f_lift_takeoff",
    #             "mass.total_mass",
    #             "cruise_fuel.m_fuel_cruise_out",
    #             "delta_wing_sweep",
    #             "r_wing_taper",
    #             "x_wing_span",
    #         ],
    #         hold=True  # to save each iter
    #     )
    # )
    # optim.options['monitor'] = True

    # start_time = time.perf_counter()
    opt.run_drivers()
    # end_time = time.perf_counter()

    # df = optim.recorder.export_data()
    # print(df)

    # df.to_csv(f'{timestr}_optimize_results.csv')

    # print(f'total time = {end_time - start_time}')
    print(f"{opt.mass.total_mass=}")
    print(f"{opt.chord_wing_root=}")


def Cartesian_DoE(axes: dict) -> pandas.DataFrame:
    """
    Simple Cartesian grid DoE from 1D samples in all axis directions
    https://cosapp.readthedocs.io/en/latest/tutorials/SystemSurrogates.html
    """
    return pandas.DataFrame(
        list(itertools.product(*axes.values())),
        columns=list(axes.keys()),
    )


def generate_metamodel_manual():
    import time

    timestr = time.strftime("%Y%m%d-%H%M%S")

    print("initializing model...")
    meta = single_aisle_concept(OptimizeAircraftMass("opt"))
    meta.add_driver(NonLinearSolver("nls", method="NR", tol=1e-2))

    # Performance params
    meta.z_altitude = 10058.4  # cruise altitude
    meta.m_fuel_climb = 2300.0
    meta.m_fuel_descent = 300.0
    meta.m_fuel_taxi = 500.0
    meta.n_pax = 189
    meta.mach_current = 0.8  # cruise mach
    meta.thrust_eng = 120000.0
    meta.x_range = 5000 * 1000.0  # 5000km

    # axes = {
    #     'wing_sweep_outer': numpy.linspace(15, 40, 11), # curve 11
    #     'chord_wing_root': numpy.linspace(5, 10, 2),    # linear 3
    #     'n_pax': list(range(150, 251, 10)),             # curve
    #     'outer_span': numpy.linspace(15, 45, 13),       # curve 13
    #     'mach_current': numpy.linspace(.65, .8, 4),     # linear 4
    #     'x_range': numpy.linspace(5e6, 8e6, 4),         # linear 4
    # }

    axes = {
        "wing_sweep_outer": numpy.linspace(15, 35, 11),
        "chord_wing_root": numpy.linspace(8.0, 10, 11),
        "outer_span": numpy.linspace(33.5, 40, 11),
        # 'mach_current': numpy.linspace(.65, .8, 4),     # linear 4
        # 'x_range': numpy.linspace(5e6, 8e6, 4),         # linear 4
    }

    print("generating doe...")
    doe = Cartesian_DoE(axes)

    total_cases = len(doe)
    print(f"total cases = {total_cases}")
    conso = []
    mtow = []
    mzfw = []
    m_structure = []
    m_payload = []
    m_systems = []
    m_fuel = []
    to_lift = []
    delta_to_lift = []

    start_time = time.perf_counter()
    for index, row in doe.iterrows():
        inner_sweep = (31.5 / 23.5) * row["wing_sweep_outer"]
        meta["delta_wing_sweep"] = [inner_sweep, row["wing_sweep_outer"]]
        meta["chord_wing_root"] = row["chord_wing_root"]
        # meta['n_pax'] = int(row['n_pax'])
        meta["x_wing_span"] = [meta["x_wing_span"][0], row["outer_span"]]
        # meta['mach_current'] = row['mach_current']
        # meta['x_range'] = row['x_range']

        print_data = (
            f"run {index}/{total_cases} || "
            + f"sweep={meta.delta_wing_sweep[0]} "
            + f"chord_wing_root={meta.chord_wing_root:.2f} "
            + f"n_pax={meta.n_pax} "
            + f"span={meta.x_wing_span[1]:.2f} "
            + f"mach= {meta.mach_current:.2f} "
            + f"range= {meta.x_range/1000:.0f} "
            + f"fuselen= {meta.mass.x_fuse:.2f} "
            + f"acmass= {meta.mass.total_mass:.0f}"
        )

        print(print_data)
        meta.run_drivers()

        ec = int(meta.drivers["nls"].error_code)
        if ec > 0:
            conso.append(numpy.nan)
            mtow.append(numpy.nan)
            mzfw.append(numpy.nan)
            to_lift.append(numpy.nan)
            delta_to_lift.append(numpy.nan)
            m_structure.append(numpy.nan)
            m_payload.append(numpy.nan)
            m_systems.append(numpy.nan)
            m_fuel.append(numpy.nan)

            meta.drivers.clear()
            meta.add_driver(NonLinearSolver("nls", method="NR", tol=1e-2))
        else:
            conso.append(meta.cruise_fuel.m_fuel_cruise.mass)
            mtow.append(meta.mass.total_mass)
            mzfw.append(meta.mass.m_zfw)
            to_lift.append(meta.to_lift.f_lift_takeoff)
            delta_to_lift.append(meta.to_lift.f_lift_takeoff - meta.mass.total_mass)
            m_structure.append(meta.mass.structure_mass)
            m_payload.append(meta.mass.payload_mass)
            m_systems.append(meta.mass.systems_mass)
            m_fuel.append(meta.mass.fuel.total.mass)

    end_time = time.perf_counter()

    doe["conso"] = conso
    doe["mtow"] = mtow
    doe["mzfw"] = mzfw
    doe["to_lift"] = to_lift
    doe["delta_to_lift"] = delta_to_lift
    doe["m_structure"] = m_structure
    doe["m_payload"] = m_payload
    doe["m_systems"] = m_systems
    doe["m_fuel"] = m_fuel

    run_time = end_time - start_time
    print(f"total time = {run_time}")
    print(f"time per run = {run_time / total_cases}")

    doe.to_pickle(f"doe_{timestr}.pickle")
    doe.to_csv(f"doe_{timestr}.csv")


def generate_metamodel_cosapp():
    print("initializing model...")
    meta = single_aisle_concept(OptimizeAircraftMass("meta"))
    meta.add_driver(NonLinearSolver("nls", method="NR", tol=1e-2))

    # Performance params
    meta.z_altitude = 10058.4  # cruise altitude
    meta.m_fuel_climb = 2300.0
    meta.m_fuel_descent = 300.0
    meta.m_fuel_taxi = 500.0
    meta.n_pax = 189
    meta.mach_current = 0.8  # cruise mach
    meta.thrust_eng = 120000.0
    meta.n_pax = 189
    meta.x_range = 5000 * 1000.0  # 5000km

    print("running once to capture reference test data...")
    meta.run_drivers()
    print(
        f"reference total mass = {meta.mass.total_mass} for a chord of {meta.chord_wing_root}"
    )

    axes = {
        "sweep_outer": numpy.linspace(15, 35, 6),
        "chord_wing_root": numpy.linspace(8.5, 9, 6),
        "span_outer": numpy.linspace(33.5, 40, 6),
    }

    print("generating doe...")
    doe = Cartesian_DoE(axes)

    meta.make_surrogate(doe, postsynch="mass.total_mass")
    meta.dump_surrogate("AMAD_Meta_Demo.pickle")

    print(f"meta.has_surrogate: {meta.has_surrogate}")
    # data_out = meta_surr.state.data_out  # pandas df with surrogate results

    print("testing doe...")
    meta.chord_wing_root = 8.57
    meta.run_drivers()

    print(
        f"Expected MTOW value = 83290.506 kg, DOE MTOW value = {meta.mass.total_mass:.3f} kg"
    )


def run_once():
    opt = single_aisle_concept(OptimizeAircraftMass("opt"))

    # Performance params
    opt.z_altitude = 11000.0  # cruise altitude
    opt.mach_current = 0.75  # cruise mach
    opt.thrust_eng = 120000.0
    opt.x_range = 5000 * 1000.0  # 5000km

    # Fuel params
    opt.m_fuel_climb = 2300.0
    opt.m_fuel_descent = 300.0
    opt.m_fuel_taxi = 500.0
    opt.mass.m_fuel_cruise = 20000.0

    opt.add_driver(NonLinearSolver("nls", tol=0.1))

    # system__output = str(opt.to_dict())
    # with open('opt_run_single.json', 'w') as f:
    #     f.write(system__output)

    opt.run_drivers()
    print(f"{opt.mass.total_mass}")

    opt["x_wing_span"] = [opt["x_wing_span"][0], 10]
    opt.run_drivers()
    print(f"{opt.mass.total_mass}")

    opt["x_wing_span"] = [opt["x_wing_span"][0], 34]
    opt["x_fuse"] = 60.0
    opt.run_drivers()
    print(f"{opt.mass.total_mass}")

    opt["x_fuse"] = 50.0
    opt.run_drivers()
    print(f"{opt.mass.total_mass}")

    opt["x_fuse"] = 30.0
    opt.run_drivers()
    print(f"{opt.mass.total_mass}")


if __name__ == "__main__":
    generate_metamodel_cosapp()
