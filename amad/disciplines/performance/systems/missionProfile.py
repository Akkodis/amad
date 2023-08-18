"""________________________________________________________________________________

                                   MISSION PROFILE MODULE 
___________________________________________________________________________________"""
## This module takes in charge of the system architecture definition, in this case it is
#  the mission to follow.
#  The climb and descent profiles exposed at the book "Airbus: Getting to grips into
#  aircraft performance" are taken as example.
## missionProfile.py
##
# Created:  Sep 2022, R. ROJAS CARDENAS
#

### ----------------------------------------------------------------------
###   Imports
### ----------------------------------------------------------------------

## Generic
from multiprocessing import Event
from unicodedata import name
import numpy as np

# from operator import attrgetter
# from ambiance import Atmosphere

## CosApp
from cosapp.base import System
from cosapp.drivers import RungeKutta, NonLinearSolver
from cosapp.recorders import DataFrameRecorder

# Important to define a path directory for other modules either in the enviroment or with 'sys' method.

## Modules and tools
import amad.tools.atmosBADA as atmos

speedsclass = atmos.AtmosphereAMAD()
import amad.tools.unit_conversion as uc

# import amad.disciplines.aerodynamics.tools.createAeroInterpolationCSV as aeroInterp
# from amad.disciplines.powerplant.systems import enginePerfoMattingly as eP
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane
from amad.disciplines.systems.fuel.systems.fuelVolume import FuelVolume_Weight
from amad.disciplines.performance.systems import (
    Acceleration as Acc,
    Climb as Clb,
    Cruise as Cru,
    Deceleration as Dec,
    Descent as Des,
)

# Import Ports from AMAD.
from amad.disciplines.performance.ports import SegmentPort

from amad.disciplines.performance.tools.missionCallback import empty_callback


class mission_profile(System):
    """This profile takes into account the high speed performance:
    - Climb , Acceleration, Cruise, Deceleration and Descent.

        Assumptions:
        1) In between the final climb and the cruise segment a possible acceleration in Mach number is taken into account.
        2) In between the first descent and the cruise segment a possible decceleration in Mach number is taken into account.
        3) Assumption 1 and 2 are managed by an "if" guard, however a mission can be hard-coded. It has been decided to code it
            as it is to show the flexibility of CosApp tool.

        REMARK !!!

    """

    def __init__(self, *args, **kwargs):
        self.flightSegments = (
            []
        )  # Used to save all the flight Segments required during the mission.
        self.drx = {}  # Dictionary to save the drivers added to each subsystem.
        self.data = (
            []
        )  # List to save the dataframes containing the resultsfrom each simulation.
        self.Data_to_record = [
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
            "rho" "THR",
            "alpha",
            "gamma",
            "theta",
            "mass",
            "out_p.fuel_mass",
            "SFC",
            "time",
            "Segment",
        ]  # Information of interest to save during the simulation.

        super().__init__(
            *args, **kwargs
        )  # Calls all arguments in init from the superior class 'system'.

    def setup(self, asb_aircraft_geometry: dict, mission_callback=empty_callback):
        ### ----------------------------------------------------------------------
        ### Flight_vehicle generation
        ### ----------------------------------------------------------------------

        # Pre-generate ASB Airplane object
        generated_airplane = CreateAirplane(
            aero_geom=asb_aircraft_geometry, generate_airfoil_polars=False
        )
        generated_airplane.generate()
        self.add_property("flight_vehicle", generated_airplane)

        # Inwards
        self.add_inward(
            "W_f", 0.0, unit="kg", desc="Max fuel mass capacity"
        )  # Variable to connect to the Aircraft Geometry module and assess the A/C capability to perform the mission profile in terms of fuel volume available vs needed.
        # Outwards
        self.add_outward(
            "Simulation_W_f",
            0.0,
            unit="kg",
            desc="Total fuel mass needed for the mission",
        )

        ### ----------------------------------------------------------------------
        ### Mission profile definition using segment modules (children systems)
        ### ----------------------------------------------------------------------

        # The computation of the mission follows the order of the segments definition.
        self.add_child(
            Clb.Climb_segment(name="Climb_segment_1"),
            pulling={
                "RC_ceiling": "RC_ceiling",
                "acceleration_altitude": "acceleration_altitude",
                "cruise_altitude": "cruise_altitude",
                "S": "S",
                "g": "g",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Acc.Accelerate(name="Accelerate"),
            pulling={
                "g": "g",
                "CD": "CD",
                "S": "S",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Clb.Climb_segment(name="Climb_segment_2"),
            pulling={
                "RC_ceiling": "RC_ceiling",
                "minimum_gamma": "minimum_gamma",
                "cruise_altitude": "cruise_altitude",
                "S": "S",
                "g": "g",
                "Iso_Mach": "Iso_Mach",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Acc.Accelerate(name="Acc_Mach"),
            pulling={
                "g": "g",
                "S": "S",
                "Mach_cruise": "Mach_cruise",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Cru.Cruise_segment(name="Cruise_segment"),
            pulling={
                "S": "S",
                "g": "g",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Dec.Decelerate(name="Dec_Mach"),
            pulling={
                "g": "g",
                "S": "S",
                "Iso_Mach": "Iso_Mach",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Des.Descent_segment(name="Descent_segment_1"),
            pulling={
                "S": "S",
                "deceleration_altitude": "deceleration_altitude",
                "g": "g",
                "Iso_Mach": "Iso_Mach",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Dec.Decelerate(name="Decelerate"),
            pulling={
                "g": "g",
                "S": "S",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )
        self.add_child(
            Des.Descent_segment(name="Descent_segment_2"),
            pulling={
                "S": "S",
                "g": "g",
                "CLAeroIt": "CLAeroIt",
                "CDAeroIt": "CDAeroIt",
                "Thau": "Thau",
                "n_eng": "n_eng",
                "DAeroIt": "DAeroIt",
            },
        )

        # Configure the callback function for each child to use either the default (No callback) or user input
        all_children = self.children

        for child in all_children:
            self[child].mission_callback.callback_method = mission_callback

        ### ----------------------------------------------------------------------
        ### Values definition
        ### ----------------------------------------------------------------------

        # Constants
        self.g = 9.81  # Gravity acceleration in m/s2, to connect with constants module.

        """AC PARAMETERS values"""
        # Pulled variables shared between segments
        #         self.S = 124
        self.S = (
            self.flight_vehicle.airplane.s_ref
        )  # Wing surface from the AC, to connect with geometry module.

        self.Thau = 0.0  # Value in degrees to maintain coherence with the aero results (alpha in degrees). Results using this variable are computed in radians.
        self.n_eng = self.flight_vehicle.ag["n_eng"]
        print(self.S, self.n_eng)

        """Fuel capacity computation"""
        # Usage of the fuel volume module.
        th_ch_Ratio = max(
            airfoils.max_thickness() for airfoils in self.flight_vehicle.wing_airfoils
        )
        flight_vehicle_Fuel_VW = FuelVolume_Weight("Fuel_VW")
        flight_vehicle_Fuel_VW.tau = th_ch_Ratio
        flight_vehicle_Fuel_VW.S = self.S
        flight_vehicle_Fuel_VW.AR = self.flight_vehicle.airplane.wings[0].aspect_ratio()
        flight_vehicle_Fuel_VW.V_fuselage = self.flight_vehicle.airplane.fuselages[
            0
        ].volume()
        flight_vehicle_Fuel_VW.rho_f = 817  # density of fuel, unit='kg/m^3'
        flight_vehicle_Fuel_VW.V_f_fuse_ratio = (
            0.05  # 5% of the fuselage volume is considered to be for fuel storage.
        )
        flight_vehicle_Fuel_VW.run_once()
        self.W_f = flight_vehicle_Fuel_VW.W_f

        """Segments Profile values (pulled inwards)"""
        # First Climb Segment
        self.Climb_segment_1.in_p.position = np.array(
            [0.0, 0.0, uc.ft2m(1500)]
        )  # Initial position in the first segment (therefore for the simulation as well),  unit in ft.
        self.Climb_segment_1.in_p.fuel_mass = np.array(
            [0.0]
        )  # Initial consumed fuel mass for the first segment (and simulation) in kg.
        self.Climb_segment_1.CAS = (
            250.0  # Desired CAS to maintain during climb segment in knots.
        )
        self.Climb_segment_1.m0 = (
            68000.0  # Initial mass for the first segment (and simulation) in kg.
        )
        self.Climb_segment_1.enginePerfo.rating_eng = "MCRZ"
        self.Climb_segment_1.CS = np.array([0.0])

        # Acceleration Segment
        self.acceleration_altitude = round(uc.ft2m(10000), 2)  # unit in ft.
        self.Accelerate.CAS_target = 300.0  # Target speed, unit in kts.
        self.Accelerate.enginePerfo.rating_eng = "MCT"

        # Second Climb Segment
        self.Climb_segment_2.CAS = (
            300.0  # Desired CAS to maintain during climb segment in knots.
        )
        self.minimum_gamma = 0.024  ##unit in radians.
        self.Iso_Mach = 0.75  # Implicit for the first descent segment by sharing the same pulled variable.
        self.RC_ceiling = (
            uc.ft2m(300) / 60
        )  # units in ft/min [300ft/min conversion to m/s].
        self.Climb_segment_2.enginePerfo.rating_eng = "MCT"

        # Acceleration Segment (If needed).
        # This segment is taken into account only if the Mach at the end of climb (either CAS or IsoMach) is greater to the Cruise Mach.
        # In a new profile it is possible to define if an acceleration or deceleration phase is wanted by adding a segment, in this example for simplicity the connections between segments drives the condition to accelerate or not in a standard mission profile.

        # Cruise Segment
        self.cruise_altitude = uc.ft2m(32000)  # unit in ft.
        self.Mach_cruise = 0.8  # Desired Mach for cruise segment.
        self.Cruise_segment.enginePerfo.rating_eng = "MCRZ"

        # Deceleration Segment (If needed).
        # This segment is taken into account only if the Mach at the end of the cruise segment (either CAS or IsoMach) is greater to the  Descent Mach.
        # In a new profile it is possible to define if an acceleration or deceleration phase is wanted by adding a segment, in this example for simplicity the connections between segments drives the condition to accelerate or not in a standard mission profile.
        self.Dec_Mach.enginePerfo.rating_eng = "IDLE"

        # Descent Segment 1
        self.Descent_segment_1.CAS = (
            300.0  # Desired CAS to maintain during descent segment in knots.
        )
        # Iso-Mach is taken from climb definition to define if a deceleration from Mach_cruise to IsoMach is needed. However it is possible to define an independent IsoMach number if wanted.
        # self.Descent_segment_1.enginePerfo.rating_eng='MCRZ'
        self.Descent_segment_1.CRD = -10.0

        # Deceleration Segment
        self.deceleration_altitude = uc.ft2m(10000)  # unit in ft.
        self.Decelerate.CAS_target = 250.0  # Target speed, unit in kts.
        self.Decelerate.enginePerfo.rating_eng = "IDLE"

        # Descent Segment2
        self.Descent_segment_2.CAS = (
            250.0  # Desired CAS to maintain during descent segment in knots.
        )
        self.Descent_segment_2.IsoMach = False  # Variable defined if AC is flying on IsoMach, since the crossover altitude is assessed at descent segment 1 then it shall be initialized as False.
        self.Descent_segment_2.Fin_appr_altitude = uc.ft2m(
            1500
        )  # Final position in the last segment (therefore for the simulation as well),  unit in ft.
        # self.Descent_segment_2.enginePerfo.rating_eng='IDLE'
        self.Descent_segment_2.CRD = -5.0

        ### ----------------------------------------------------------------------
        ### Connections between variables and ports
        ### ----------------------------------------------------------------------

        # Connections from climb first phase to acceleration phase(250 kt until 10000ft)
        self.connect(
            self.Climb_segment_1.outwards, self.Accelerate.inwards, {"mass": "m0"}
        )
        self.connect(
            self.Climb_segment_1.out_p, self.Accelerate.in_p, {"position": "position"}
        )
        self.connect(
            self.Climb_segment_1.out_p, self.Accelerate.in_p, {"TAS_speed": "TAS_speed"}
        )

        # Connections from acceleration phase to climb second phase (300 kt until cruise level ft)
        self.connect(
            self.Accelerate.outwards, self.Climb_segment_2.inwards, {"mass": "m0"}
        )
        self.connect(
            self.Accelerate.out_p, self.Climb_segment_2.in_p, {"position": "position"}
        )
        self.connect(
            self.Accelerate.out_p, self.Climb_segment_2.in_p, {"TAS_speed": "TAS_speed"}
        )

        # Segments list extend
        self.flightSegments.extend(
            [self.Climb_segment_1, self.Accelerate, self.Climb_segment_2]
        )

        if self.Iso_Mach == self.Mach_cruise:
            # Connection from second climb phase to cruise level (cruise level ft, 0.78 - 0.82)
            self.connect(
                self.Climb_segment_2.outwards,
                self.Cruise_segment.inwards,
                {"mass": "m0"},
            )
            self.connect(
                self.Climb_segment_2.out_p,
                self.Cruise_segment.in_p,
                {"position": "position"},
            )
            self.connect(
                self.Climb_segment_2.out_p,
                self.Cruise_segment.inwards,
                {"position": "Cruise_pos_init"},
            )
            self.connect(
                self.Climb_segment_2.out_p,
                self.Cruise_segment.in_p,
                {"TAS_speed": "TAS_speed"},
            )
            # Connection from cruise to first descent phase.
            self.connect(
                self.Cruise_segment.outwards,
                self.Descent_segment_1.inwards,
                {"mass": "m0"},
            )
            self.connect(
                self.Cruise_segment.out_p,
                self.Descent_segment_1.in_p,
                {"position": "position"},
            )
            self.connect(
                self.Cruise_segment.out_p,
                self.Descent_segment_1.in_p,
                {"TAS_speed": "TAS_speed"},
            )

            self.flightSegments.extend([self.Cruise_segment, self.Descent_segment_1])

        else:
            # Connection in case that the 0.78 Mach needs to be increased to a different Mach number.
            self.connect(
                self.Climb_segment_2.outwards, self.Acc_Mach.inwards, {"mass": "m0"}
            )
            self.connect(
                self.Climb_segment_2.out_p, self.Acc_Mach.in_p, {"position": "position"}
            )
            self.connect(
                self.Climb_segment_2.out_p,
                self.Acc_Mach.in_p,
                {"TAS_speed": "TAS_speed"},
            )
            # Connection from cruise acceleration phase to cruise level (cruise level ft, 0.78 - 0.82)
            self.connect(
                self.Acc_Mach.outwards, self.Cruise_segment.inwards, {"mass": "m0"}
            )
            self.connect(
                self.Acc_Mach.out_p, self.Cruise_segment.in_p, {"position": "position"}
            )
            self.connect(
                self.Acc_Mach.out_p,
                self.Cruise_segment.inwards,
                {"position": "Cruise_pos_init"},
            )
            self.connect(
                self.Acc_Mach.out_p,
                self.Cruise_segment.in_p,
                {"TAS_speed": "TAS_speed"},
            )
            # Connection in case that the cruise Mach needs to be deccelerated to an IsoMach descent.
            self.connect(
                self.Cruise_segment.outwards, self.Dec_Mach.inwards, {"mass": "m0"}
            )
            self.connect(
                self.Cruise_segment.out_p, self.Dec_Mach.in_p, {"position": "position"}
            )
            self.connect(
                self.Cruise_segment.out_p,
                self.Dec_Mach.in_p,
                {"TAS_speed": "TAS_speed"},
            )
            # Connection from deceleration to first descent phase.
            self.connect(
                self.Dec_Mach.outwards, self.Descent_segment_1.inwards, {"mass": "m0"}
            )
            self.connect(
                self.Dec_Mach.out_p,
                self.Descent_segment_1.in_p,
                {"position": "position"},
            )
            self.connect(
                self.Dec_Mach.out_p,
                self.Descent_segment_1.in_p,
                {"TAS_speed": "TAS_speed"},
            )

            self.flightSegments.extend(
                [
                    self.Acc_Mach,
                    self.Cruise_segment,
                    self.Dec_Mach,
                    self.Descent_segment_1,
                ]
            )

        # Connection from first descent phase to a deceleration (CAS of 300kt to 250kt)
        self.connect(
            self.Descent_segment_1.outwards, self.Decelerate.inwards, {"mass": "m0"}
        )
        self.connect(
            self.Descent_segment_1.out_p, self.Decelerate.in_p, {"position": "position"}
        )
        self.connect(
            self.Descent_segment_1.out_p,
            self.Decelerate.in_p,
            {"TAS_speed": "TAS_speed"},
        )

        # Connection from deceleration to final descent phase.
        self.connect(
            self.Decelerate.outwards, self.Descent_segment_2.inwards, {"mass": "m0"}
        )
        self.connect(
            self.Decelerate.out_p, self.Descent_segment_2.in_p, {"position": "position"}
        )
        self.connect(
            self.Decelerate.out_p,
            self.Descent_segment_2.in_p,
            {"TAS_speed": "TAS_speed"},
        )

        self.flightSegments.extend([self.Decelerate, self.Descent_segment_2])

        ### ----------------------------------------------------------------------
        ### Drivers definition for each segment
        ### -----------------------------------------------------------------------
        # dt attribute is key for convergence, specially for those segments of small duration (accelerate/deccelerate)
        for segment in self.flightSegments:
            segment_driver = segment.add_driver(
                RungeKutta(
                    name="driver_" + segment.name, time_interval=(0, 100000), dt=1
                )
            )
            solver = segment_driver.add_child(
                NonLinearSolver("solver_" + segment.name, max_iter=500, tol=0.1)
            )

            segment_driver.add_recorder(
                DataFrameRecorder(
                    includes=self.Data_to_record,
                    raw_output=False,
                ),
                period=10,
            )
            self.drx[segment.name] = segment_driver  # Drivers dicctionary definition
        print("ITERATION")


if __name__ == "__main__":
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long_opti as airplane_geom,
    )

    mp = mission_profile(
        "mp", asb_aircraft_geometry=airplane_geom(), mission_callback=empty_callback
    )
