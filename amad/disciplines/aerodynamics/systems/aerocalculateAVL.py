import aerosandbox
import math
import numpy
import itertools
import subprocess
import tempfile
import json
import shutil
import sarge
import copy
import psutil
import scipy.constants
from amad.disciplines.aerodynamics.systems import BaseAeroCalculator
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane
from amad.disciplines.design.ports import AsbGeomPort
from amad.tools.atmosBADA import AtmosphereAMAD


class AeroCalculateAVL(BaseAeroCalculator):
    def setup(
        self,
        asb_aircraft_geometry: dict,
        atmos_model=AtmosphereAMAD(),
        init_altitude=0.0,
        option_optimization=True,
        debug=False,
        avl_command="avl",
        avl_keys=None,
        working_directory=None,
    ):
        self.add_input(AsbGeomPort, "geom_in")
        self.add_outward("asb_geometry_internal", asb_aircraft_geometry)

        # pre-generate ASB Airplane object
        generated_airplane = CreateAirplane(
            aero_geom=asb_aircraft_geometry, generate_airfoil_polars=False
        )
        generated_airplane.generate()

        # create keystroke inputs
        if avl_keys is None:
            avl_keys = "\n".join(["oper", "xx", "", "", "q"])

        # determine working directory
        remove_temp_directory = False
        if working_directory is None:
            working_directory = tempfile.mkdtemp()
            remove_temp_directory = True

        # count number of physical CPU cores
        n_cores = psutil.cpu_count(logical=False)

        self.add_property("atmos_model", atmos_model)
        self.add_property("flight_vehicle", generated_airplane)
        self.add_property("option_optimization", option_optimization)
        self.add_property("max_avl_cases", 25)
        self.add_property("debug", debug)
        self.add_property("avl_command", avl_command)
        self.add_property("avl_keystrokes", avl_keys)
        self.add_property("working_directory", working_directory)
        self.add_property("remove_temp_directory", remove_temp_directory)
        self.add_property("n_cores", n_cores)

        # aerodynamic outwards
        self.add_outward("raw_parameters", dtype=(dict, list, str, float, int))
        self.add_outward("v_tas", dtype=(dict, list, str, float, int))
        self.add_outward("run_data", {}, dtype=dict, desc="dictionary of run cases")
        self.add_outward("avl_out", desc="dictionary of completed run data")
        self.add_outward("n_avl_input_files", 1)
        self.add_outward("n_run_cases")
        self.add_outward("S")
        self.add_outward("b")
        self.add_outward("c")

        super().setup()

    def __create_avl_runfile(self, run_data: dict):
        # creates an AVL run file text content (with multiple cases if provided)
        runfile = []
        header = "---------------------------------------------"

        for index, key in enumerate(run_data):
            # compute intermediate params
            altitude = run_data[key]["altitude"]
            v_tas = self.atmos_model.mach2tas(alt=altitude, M=run_data[key]["Mach"])
            rho = self.atmos_model.airdens_kgpm3(altitude)
            # pressure = self.atmos_model.airpress_pa(altitude)
            q = 0.5 * rho * v_tas**2

            # add intermediate params to results as we'll use them later
            self.raw_parameters[key]["q"] = q
            self.raw_parameters[key]["v_tas"] = v_tas

            # calculate drag due to nacelle
            nacelle_c = 5.7e-3
            nacelle_k = 1.8e7
            nacelle_drag_unit = (
                self.asb_geometry_internal["d_nacelle"] * math.pi * q / nacelle_k
            ) + nacelle_c
            nacelle_drag = self.asb_geometry_internal["n_eng"] * nacelle_drag_unit

            # append to runfile
            runfile.append(header)
            runfile.append(f"Run case  {index+1}: -{key+1}-")
            runfile.append(f'alpha -> alpha = {run_data[key]["alpha"]}')
            runfile.append(f'beta -> beta = {run_data[key]["beta"]}')
            runfile.append("pb/2V -> pb/2V = 0.0000")
            runfile.append("qc/2V -> qc/2V = 0.0000")
            runfile.append("rb/2V -> rb/2V = 0.0000")
            runfile.append(f"CDo = {nacelle_drag}")
            runfile.append(f'Mach = {run_data[key]["Mach"]}')
            runfile.append(f"velocity = {v_tas}")
            runfile.append(f"density = {rho}")
            runfile.append(f"grav.acc. = {scipy.constants.g}")

        # debug
        if self.debug is True:
            run_file = open(f"{self.working_directory}/avl_raw_params.txt", "w")
            run_file.write(
                str(json.dumps(self.raw_parameters, sort_keys=False, indent=4))
            )
            run_file.close()

        runfile_text = "\n".join(runfile)
        return runfile_text

    def __create_run_data(self):
        # populate an array of input cases
        axes = {
            "alpha": self.alpha_aircraft,
            "beta": self.beta_aircraft,
            "altitude": self.z_altitude,
            "Mach": self.mach_current,
        }

        # create dictionary of all run cases
        run_data_dict = {
            key: dict(zip(axes, data))
            for key, data in enumerate(itertools.product(*axes.values()))
        }

        # make a copy which we'll append results to later
        self.raw_parameters = copy.deepcopy(run_data_dict)

        # capture number of total run cases
        self.n_run_cases = len(run_data_dict)

        # split dictionary into blocks of n run cases (for batching and multithreading)
        final_data = {}
        keys = list(run_data_dict.keys())

        for h, i in enumerate(range(0, len(keys), self.max_avl_cases)):
            final_data[h] = {
                k: run_data_dict[k] for k in keys[i : i + self.max_avl_cases]
            }

        self.run_data = final_data

    def __to_list(self, aero_param):
        if type(aero_param) is not list:
            return [aero_param]
        else:
            return aero_param

    def __create_aircraft_file(self):
        # return aircraft txt
        pass

    def __process_avl_output(self, avl_compute_data: str, n_runs=1):
        # loop thru output text and extract parameter values
        pos_res = 0
        keys = {  # could be a user input (opt)
            "Alpha": "alpha-res",
            "CLtot": "CL",
            "CDtot": "CD",
            "CYtot": "CY",
            "Cltot": "Cl",
            "Cmtot": "Cm",
            "Cntot": "Cn",
        }
        # all_res = {}

        for i in range(n_runs):
            # see if the next run case is possible to find
            try:
                pos_res = avl_compute_data.index("Run case: -", pos_res + 1)
            except ValueError:
                print("ERROR: Run case not found")
                pos_res = pos_res

            # add all parameters from keys
            for key in keys:
                name = keys[key]
                try:
                    pos_key = avl_compute_data.index(key, pos_res)
                    pos_eq = avl_compute_data.index("=", pos_key)
                    value = float(avl_compute_data[pos_eq + 1 : pos_eq + 12])
                    self.raw_parameters[i][name] = value
                except ValueError:
                    self.raw_parameters[i][name] = numpy.nan

            # add calculated parameters
            q = self.raw_parameters[i]["q"]
            self.raw_parameters[i]["L"] = q * self.S * self.raw_parameters[i]["CL"]
            self.raw_parameters[i]["Y"] = q * self.S * self.raw_parameters[i]["CY"]
            self.raw_parameters[i]["D"] = q * self.S * self.raw_parameters[i]["CD"]
            self.raw_parameters[i]["l_b"] = (
                q * self.S * self.b * self.raw_parameters[i]["Cl"]
            )
            self.raw_parameters[i]["m_b"] = (
                q * self.S * self.c * self.raw_parameters[i]["Cm"]
            )
            self.raw_parameters[i]["n_b"] = (
                q * self.S * self.b * self.raw_parameters[i]["Cn"]
            )

    def __remove_temp_dir(self):
        if self.remove_temp_directory is True:
            shutil.rmtree(self.working_directory, ignore_errors=True)

    def __split_job_cpus(self, iterable):
        # splits a list of run cases according to number of available CPU cores
        return itertools.zip_longest(
            *[iter(iterable)] * (self.n_cores - 1), fillvalue=None
        )

    def __compute_avl_single(self):
        # single-threaded AVL computation

        command = f"{self.avl_command} airplane.avl"
        results = ""

        # run AVL and capture output
        for run in self.run_data:
            run_data = self.run_data[run]

            # convert run to runfile text
            run_file_data = self.__create_avl_runfile(run_data=run_data)

            # write run file to disk
            run_file = open(f"{self.working_directory}/airplane.run", "w")
            run_file.write(run_file_data)
            run_file.close()

            # run computation
            avl_results_object = subprocess.run(
                command,
                shell=True,
                cwd=self.working_directory,
                input=self.avl_keystrokes,
                text=True,
                capture_output=True,
            )

            if self.debug is True:
                res_run_file = open(
                    f"{self.working_directory}/avl_results_{run}.txt", "w"
                )
                res_run_file.write(
                    str(avl_results_object).encode("utf-8").decode("unicode_escape")
                )
                res_run_file.close()

            # append results to previous runs
            results = results + str(avl_results_object).encode("utf-8").decode(
                "unicode_escape"
            )

        # debug
        if self.debug is True:
            all_res_file = open(f"{self.working_directory}/avl_results_all.txt", "w")
            all_res_file.write(results)
            all_res_file.close()

        # process final results and return
        return self.__process_avl_output(
            avl_compute_data=results, n_runs=self.n_run_cases
        )

    def __compute_avl_multi(self):
        # multi-core AVL computation

        results = ""
        commands = []

        # prepare run files
        for run in self.run_data:
            # prepare path
            run_data = self.run_data[run]
            run_file = f"{self.working_directory}/airplane_{run}.run"

            # convert run to runfile text
            run_file_data = self.__create_avl_runfile(run_data=run_data)

            # write run file to disk
            run_file = open(f"{run_file}", "w")
            run_file.write(run_file_data)
            run_file.close()

            # add command to list
            commands.append(f"{self.avl_command} airplane.avl airplane_{run}.run")

        # run AVL and capture output
        procs = [
            sarge.run(
                command,
                input=self.avl_keystrokes,
                stdout=sarge.Capture(),
                async_=True,
                cwd=self.working_directory,
            )
            for command in commands
        ]

        # wait for all processes to finish
        for proc in procs:
            proc.wait()

        # capture results
        results = "\n".join([proc.stdout.text for proc in procs])

        # debug
        if self.debug is True:
            all_res_file = open(f"{self.working_directory}/avl_results_all.txt", "w")
            all_res_file.write(results)
            all_res_file.close()

        # process final results and return
        return self.__process_avl_output(
            avl_compute_data=results, n_runs=self.n_run_cases
        )

    def compute_aero(self):
        if self.option_optimization is True and self.geom_in.asb_aircraft_geometry:
            # Update the flight vehicle geometry (useful when this is changing due to optimization)
            self.asb_geometry_internal = self.geom_in.asb_aircraft_geometry
            self.flight_vehicle.update(latest_geom=self.geom_in.asb_aircraft_geometry)

        # convert inputs to lists if necessary so they are iterable
        self.alpha_aircraft = self.__to_list(self.alpha_aircraft)
        self.beta_aircraft = self.__to_list(self.beta_aircraft)
        self.z_altitude = self.__to_list(self.z_altitude)
        self.mach_current = self.__to_list(self.mach_current)

        # retrieve geometric parameters
        self.S = self.flight_vehicle.airplane.s_ref
        self.b = self.flight_vehicle.airplane.b_ref
        self.c = self.flight_vehicle.airplane.c_ref

        # generate and write aircraft file
        operating_point = aerosandbox.OperatingPoint(
            atmosphere=aerosandbox.Atmosphere(altitude=0.0),
            velocity=0.0,
            alpha=0.0,
            beta=0.0,
            p=0.0,  # The roll rate about the x_b axis. [rad/sec]
            q=0.0,
            r=0.0,
        )
        analysis = aerosandbox.AVL(
            airplane=self.flight_vehicle.airplane,
            op_point=operating_point,
            verbose=False,
        )
        aircraft_file_path = f"{self.working_directory}/airplane.avl"
        analysis.write_avl(filepath=aircraft_file_path)

        # generate run data
        self.__create_run_data()

        # run AVL
        if self.n_run_cases <= self.max_avl_cases:
            self.__compute_avl_single()
        else:
            self.__compute_avl_multi()

        # output results
        if len(self.raw_parameters) == 1:
            self.CD = self.raw_parameters[0]["CD"]
            self.CL = self.raw_parameters[0]["CL"]
            self.CY = self.raw_parameters[0]["CY"]
            self.Cl = self.raw_parameters[0]["Cl"]
            self.Cm = self.raw_parameters[0]["Cm"]
            self.Cn = self.raw_parameters[0]["Cn"]
            self.L = self.raw_parameters[0]["L"]
            self.D = self.raw_parameters[0]["D"]
            self.Y = self.raw_parameters[0]["Y"]
            self.v_tas = self.raw_parameters[0]["v_tas"]
        else:
            self.CD = []
            self.CL = []
            self.CY = []
            self.Cl = []
            self.Cm = []
            self.Cn = []
            self.L = []
            self.D = []
            self.Y = []
            self.v_tas = []
            for key in self.raw_parameters:
                self.CD.append(self.raw_parameters[key]["CD"])
                self.CL.append(self.raw_parameters[key]["CL"])
                self.CY.append(self.raw_parameters[key]["CY"])
                self.Cl.append(self.raw_parameters[key]["Cl"])
                self.Cm.append(self.raw_parameters[key]["Cm"])
                self.Cn.append(self.raw_parameters[key]["Cn"])
                self.L.append(self.raw_parameters[key]["L"])
                self.D.append(self.raw_parameters[key]["D"])
                self.Y.append(self.raw_parameters[key]["Y"])
                self.v_tas.append(self.raw_parameters[key]["v_tas"])

        if self.debug is True:
            debug_message = (
                "Calculating flight point for "
                + f"altitude={self.z_altitude} "
                + f"speed={self.v_tas} "
                + f"alpha={self.alpha_aircraft} "
                + f"beta={self.beta_aircraft} "
                + f"q={self.raw_parameters[0]['q']:.3f}"
            )
            print(debug_message)


if __name__ == "__main__":
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long as airplane_geom,
    )
    import time
    import pandas
    import plotly.express as px

    aercal_avl = AeroCalculateAVL(
        "aercal_avl",
        asb_aircraft_geometry=airplane_geom(),
        debug=False,
    )
    alpha_list = list(numpy.linspace(-10, 10, 21))
    aercal_avl.alpha_aircraft = alpha_list
    aercal_avl.beta_aircraft = 0.0
    aercal_avl.z_altitude = [11000.0]
    aercal_avl.mach_current = [0.8]

    start_time = time.perf_counter()
    aercal_avl.run_drivers()
    end_time = time.perf_counter()
    total_time = end_time - start_time
    time_per_case = total_time / (
        len(alpha_list) * len(aercal_avl.z_altitude) * len(aercal_avl.mach_current)
    )

    result_df = pandas.DataFrame.from_dict(aercal_avl.raw_parameters).transpose()
    print(result_df)
    print(f"total time = {total_time:.2f}")
    print(f"time per run = {time_per_case:.4f}")

    cl_list_avl = []
    cd_list_avl = []

    for i in aercal_avl.raw_parameters:
        cl_list_avl.append(aercal_avl.raw_parameters[i]["CL"])
        cd_list_avl.append(aercal_avl.raw_parameters[i]["CD"])

    fig = px.line(
        x=cd_list_avl, y=cl_list_avl, title=f'{airplane_geom()["ac_name"]} CL vs CD'
    )

    fig.update_traces(showlegend=True)
    fig.show()
