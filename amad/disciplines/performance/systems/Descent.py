"""________________________________________________________________________________

                                   DESCENT MODULE
___________________________________________________________________________________"""
# This module takes in charge the computations for the climb segment.
# Descent.py
#
# Created:  Sep 2022, R. ROJAS CARDENAS
#

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

# Generic
import numpy as np
import math
from ambiance import Atmosphere

# CosApp
from cosapp.base import System

# Important to define a path directory for other modules either in the enviroment or with 'sys' method.

# Modules and tools
import amad.disciplines.powerplant.systems.enginePerfoMattingly as eP
import amad.tools.unit_conversion as uc
import amad.tools.atmosBADA
from amad.disciplines.performance.ports import SegmentPort
from amad.disciplines.performance.tools import MissionCallback
speedsclass = (
    amad.tools.atmosBADA.AtmosphereAMAD()
)  # Instantiate function to use in compute method.


class Descent_segment(System):
    """
    Vehicle Descent at a constant Throttle and constant CAS.

    Assumptions:
        1) The constant CAS is taken from the standard procedure described in the Airbus Getting to Grips.
        2) The guard to know if the AC shall descent with at a constant CAS or at IsoMach depends on the mode_variable "ISOMach" [Boolean type].

    REMARK !!!
    Do not confund ISOMach with the Inward variable "Iso_Mach" [Float type] that defines the Mach number to maintain constant."

        3) A
           It is into consideration a module whos variable throttle is not constrainted in position in order to define a constant rate of climb.

    Source: Airbus Getting to grips and SUAVE.
    """

    def setup(self):
        """
        `setup` method defines system structure
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
        self.add_inward("m0", np.zeros(1), unit="kg", desc="mass initial")
        self.add_inward("Iso_Mach", unit="", desc="Iso_Mach to maintain")
        self.add_inward("gamma", 0.0, unit="rad", desc="Flight path angle")
        self.add_inward("CAS", 0.0, unit="kt", desc="CAS in knots")
        self.add_inward("rho", 0.0, unit="kg/m**3", desc="Air density")
        self.add_inward(
            "deceleration_altitude",
            0.0,
            unit="m",
            desc="Altitude at which we want to decelerate",
        )
        self.add_inward(
            "Fin_appr_altitude",
            100.0,
            unit="m",
            desc="Altitude at which we want to perform the final approach",
        )
        self.add_inward("Lift", 0.0, unit="N", desc="Lift")
        self.add_inward("Drag", unit="N", desc="Drag")
        self.add_inward("CL", unit="", desc="Lift coefficient")
        self.add_inward("CD", unit="", desc=" Drag coefficient")
        self.add_inward("CS", np.zeros(1), unit="kg", desc="Fuel mass flow")
        self.add_inward("CAS_CrossOver", unit="m/s", desc="CAS at crossover altitude")
        self.add_inward("CRD", 0.0, unit="m/s", desc="Constant Rate of descent")
        self.add_inward("THR", unit="N", desc="Thrust")

        # Inwards A/C parameters
        self.add_inward("n_eng", 0, unit="", desc="Number of engines")
        self.add_inward("S", unit="m**2", desc="Surface")
        self.add_inward("alpha", 0.0, unit="deg", desc="Angle of Attack")
        self.add_inward(
            "Thau",
            0.0,
            unit="deg",
            desc="Angle between wing cord and AC longitudinal axis",
        )
        self.add_inward("Throttle", 0.5, unit="", desc="Throttle")

        # ------------------------------------------------------------------------------
        #   Outwards variables
        # ------------------------------------------------------------------------------
        # segment status parameters
        self.add_outward("mass", unit="kg", desc="Aircraft mass")
        self.add_outward("TAS", unit="m/s", desc="True Airspeed Magnitude")
        self.add_outward("Mach", unit="", desc="Mach number")
        self.add_outward("SFC", unit="kg/(s*N)", desc="Specific Fuel Consumption")
        self.add_outward("Altitude", unit="ft", desc="Altitude in ft")
        self.add_outward("Distance", unit="NM", desc="Distance in NM")
        self.add_outward(
            "theta",
            unit="deg",
            desc="Aircraft attitude (body angle in AVL), in deg to export data",
        )
        self.add_outward("RC", unit="ft/min", desc="Rate of Climb/descent")

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
        # self.enginePerfo.rating_eng = 'MCRZ' # Input rating for Mattingly Module

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
        self.add_unknown("Throttle").add_equation("in_p.TAS_speed[2] == CRD")
        self.add_unknown("alpha").add_equation(
            "Lift == mass*g*cos(gamma)- THR*sin(alpha*pi/180+Thau*pi/180)"
        )

        # ------------------------------------------------------------------------------
        #   Events
        # ------------------------------------------------------------------------------
        self.add_event(
            "Final_approach_altitude_reached",
            trigger="in_p.position[2] == Fin_appr_altitude",
            final=True,
        )  # Event finishes the simulation when the altitude to begin the final approach is reached.
        self.add_event(
            "Deceleration_altitude_reached",
            trigger="in_p.position[2] == deceleration_altitude",
            final=True,
        )  # Event finishes the simulation when the altitude to begin the deceleration is reached.
        self.add_event(
            "Crossover_altitude", trigger="CAS_CrossOver >= 154.3"
        )  # Event detects the moment at which the A/C exits the CrossOver altitude.
        #    Mach == Iso_Mach
        self.add_inward_modevar(
            "IsoMach", True
        )  # Variable that monitors if condition to compute by IsoMach is activated.

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
        atm = Atmosphere(
            self.in_p.position[2]
        )  # Input of Aircraft z-position (altitude) for  Atmosphere tool.
        self.rho = atm.density  # Air density at Aircraft position [kg/m^3].

        """ IsoMach guard verification  """

        if self.IsoMach is True:
            self.Mach = self.Iso_Mach
            self.TAS = speedsclass.mach2tas(
                self.Mach, self.in_p.position[2]
            )  # convertion from mach to TAS
            self.CAS_CrossOver = speedsclass.tas2cas(
                self.TAS, self.in_p.position[2]
            )  # convertion from mach to TAS
            self.CAS = uc.ms2kt(self.CAS_CrossOver)

        elif self.IsoMach is False:
            self.TAS = speedsclass.cas2tas(
                uc.kt2ms(self.CAS), self.in_p.position[2]
            )  # convertion from CAS to TAS
            self.Mach = speedsclass.tas2mach(
                self.TAS, self.in_p.position[2]
            )  # convertion from TAS to Mach
            # self.enginePerfo.rating_eng = 'IDLE' # Input rating for Mattingly Module

        """ Thrust computation  """
        self.enginePerfo.z_altitude = self.in_p.position[
            2
        ]  # Input altitude for Mattingly Module
        self.enginePerfo.mach_current = self.Mach  # Input Mach for Mattingly Module
        self.SFC = self.enginePerfo.SFC  # Output SFC from Mattingly Module.
        # self.THR = self.n_eng*self.enginePerfo.THR_Mattingly # Output Thrust from Mattingly Module, input from geometry module.
        self.THR = (
            self.n_eng * self.enginePerfo.THR_Mattingly_max * self.Throttle
        )  # Output Thrust from Mattingly Module, input from geometry module.

        """Fuel consumption computation"""
        self.CS = np.array([self.SFC * self.THR])  # Consumtion in [kg/s]

        """ Aerodynamic equations """
        pt = np.array(
            [self.alpha, self.Mach, self.in_p.position[2]]
        )  # Aircraft parameters at a point to input for interpolation.

        # CL, CD and Drag evaluation.
        self.CL = self.CLAeroIt(pt)
        self.CD = self.CDAeroIt(pt)
        self.Drag = self.DAeroIt(pt)
        #         self.Drag=0.5*self.rho*self.S*self.TAS**2*self.CD

        """ Static equilibrium computation"""
        self.mass = (
            self.m0 - self.mass_variation
        )  # A/C mass is the initial mass minus the mass variation due to fuel fuel flow.
        # Lift needs to be computed since the variable is also used in the equilibrium equation at the constraints definition.
        self.Lift = 0.5 * self.rho * self.S * self.TAS**2 * self.CL
        # self.Lift = self.mass*self.g*math.cos(self.gamma)- self.THR*math.sin(self.alpha*math.pi/180+self.Thau*math.pi/180)

        # Flight path angle computation depending on alpha and thau.
        self.gamma = math.asin(
            (
                self.THR
                * math.cos(self.alpha * math.pi / 180 + self.Thau * math.pi / 180)
                - self.Drag
            )
            / (self.mass[0] * self.g)
        )
        self.theta = math.degrees(self.gamma) + self.alpha

        # Speed Definition
        Vx = float(self.TAS * math.cos(self.gamma))
        Vy = 0.0  # No lateral flight or wind taked into account for this version.
        Vz = float(self.TAS * math.sin(self.gamma))
        self.in_p.TAS_speed = np.array([Vx, Vy, Vz])

        """ Outputs definition """
        # All the computations are done changing the input variables. Therefore, the outputs are defined as
        self.out_p.position = self.in_p.position
        self.out_p.fuel_mass = self.mass_variation
        self.out_p.TAS_speed = self.in_p.TAS_speed

        # Outwards defined for data visualization in plot
        self.Distance = uc.m2nm(self.out_p.position[0])
        self.Altitude = uc.m2ft(self.out_p.position[2])
        self.RC = uc.ms2ftm(float(Vz))

        self.mission_callback.callback({"segment": "Descent", "data": self.out_p})

    def transition(self):
        """
        Transition the current state of the object.

        If the crossover altitude is present, set the IsoMach attribute to False.

        Parameters
        ----------
        self : object
            The current object instance.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        if self.Crossover_altitude.present:
            self.IsoMach = False


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

    s1 = Descent_segment(name="s1")
    s1.CLAeroIt = CLAeroIt
    s1.CDAeroIt = CDAeroIt
    s1.DAeroIt = DAeroIt

    driver = s1.add_driver(RungeKutta())
    solver = driver.add_child(NonLinearSolver("solver"))

    driver.time_interval = (0, 10000)
    driver.dt = 2
    Data_to_record = [
        "Altitude",
        "CD",
        "CL",
        "Distance",
        "Drag",
        "Lift",
        "Mach",
        "RD",
        "TAS",
        "CAS",
        "THR",
        "alpha",
        "gamma",
        "theta",
        "Throttle",
        "mass",
        "out_p.fuel_mass",
        "time",
    ]

    # Add a recorder to capture time evolution in a dataframe
    driver.add_recorder(
        DataFrameRecorder(
            includes=Data_to_record,
        ),
        period=10,
    )

    # Initial conditions
    p_0 = np.array([0.0, 0.0, 10668.0])  # Position [m]
    CS_0 = np.array([0.0])  # Fuel consumption rate [kg/s]
    m_0 = np.array([68000])  # mass [kg]

    # Define a simulation scenario
    driver.set_scenario(
        init={"CS": CS_0, "in_p.position": p_0, "g": 9.81, "m0": m_0},  #
        values={
            "CAS": 300,  # [kt]
            "Iso_Mach": 0.78,
            #             'Fin_appr_altitude':457,
            "deceleration_altitude": 3048,  # m
            "S": 134,  # [m^2]
            "n_eng": 2,
            "CRD": -10,
            #             'IsoMach' : False
        },
    )

    s1.run_drivers()
    data = driver.recorder.export_data()
