"""________________________________________________________________________________

                                   DECELERATION MODULE
___________________________________________________________________________________"""
# This module takes in charge the computations for the transition between segments
# in case of deceleration.
# Decceleration.py
#
# Created:  Sep 2022, R. ROJAS CARDENAS
#

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

# Genericimport numpy as np
import numpy as np

# CosApp
from cosapp.base import System

# Important to define a path directory for other modules either in the enviroment or with 'sys' method.

# Modules and tools
import amad.disciplines.powerplant.systems.enginePerfoMattingly as eP
import amad.tools.unit_conversion as uc
import amad.tools.atmosBADA as atmos
from amad.disciplines.performance.tools import MissionCallback
from amad.disciplines.performance.ports import SegmentPort
speedsclass = atmos.AtmosphereAMAD()  # Instantiate function to use in compute method.


class Decelerate(System):
    """
    Vehicle decelerates at a constant rate between two airspeeds.

    Assumptions:
    1) The guard to know if the AC shall decelerate REGARDGING THE CAS [kt] OR THE MACH NUMBER relies
    on the following logic.
    Both `Mach_cruise` and `CAS_target` inward variables have an initial value of 0.0.
    Thus, if during the instantiation of this brick the `Mach_cruise` or `CAS_target` value is changed then do.
    For instance, if any of the values is different to zero, it means that this brick shall accelerate to the target value in
    the corresponding speed.

    REMARK !!!
    IF NONE MODIFICATION IS MADE OR BOTH MACH AND CAS ARE CHANGED THEN POSSIBLE ERRORS IN COMPUTATION MIGHT ARISE...

    2) Local correction for TAS input since the A/C shall not change its position on the Y or Z earth axis.

    Source:
    None
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
        self.add_input(SegmentPort, "in_p")

        # ------------------------------------------------------------------------------
        #   Inward variables
        # ------------------------------------------------------------------------------
        # Constants
        self.add_inward("g", unit="m/s**2", desc="Gravity")

        # Mission state conditions
        self.add_inward("m0", 0.0, unit="kg", desc="Initial mass")
        self.add_inward(
            "CAS_target", 0.0, unit="kt", desc="CAS target for acceleration"
        )
        self.add_inward("rho", 0.0, unit="kg/m**3", desc="Air density")
        self.add_inward("vf", unit="m/s", desc="Target of final AC speed")
        self.add_inward(
            "Iso_Mach", 0.0, unit="", desc="In case of descent Target of Iso_Mach"
        )
        self.add_inward("Mach", 0.0, unit="", desc="Mach")
        self.add_inward("THR", 0.0, unit="N", desc="Thrust")
        self.add_inward("Lift", 0.0, unit="N", desc="Lift Force")
        self.add_inward("Drag", 0.0, unit="N", desc="Drag Force")
        self.add_inward("CL", unit="", desc="Lift coefficient")
        self.add_inward("CD", unit="", desc="Drag coefficient")
        self.add_inward("alpha", 0.0, unit="deg", desc="Angle of Attack")
        self.add_inward(
            "CS", np.zeros(1), unit="kg/s", desc="Mass fuel flow (Fuel consumption)"
        )

        # A/C parameters
        self.add_inward("n_eng", 0, unit="", desc="Number of engines")
        self.add_inward("S", unit="m**2", desc="wing surface")
        self.add_inward(
            "Thau",
            2.2,
            unit="deg",
            desc="Angle between wing cord and AC longitudinal axis",
        )

        # Outwards
        self.add_outward("mass", unit="kg", desc="Aircraft Mass")
        self.add_outward("a", np.zeros(3), desc="AC acceleration")
        self.add_outward("TAS", unit="m/s", desc="True Airspeed Magnitude")
        self.add_outward("CAS", unit="kt", desc="CAS in knots")
        self.add_outward("Altitude", unit="ft", desc="Altitude in ft")
        self.add_outward("Distance", unit="NM", desc="Distance in NM")
        self.add_outward("RC", unit="ft/min", desc="Rate of climb")
        self.add_inward("SFC", unit="kg/(s*N)", desc="Specific Fuel Consumption")

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
        )  # The speed is the time-position derivative.
        self.add_transient(
            "in_p.TAS_speed", der="a"
        )  # The acceleration is the speed derivative over the time.
        self.add_transient(
            "mass_variation", der="CS"
        )  # The fuel flow is the time-mass derivative.

        # ------------------------------------------------------------------------------
        #   Off-design constraints
        # ------------------------------------------------------------------------------
        # Constraints to respect during computation.
        # In this case, the constraint is defined by the equilibrium of forces in the Z axis (equation)
        # In order to meet such constraint the AOA (alpha) is left as a free variable (Unknown)
        # Since the Aero_CSV file that contains the results brings alpha in degrees the conversion to radias is made manually in the equation.
        self.add_unknown("alpha").add_equation(
            "Lift == mass*g - THR*sin(Thau*pi/180 + alpha*pi/180)"
        )

        # ------------------------------------------------------------------------------
        #   Events
        # ------------------------------------------------------------------------------
        # Event finishes the computations when the target speed (vf) is reached.
        self.add_event(
            "speed_arrived", trigger="in_p.TAS_speed[0] <= vf", final=True
        )  # event to finish simulation when the target speed is reached.

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
        # print('dec')
        """
        compute method defines what the system does
        """

        atm = atmos.AtmosphereAMAD(
            alt=self.in_p.position[2]
        )  # Input of Aircraft z-position (altitude) for  Atmosphere module.
        self.rho = atm.airdens_kgpm3(
            alt=self.in_p.position[2]
        )  # Air density at Aircraft position [kg/m^3].

        """ Current aircraft speed """

        # Local correction for inputs since the A/C shall not change its position on the Y or Z earth axis.
        self.in_p.TAS_speed[1] = 0
        self.in_p.TAS_speed[2] = 0
        self.TAS = np.linalg.norm(self.in_p.TAS_speed)

        """ Speed guard verification """
        if self.Iso_Mach != 0.0:
            self.Mach = speedsclass.tas2mach(
                (self.TAS), self.in_p.position[2]
            )  # convertion from TAS to Mach
            self.vf = speedsclass.mach2tas(
                self.Iso_Mach, self.in_p.position[2]
            )  # Final speed vf defined in TAS [m/s] by the target Mach speed.
        elif self.CAS_target != 0.0:
            self.vf = speedsclass.cas2tas(
                uc.kt2ms(self.CAS_target), self.in_p.position[2]
            )  # Final speed vf defined in TAS [m/s] by the target CAS speed with a 2% error correction for CAS.
            self.Mach = speedsclass.tas2mach(
                (self.TAS), self.in_p.position[2]
            )  # convertion from TAS to Mach

        """ Aerodynamic equations """
        pt = np.array(
            [self.alpha, self.Mach, self.in_p.position[2]]
        )  # Aircraft parameters at a point to input for interpolation.

        # CL, CD and Drag evaluation.

        self.CL = self.CLAeroIt(pt)
        self.CD = self.CDAeroIt(
            pt
        )  # Interpolated CD is greater than those expected from a B737.
        #         self.Drag = self.DAeroIt(pt) # Interpolated Drag is much lower than those expected from a B737.

        # Lift needs to be computed since the variable is also used in the equilibrium equation for at constraints definition.
        self.Lift = 0.5 * self.rho * self.S * self.TAS**2 * self.CL
        self.Drag = 0.5 * self.rho * self.S * self.TAS**2 * self.CD

        """ Thrust computation  """
        self.enginePerfo.z_altitude = self.in_p.position[
            2
        ]  # Input altitude for Mattingly Module
        self.enginePerfo.mach_current = self.Mach  # Input Mach for Mattingly Module
        self.enginePerfo.rating_eng = "IDLE"  # Input rating for Mattingly Module
        self.SFC = self.enginePerfo.SFC  # Output SFC from Mattingly Module.
        self.THR = (
            self.n_eng * self.enginePerfo.THR_Mattingly
        )  # Output Thrust from Mattingly Module, taking into consideration 2 engines.

        """Fuel consumption computation"""
        self.CS = np.array(
            [self.SFC * self.THR]
        )  # The fuel mass consumption per second is defined as the SFC times the produced Thrust.

        """Static equilibrium computation"""
        self.mass = (
            self.m0 - self.mass_variation
        )  # A/C current mass is the initial mass minus the mass variation due to fuel flow.
        self.a[0] = np.array(
            [(self.THR - self.Drag) / self.mass]
        )  # Acceleration is the equilibrium of forces divided by the A/C mass.

        """ Outputs definition"""
        # All the computations are done changing the input variables. Therefore, the outputs are defined as
        self.out_p.position = self.in_p.position
        self.out_p.TAS_speed = self.in_p.TAS_speed
        self.out_p.fuel_mass = self.mass_variation

        # Outwards defined for data visualization in plot
        self.Distance = uc.m2nm(self.out_p.position[0])
        self.Altitude = uc.m2ft(self.out_p.position[2])
        self.RC = uc.ms2ftm(self.out_p.TAS_speed[2])
        self.CAS = uc.ms2kt(speedsclass.tas2cas(self.TAS, self.in_p.position[2]))

        self.mission_callback.callback({"segment": "Deceleration", "data": self.out_p})


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

    s1 = Decelerate(name="s1")
    s1.CLAeroIt = CLAeroIt
    s1.CDAeroIt = CDAeroIt
    s1.DAeroIt = DAeroIt
    ###
    driver = s1.add_driver(RungeKutta())
    solver = driver.add_child(NonLinearSolver("solver"), tol=0.01, it=400)
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
        period=20,
    )

    # Initial conditions
    p_0 = np.array([0.0, 0.0, 12000.0])  # Position [m]
    CS_0 = np.array([0.0])  # Fuel consumption [kg/s]
    v_0 = np.array([340.0, 0.0, 6.0])  # TAS
    m_0 = np.array([68000])  # mass

    # Define a simulation scenario
    driver.set_scenario(
        init={"CS": CS_0, "in_p.position": p_0, "in_p.TAS_speed": v_0, "m0": m_0},  #
        values={"g": 9.81, "S": 124, "n_eng": 2, "Iso_Mach": 0.75},  # [m/s^2]  # [m^2]
    )

    s1.run_drivers()
    data = driver.recorder.export_data()
