import aerosandbox
import math
from amad.disciplines.aerodynamics.systems import BaseAeroCalculator
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane
from amad.disciplines.design.ports import AsbGeomPort
from amad.tools.atmosBADA import AtmosphereAMAD
import numpy as np


class AeroCalculateASB(BaseAeroCalculator):
    def setup(
        self,
        asb_aircraft_geometry: dict,
        atmos_model=AtmosphereAMAD(),
        init_altitude=0.0,
        option_optimization=True,
        option_method="AVL",
        debug=False,
    ):
        self.add_input(AsbGeomPort, "geom_in")
        self.add_inward("option_method", option_method)
        self.add_outward("asb_geometry_internal", asb_aircraft_geometry)

        # pre-generate ASB Airplane object
        generated_airplane = CreateAirplane(aero_geom=asb_aircraft_geometry)
        generated_airplane.generate()

        if option_method == "VLM":
            asb_method = aerosandbox.VortexLatticeMethod
        elif option_method == "AVL":
            asb_method = aerosandbox.AVL
        elif option_method == "LL":
            print(
                "WARNING: Lifting-line functionality is currently broken in AeroSandBox"
            )
            asb_method = aerosandbox.LiftingLine

        self.add_property("atmos_model", atmos_model)
        self.add_property("flight_vehicle", generated_airplane)
        self.add_property(
            "atmosphere_condition", aerosandbox.Atmosphere(altitude=init_altitude)
        )
        self.add_property("option_optimization", option_optimization)
        self.add_property("asb_method", asb_method)
        self.add_property("debug", debug)

        self.add_outward("raw_parameters", dtype=(dict, list, str, float, int))
        self.add_outward("v_tas")

        super().setup()

    def compute_aero(self):
        # calculate TAS for the given mach and altitude
        self.v_tas = self.atmos_model.mach2tas(alt=self.z_altitude, M=self.mach_current)

        self.alpha_aircraft = max(self.alpha_aircraft, -45.0)
        self.alpha_aircraft = min(self.alpha_aircraft, 45.0)

        if self.option_optimization is True and self.geom_in.asb_aircraft_geometry:
            # Update the flight vehicle geometry (useful when this is changing due to optimization)
            self.asb_geometry_internal = self.geom_in.asb_aircraft_geometry
            self.flight_vehicle.update(latest_geom=self.geom_in.asb_aircraft_geometry)

        # Update the atmosphere
        runtime_atmosphere_condition = aerosandbox.Atmosphere(altitude=self.z_altitude)

        operating_point = aerosandbox.OperatingPoint(
            atmosphere=runtime_atmosphere_condition,
            velocity=self.v_tas,
            alpha=self.alpha_aircraft,
            beta=self.beta_aircraft,
            p=(
                np.deg2rad(self.rate_roll)
            ),  # The roll rate about the x_b axis. [rad/sec]
            q=(
                np.deg2rad(self.rate_pitch)
            ),  # The pitch rate about the y_b axis. [rad/sec]
            r=(np.deg2rad(self.rate_yaw)),  # The yaw rate about the z_b axis. [rad/sec]
        )

        # collect intermediate params
        q = operating_point.dynamic_pressure()

        # calculate drag due to nacelle
        nacelle_c = 5.7e-3
        nacelle_k = 1.8e7
        nacelle_drag_unit = (
            self.asb_geometry_internal["d_nacelle"] * math.pi * q / nacelle_k
        ) + nacelle_c
        nacelle_drag = self.asb_geometry_internal["n_eng"] * nacelle_drag_unit
        self.flight_vehicle.airplane.analysis_specific_options[aerosandbox.AVL] = dict(
            profile_drag_coefficient=nacelle_drag
        )

        if self.option_method == "VLM":
            # specific parameters for VLM (unfortunately ASB doesn't accept **kwargs)
            analysis = self.asb_method(
                airplane=self.flight_vehicle.airplane,
                op_point=operating_point,
                verbose=False,
                spanwise_resolution=12,
                chordwise_resolution=12,
            )
        elif self.option_method == "AVL":
            analysis = self.asb_method(
                airplane=self.flight_vehicle.airplane,
                op_point=operating_point,
                verbose=False,
                working_directory="amad/disciplines/aerodynamics/temp/avl",
            )
        else:
            # Lifting Line method LL
            analysis = self.asb_method(
                airplane=self.flight_vehicle.airplane,
                op_point=operating_point,
                run_symmetric_if_possible=True,
                verbose=True,
                spanwise_resolution=12,
                spanwise_spacing="cosine",
                vortex_core_radius=1e-8,
            )
        try:
            asb_out = analysis.run()
        except RuntimeError:
            print("ERROR: Problem running aero analysis!")
            asb_out = {
                "CD": 0.0,
                "CL": 0.0,
                "CY": 0.0,
                "Cl": 0.0,
                "Cm": 0.0,
                "Cn": 0.0,
            }

        if self.debug is True:
            debug_message = (
                "Calculating flight point for "
                + f"altitude={runtime_atmosphere_condition.altitude:.0f} "
                + f"speed={self.v_tas:.3f} "
                + f"alpha={self.alpha_aircraft:.3f} "
                + f"beta={self.beta_aircraft:.3f} "
                + f"q={q:.3f}"
            )
            print(debug_message)

        # raw output from ASB in case it's needed
        self.raw_parameters = asb_out

        self.CD = asb_out["CD"]
        self.CL = asb_out["CL"]
        self.CY = asb_out["CY"]
        self.Cl = asb_out["Cl"]
        self.Cm = asb_out["Cm"]
        self.Cn = asb_out["Cn"]

        self.L = asb_out["L"]
        self.D = asb_out["D"]
        self.Y = asb_out["Y"]

        try:
            self.l = asb_out["l_b"]
            self.m = asb_out["m_b"]
            self.n = asb_out["n_b"]

        except KeyError:  # ASB uses different nomenclature for the VLM method >:[
            self.l = asb_out["l"]
            self.m = asb_out["m"]
            self.n = asb_out["n"]


if __name__ == "__main__":
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long as airplane_geom,
    )
    import plotly.express as px

    mach = 0.75
    z_alt = 10000.0

    list_methods = ["VLM", "AVL"]
    # TODO: 05MAY2022 Lifting Line still does not work, but development in progress on Git
    #  list_methods = ['LL']
    dict_res = {}
    for elm_aero in list_methods:
        dict_res[elm_aero] = {}
        sys_name = "aercal_" + elm_aero
        aercal = AeroCalculateASB(
            sys_name, asb_aircraft_geometry=airplane_geom(), option_method=elm_aero
        )
        aercal.mach_current = mach
        aercal.z_altitude = z_alt
        alpha_list = []
        cd_list = []
        cl_list = []
        d_list = []
        l_list = []

        for alpha in range(-100, 100, 5):
            alpha_list.append(alpha / 10)

            print(f"running alpha={alpha / 10}")

            aercal.alpha_aircraft = alpha / 10
            aercal.run_once()

            cd_list.append(aercal.CD)
            cl_list.append(aercal.CL)

            d_list.append(aercal.D)
            l_list.append(aercal.L)
        dict_res[elm_aero]["alpha_list"] = alpha_list
        dict_res[elm_aero]["cd_list"] = cd_list
        dict_res[elm_aero]["cl_list"] = cl_list
        dict_res[elm_aero]["d_list"] = d_list
        dict_res[elm_aero]["l_list"] = l_list

    # Plot per method CL/CD
    for idx, elm_aero in enumerate(list_methods):
        if idx == 0:
            fig = px.line(
                x=dict_res[elm_aero]["cd_list"],
                y=dict_res[elm_aero]["cl_list"],
                title=f'{airplane_geom()["ac_name"]} Drag vs Lift Coefficient',
                labels=dict(x="CD [-]", y="CL [-]"),
            )
        else:
            fig.add_scatter(
                x=dict_res[elm_aero]["cd_list"],
                y=dict_res[elm_aero]["cl_list"],
                mode="lines",
            )
        fig.data[idx].name = elm_aero
    fig.update_traces(showlegend=True)
    fig.show()

    # Plot per method CL/Alpha
    for idx, elm_aero in enumerate(list_methods):
        if idx == 0:
            fig = px.line(
                x=dict_res[elm_aero]["alpha_list"],
                y=dict_res[elm_aero]["cl_list"],
                title=f'{airplane_geom()["ac_name"]} Lift coefficient ',
                labels=dict(x=r"$\alpha$ [DEG]", y="CL [-]"),
            )
        else:
            fig.add_scatter(
                x=dict_res[elm_aero]["alpha_list"],
                y=dict_res[elm_aero]["cl_list"],
                mode="lines",
            )
        fig.data[idx].name = elm_aero

    fig.update_traces(showlegend=True)
    fig.show()
