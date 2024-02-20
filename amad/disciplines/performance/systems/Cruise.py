"""________________________________________________________________________________

                                   CRUISE MODULE
___________________________________________________________________________________"""
# This module takes in charge the computations for the climb segment.
# Cruise.py
#
# Created:  Sep 2022, R. ROJAS CARDENAS
#

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

# Generic
import numpy as np
import math

# CosApp
from cosapp.base import System

# Important to define a path directory for other modules either in the enviroment or with 'sys' method.

#  Modules and tools
import amad.disciplines.powerplant.systems.enginePerfoMattingly as eP
import amad.tools.unit_conversion as uc
import amad.tools.atmosBADA as atmos
from amad.disciplines.performance.ports import SegmentPort
from amad.disciplines.performance.tools import MissionCallback

speedsclass = atmos.AtmosphereAMAD()  # Instantiate function to use in compute method.


class Cruise_segment(System):
    """
    Vehicle Cruise at a constant Throttle and constant Mach.

    Assumptions:
    1) The constant Mach number is taken from airbus getting into grips reports.
    2) The VC cruise limit speed is not considered in this version since the
       "structure" discipline is not yet developed in order to know the aero-elasticity limitations.
    3) TAS input port correction in values since the A/C shall not change its position on the Y or Z earth axis.
    Source: Airbus Getting to grips and SUAVE.
    """

    def setup(self):
        """
        `setup` method defines system structure.
        """

        # ------------------------------------------------------------------------------
        #   Input ports
        # ------------------------------------------------------------------------------
        # Port including the AC TAS(V_x,V_y_V_z), position(x,y,z) and mass.
        # It allows to initialize these conditions or to connect to a previous segment.
        # Inputs from other flight segments.
        self.add_input(SegmentPort, "in_p")

        # ------------------------------------------------------------------------------
        #   Inward variables
        # ------------------------------------------------------------------------------
        # Constants
        self.add_inward("g", unit="m/s**2", desc="Gravity")

        # Mission state conditions
        self.add_inward(
            "m0", np.zeros(1), unit="kg", desc="Initiel mass for the segment"
        )
        self.add_inward("CAS", unit="kt", desc="CAS in knots")
        self.add_inward("Mach", 0.0, unit="", desc="Mach number cruise")
        self.add_inward("gamma", 0.0, unit="rad", desc="CAS in knots")
        self.add_inward(
            "Cruise_pos_init",
            np.zeros(3),
            unit="m",
            desc="Position on which the cruise starts",
        )
        self.add_inward(
            "Cruise_distance_target",
            1000.0,
            unit="m",
            desc="Position on which the cruise end",
        )
        self.add_inward("rho", unit="kg/m**3", desc="Air density")
        self.add_inward("Lift", 0.0, unit="N", desc="Lift Force")
        self.add_inward("Drag", 0.0, unit="N", desc="Drag")
        self.add_inward("CL", unit="", desc="Lift coefficient")
        self.add_inward("CD", unit="", desc=" Drag coefficient")
        self.add_inward(
            "CS", np.zeros(1), unit="kg", desc="Fuel mass flow for combution"
        )

        # Inwards A/C parameters
        self.add_inward("n_eng", 0, unit="", desc="Number of engines")
        self.add_inward("S", unit="m**2", desc="Aing Surface of reference")
        self.add_inward(
            "alpha",
            0.0,
            unit="deg",
            desc="Angle of Attack in degrees due to results from AVL, computed in radians",
        )
        self.add_inward(
            "Thau",
            2.2,
            unit="deg",
            desc="Angle between wing chord and AC longitudinal axis",
        )

        # ------------------------------------------------------------------------------
        #   Outwards variables
        # ------------------------------------------------------------------------------
        # segment status parameters
        self.add_outward("mass", unit="kg", desc="Aircraft mass for a time instant")
        self.add_outward("SFC", unit="kg/(s*N)", desc="Specific Fuel Consumption")
        self.add_outward("THR", unit="N", desc="Cruise Thrust")
        self.add_outward(
            "Cruise_distance",
            0.0,
            unit="m",
            desc="Cruise_distance added from the descent point calculation",
        )  # Computed variable to assess when the AC over-passes the distance limit.
        self.add_outward("TAS", unit="m/s", desc="True Airspeed Magnitude")
        self.add_outward("Altitude", unit="ft", desc="Altitude in ft")
        self.add_outward("Distance", unit="NM", desc="Distance in NM")
        self.add_outward("RC", unit="ft/min", desc="Rate of climb")
        self.add_outward(
            "theta",
            unit="deg",
            desc="Aircraft attitude (body angle in AVL), in deg to export data",
        )

        # ------------------------------------------------------------------------------
        #   Output ports
        # ------------------------------------------------------------------------------
        # Port including the AC TAS(V_x,V_y_V_z), position(x,y,z) and mass.
        # Allows to connect to other flight segments.
        self.add_output(SegmentPort, "out_p")

        # ------------------------------------------------------------------------------
        #   Child systems
        # ------------------------------------------------------------------------------
        # Syub-systems definition (Diciplines' Modules and Bricks integration)
        # Here the only explicit sub-system comes from the propulsion module using the Mettingly method.
        self.add_child(
            eP.EnginePerfoMattingly(
                name="enginePerfo", altitude=self.in_p.position[2], dISA=0
            )
        )

        # ------------------------------------------------------------------------------
        #   Transient variables
        # ------------------------------------------------------------------------------
        # It declares inputs and inwards as time dependent variables with respect to other parameters.
        # Helpful to monitor gradients or rate of change in a very simplyfied way.
        self.add_transient(
            "in_p.position", der="in_p.TAS_speed"
        )  # The speed is the position derivative over the time.
        self.add_transient(
            "mass_variation", der="CS"
        )  # The fuel flow is the mass derivative over the time.

        # ------------------------------------------------------------------------------
        #   Off-design constraints
        # ------------------------------------------------------------------------------
        # Constraints to respect during computation.
        # In this case, the constraint is defined by the equilibrium of forces in the Z axis (equation)
        # In order to meet such constraint the AOA (alpha) is left as a free variable (Unknown)
        # Since the Aero_CSV file that contains the results brings alpha in degrees the conversion to radias is made manually in the equation.
        self.add_unknown("alpha").add_equation(
            "Lift == mass*g - THR*sin(Thau*pi/180+alpha*pi/180)"
        )

        # ------------------------------------------------------------------------------
        #   Events
        # ------------------------------------------------------------------------------
        self.add_event(
            "Cruise_distance_reached",
            trigger="Cruise_distance == Cruise_distance_target",
            final=True,
        )

        # Event to detect the moment at which the A/C passes the limit distance.
        # The previous event is needed to calculate the optimum point at which the A/C shall descent.

        # ------------------------------------------------------------------------------
        #   AERO Interpolation functions
        # ------------------------------------------------------------------------------
        # Definition of the function variables that will contain the aerodynamic interpolation.
        self.add_inward("CLAeroIt", None)
        self.add_inward("CDAeroIt", None)
        self.add_inward("DAeroIt", None)

        #   Callback function to replace `print` statements
        mc = MissionCallback()
        self.add_property("mission_callback", mc)

    def compute(self):
        """
        `compute` method defines what the system does
        """

        atm = atmos.AtmosphereAMAD(
            alt=self.in_p.position[2]
        )  # geometric altitudes by default
        self.rho = atm.airdens_kgpm3(alt=self.in_p.position[2])  # [kg/m^3]

        # Local correction for inputs since the A/C shall not change its position on the Y or Z earth axis.
        self.in_p.TAS_speed[1] = 0
        self.in_p.TAS_speed[2] = 0
        self.Mach = speedsclass.tas2mach(
            self.in_p.TAS_speed[0], self.in_p.position[2]
        )  # convertion from TAS to Mach
        self.Mach = speedsclass.tas2mach(
            self.in_p.TAS_speed[0], self.in_p.position[2]
        )  # convertion from TAS to Mach

        """ Aerodynamic equations """
        pt = np.array(
            [self.alpha, self.Mach, self.in_p.position[2]]
        )  # Aircraft parameters at a point to input for interpolation.

        # CL, CD and Drag evaluation.
        self.CL = self.CLAeroIt(pt)
        self.CD = self.CDAeroIt(pt)
        #         self.Drag = self.DAeroIt(pt)

        # Lift needs to be computed since the variable is also used in the equilibrium equation for at constraints definition.
        self.Lift = 0.5 * self.rho * self.S * self.TAS**2 * self.CL
        self.Drag = 0.5 * self.rho * self.S * self.TAS**2 * self.CD

        # Lift needs to be computed since the variable is also used in the equilibrium equation at the constraints definition.
        self.Lift = 0.5 * self.rho * self.S * self.TAS**2 * self.CL

        """Static equilibrium computation"""
        self.mass = (
            self.m0 - self.mass_variation
        )  # A/C mass is the initial mass minus the mass variation due to fuel fuel flow.
        self.THR = self.Drag / math.cos(
            math.radians(self.Thau + self.alpha)
        )  # Longitudinal axis equilibrium.
        self.theta = self.alpha

        """Fuel consumption computation"""
        self.enginePerfo.z_altitude = self.in_p.position[
            2
        ]  # Input altitude for Mattingly Module
        self.enginePerfo.mach_current = self.Mach  # Input Mach for Mattingly Module
        self.SFC = self.enginePerfo.SFC  # Output SFC from Mattingly Module.
        self.CS = (
            self.SFC * self.THR
        )  # Output Thrust from Mattingly Module, taking into consideration 2 engines producing the required thrust.

        """Cruise distance computation"""
        self.Cruise_distance = (
            self.in_p.position[0] - self.Cruise_pos_init[0]
        )  # The cruise distance to assess if the descent point is the actual position minus the initial position.

        """ Outputs definition"""
        # All the computations are done changing the input variables. Therefore, the outputs are defined as
        self.out_p.position = self.in_p.position
        self.out_p.fuel_mass = self.mass_variation
        self.out_p.TAS_speed = self.in_p.TAS_speed

        # Outwards defined for data visualization in plot
        self.Distance = uc.m2nm(self.out_p.position[0])
        self.Altitude = uc.m2ft(self.out_p.position[2])
        self.RC = uc.ms2ftm(self.out_p.TAS_speed[2])
        self.TAS = np.linalg.norm(
            self.in_p.TAS_speed
        )  # Obtaining the norm from speed vector
        self.CAS = uc.ms2kt(speedsclass.tas2cas(self.TAS, self.out_p.position[2]))

        self.mission_callback.callback({"segment": "Cruise", "data": self.out_p})


if __name__ == "__main__":
    from cosapp.drivers import RungeKutta, NonLinearSolver
    from cosapp.recorders import DataFrameRecorder
    import amad.disciplines.aerodynamics.tools.createAeroInterpolationCSV as aeroInterp  # Tool to create the function to Interpolate.

    """Aerodynamic inputs"""
    # Directory to the Aero results in CSV in order to build the interpolation functions.
    Aero_CSV = r"amad/disciplines/aerodynamics/tools/Results/aero_results.csv"
    # Ranges to create CL and CD interpolation functions from AVL Aero Results (CSV file).
    # REMARK: To maintain units, array and split format to the values must correlate to the CSV file results.
    alpha_list = list(
        np.arange(-6.0, 10.0, 2)
    )  # unit='deg', desc='Range of AOA to create functions')
    mach_list = list(
        np.arange(0.0, 0.84, 0.04)
    )  # unit='', desc='Range of Mach to create functions')
    altitude_list = list(
        np.arange(0.0, 13000, 500)
    )  # unit='m', desc='Range of altitude to create functions')

    # Creation of functions for the aerodynamic coefficients interpolation.
    CLAeroIt = aeroInterp.CL_Interpolation_function(
        alpha_list, mach_list, altitude_list, Aero_CSV
    )
    CDAeroIt = aeroInterp.CD_Interpolation_function(
        alpha_list, mach_list, altitude_list, Aero_CSV
    )
    DAeroIt = aeroInterp.Drag_Interpolation_function(
        alpha_list, mach_list, altitude_list, Aero_CSV
    )

    s1 = Cruise_segment(name="s1")
    s1.CLAeroIt = CLAeroIt
    s1.CDAeroIt = CDAeroIt
    s1.DAeroIt = DAeroIt
    ###
    ###
    driver = s1.add_driver(RungeKutta())
    solver = driver.add_child(NonLinearSolver("solver"))
    driver.time_interval = (0, 10000)
    driver.dt = 10
    Data_to_record = [
        "Altitude",
        "CD",
        "CL",
        "Distance",
        "Drag",
        "Lift",
        "Mach",
        "RC",
        "TAS",
        "CAS",
        "THR",
        "alpha",
        "gamma",
        "mass",
        "out_p.fuel_mass",
        "time",
    ]

    # Add a recorder to capture time evolution in a dataframe
    driver.add_recorder(
        DataFrameRecorder(
            includes=Data_to_record,
        ),
        period=50,
    )

    # Initial conditions
    p_0 = np.array([0.0, 0.0, 12000.0])  # Position
    CS_0 = np.array([0.0])  # Fuel consumption
    v_0 = np.array([140.0, 0.0, 0.0])  # TAS
    m_0 = np.array([0.0])  # mass
    #     pt_0=np.array([0.0,0.72,10000]) #point to initialize interpolation

    # Define a simulation scenario
    driver.set_scenario(
        init={"CS": CS_0, "in_p.position": p_0, "in_p.TAS_speed": v_0, "m0": m_0},  #
        values={
            "Cruise_distance_target": 100000,
        },
    )

    s1.run_drivers()
    data = driver.recorder.export_data()
