import abc
from cosapp.base import System
from amad.disciplines.mass.ports import MassPort


class AbstractMassComponent(System):
    """
    A system which has a standard mass output port
    and an abstract mass computation method.
    Inward parameters are input automatically from a configuration file
    """

    def setup(
        self, inward_list: list[str]
    ):  # list[dict] if we want to pass a list of dict instead
        # mass 'port'
        """
        Set up the object with the specified inward list.

        Parameters
        ----------
        inward_list : list[str]
            A list of strings representing the names of the inward values to be added.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.add_output(MassPort, "total")

        numerics = (int, float, list)

        # TODO move this to resources
        inward_dict = {
            "a_control_surfaces": {
                "definition": "a_control_surfaces",
                "value": 0.0,
                "desc": "Total area of all flight control surfaces",
                "unit": "m*2",
                "dtype": numerics,
            },
            "a_fuselage": {
                "definition": "a_fuselage",
                "value": 0.0,
                "desc": "Fuselage surface area",
                "unit": "m**2",
                "dtype": numerics,
            },
            "chord_wing_root": {
                "definition": "chord_wing_root",
                "value": 0.0,
                "desc": "Wing root chord",
                "unit": "m",
                "dtype": numerics,
            },
            "chord_htail_root": {
                "definition": "chord_htail_root",
                "value": 0.0,
                "desc": "Horizontal Tail root chord",
                "unit": "m",
                "dtype": numerics,
            },
            "chord_vtail_root": {
                "definition": "chord_vtail_root",
                "value": 0.0,
                "desc": "Vertical Tail root chord",
                "unit": "m",
                "dtype": numerics,
            },
            "d_nacelle": {
                "definition": "d_nacelle",
                "value": 0.0,
                "desc": "Nacelle maximum diameter",
                "unit": "m",
                "dtype": numerics,
            },
            "delta_htail_sweep": {
                "definition": "delta_htail_sweep",
                "value": 0.0,
                "desc": "Horizontal Tail Sweep",
                "unit": "deg",
                "dtype": numerics,
            },
            "delta_vtail_sweep": {
                "definition": "delta_vtail_sweep",
                "value": 0.0,
                "desc": "Vertical Tail Sweep",
                "unit": "deg",
                "dtype": numerics,
            },
            "delta_wing_sweep": {
                "definition": "delta_wing_sweep",
                "value": 0.0,
                "desc": "Wing sweep",
                "unit": "deg",
                "dtype": numerics,
            },
            "f_cargo_floor": {
                "definition": "f_cargo_floor",
                "value": 0.0,
                "desc": "Cargo aircraft floor  factor",
                "unit": "",
                "dtype": numerics,
            },
            "f_wing_var_sweep": {
                "definition": "f_wing_var_sweep",
                "value": 0.0,
                "desc": "Wing variable sweep weight penalty factor",
                "unit": "",
                "dtype": numerics,
            },
            "h_fuse": {
                "definition": "h_fuse",
                "value": 0.0,
                "desc": "Maximum fuselage height",
                "unit": "m",
                "dtype": numerics,
            },
            "m_cargo": {
                "definition": "m_cargo",
                "value": 0.0,
                "desc": "Cargo weight carried",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_fuel_climb": {
                "definition": "m_fuel_climb",
                "value": 0.0,
                "desc": "Climb fuel requirement",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_fuel_cruise": {
                "definition": "m_fuel_cruise",
                "value": 0.0,
                "desc": "Cruise fuel requirement",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_fuel_descent": {
                "definition": "m_fuel_descent",
                "value": 0.0,
                "desc": "Descent fuel requirement",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_fuel_taxi": {
                "definition": "m_fuel_taxi",
                "value": 0.0,
                "desc": "Taxi fuel requirement",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_fuel": {
                "definition": "m_fuel",
                "value": 0.0,
                "desc": "Fuel capacity",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_me": {
                "definition": "m_me",
                "value": 0.0,
                "desc": "Manufacturer Empty Mass",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_mlw": {
                "definition": "m_mlw",
                "value": 0.0,
                "desc": "Max. Landing Mass",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_mto": {
                "definition": "m_mto",
                "value": 0.0,
                "desc": "Max.Takeoff Mass",
                "unit": "kg",
                "dtype": numerics,
            },
            "m_mzf": {
                "definition": "m_mzf",
                "value": 0.0,
                "desc": "Maximum Zero Fuel Weight",
                "unit": "kg",
                "dtype": numerics,
            },
            "mach_cruise": {
                "definition": "mach_cruise",
                "value": 0.0,
                "desc": "Mach, cruise",
                "unit": "",
                "dtype": numerics,
            },
            "mach_mo": {
                "definition": "mach_mo",
                "value": 0.0,
                "desc": "Mach, maximum operational",
                "unit": "",
                "dtype": numerics,
            },
            "n_eng": {
                "definition": "n_eng",
                "value": 0.0,
                "desc": "Number of engines, total",
                "unit": "",
                "dtype": numerics,
            },
            "n_eng_fuse": {
                "definition": "n_eng_fuse",
                "value": 0.0,
                "desc": "Number of fuselage-mounted engines",
                "unit": "",
                "dtype": numerics,
            },
            "n_flatt": {
                "definition": "n_flatt",
                "value": 0.0,
                "desc": "Number of Flight Attendants",
                "unit": "",
                "dtype": numerics,
            },
            "n_flcr": {
                "definition": "n_flcr",
                "value": 0.0,
                "desc": "Number of Flight Crew",
                "unit": "",
                "dtype": numerics,
            },
            "n_fuel_tanks": {
                "definition": "n_fuel_tanks",
                "value": 0.0,
                "desc": "Number of fuel tanks",
                "unit": "",
                "dtype": numerics,
            },
            "n_fuse": {
                "definition": "n_fuse",
                "value": 0.0,
                "desc": "Number of fuselages",
                "unit": "",
                "dtype": numerics,
            },
            "n_pax": {
                "definition": "n_pax",
                "value": 0.0,
                "desc": "Number of passengers (max)",
                "unit": "",
                "dtype": numerics,
            },
            "n_pax_f": {
                "definition": "n_pax_f",
                "value": 0.0,
                "desc": "Number of F class passengers (First)",
                "unit": "",
                "dtype": numerics,
            },
            "n_pax_j": {
                "definition": "n_pax_j",
                "value": 0.0,
                "desc": "Number of J class passengers (Business)",
                "unit": "",
                "dtype": numerics,
            },
            "n_pax_y": {
                "definition": "n_pax_y",
                "value": 0.0,
                "desc": "Number of Y class passengers (Economy)",
                "unit": "",
                "dtype": numerics,
            },
            "n_ult": {
                "definition": "n_ult",
                "value": 0.0,
                "desc": "Design Ultimate Load Factor",
                "unit": "",
                "dtype": numerics,
            },
            "p_hydraulic": {
                "definition": "p_hydraulic",
                "value": 0.0,
                "desc": "Hydraulic system pressure",
                "unit": "Pa",
                "dtype": numerics,
            },
            "r_bypass": {
                "definition": "r_bypass",
                "value": 0.0,
                "desc": "Byapss Ratio (Turbofan or Turbojet)",
                "unit": "",
                "dtype": numerics,
            },
            "r_wing_aspect": {
                "definition": "r_wing_aspect",
                "value": 0.0,
                "desc": "Wing aspect ratio",
                "unit": "",
                "dtype": numerics,
            },
            "r_wing_taper": {
                "definition": "r_wing_taper",
                "value": 0.0,
                "desc": "Wing taper ratio",
                "unit": "",
                "dtype": numerics,
            },
            "r_htail_taper": {
                "definition": "r_htail_taper",
                "value": 0.0,
                "desc": "Horizontal Tail Taper ratio(s)",
                "unit": "",
                "dtype": numerics,
            },
            "r_vtail_taper": {
                "definition": "r_vtail_taper",
                "value": 0.0,
                "desc": "Vertical Tail Taper ratio(s)",
                "unit": "",
                "dtype": numerics,
            },
            "t_wing_root_chord": {
                "definition": "t_wing_root_chord",
                "value": 0.0,
                "desc": "Wing root chord thickness",
                "unit": "m",
                "dtype": numerics,
            },
            "tech_attached_gear": {
                "definition": "tech_attached_gear",
                "value": "-",
                "desc": "Identifies if main gear is attached to fuselage or not",
                "dtype": str,
            },
            "tech_bracing": {
                "definition": "tech_bracing",
                "value": "-",
                "desc": "Specifies if wing is strut braced or not",
                "dtype": str,
            },
            "tech_cargo_floor": {
                "definition": "tech_cargo_floor",
                "value": "-",
                "desc": "Identifies if aircraft is cargo and has cargo floor",
                "dtype": str,
            },
            "tech_center_eng": {
                "definition": "tech_center_eng",
                "value": "-",
                "desc": "Center-mounted engine fitted",
                "dtype": str,
            },
            "tech_highwing": {
                "definition": "tech_highwing",
                "value": "-",
                "desc": "Specifies if wing is highwing or not",
                "dtype": str,
            },
            "tech_htail_mounting": {
                "definition": "tech_htail_mounting",
                "value": "-",
                "desc": "Fuselage or fin (VTP) mounted horizontal tails",
                "dtype": str,
            },
            "tech_pressurized_fuse": {
                "definition": "tech_pressurized_fuse",
                "value": "-",
                "desc": "Identifies if fuselage is pressurized or not",
                "dtype": str,
            },
            "tech_retractable": {
                "definition": "tech_retractable",
                "value": "-",
                "desc": "Identifies if gear is retractable",
                "dtype": str,
            },
            "tech_stabilizers": {
                "definition": "tech_stabilizers",
                "value": "-",
                "desc": "Fixed or variable incidence stabilizers",
                "dtype": str,
            },
            "tech_tail_gear": {
                "definition": "tech_tail_gear",
                "value": "-",
                "desc": "Identifies if a tail gear system is present",
                "dtype": str,
            },
            "techno_carrier": {
                "definition": "techno_carrier",
                "value": 0.0,
                "desc": "Technology switch to specify if carrier-based or not",
                "unit": "",
                "dtype": numerics,
            },
            "thrust_eng": {
                "definition": "thrust_eng",
                "value": 0.0,
                "desc": "Thrust per engine",
                "unit": "N",
                "dtype": numerics,
            },
            "type_aircraft": {
                "definition": "type_aircraft",
                "value": "-",
                "desc": "",
                "dtype": str,
            },
            "v_dive": {
                "definition": "v_dive",
                "value": 0.0,
                "desc": "Design dive speed",
                "unit": "kt",
                "dtype": numerics,
            },
            "v_fuel_fuse": {
                "definition": "v_fuel_fuse",
                "value": 0.0,
                "desc": "Fuselage fuel volume, could be derived from weight",
                "unit": "m**3",
                "dtype": numerics,
            },
            "w_fuse": {
                "definition": "w_fuse",
                "value": 0.0,
                "desc": "Maximum fuselage width",
                "unit": "m",
                "dtype": numerics,
            },
            "x_cabin": {
                "definition": "x_cabin",
                "value": 0.0,
                "desc": "Cabin length",
                "unit": "m",
                "dtype": numerics,
            },
            "x_fuse": {
                "definition": "x_fuse",
                "value": 0.0,
                "desc": "Total Fuselage Length",
                "unit": "m",
                "dtype": numerics,
            },
            "x_mlgoleo": {
                "definition": "x_mlgoleo",
                "value": 0.0,
                "desc": "Length of MLG oleo, extended",
                "unit": "m",
                "dtype": numerics,
            },
            "x_nacelle": {
                "definition": "x_nacelle",
                "value": 0.0,
                "desc": "Nacelle length",
                "unit": "m",
                "dtype": numerics,
            },
            "x_nlgoleo": {
                "definition": "x_nlgoleo",
                "value": 0.0,
                "desc": "Length of NLG oleo, extended",
                "unit": "m",
                "dtype": numerics,
            },
            "x_range": {
                "definition": "x_range",
                "value": 0.0,
                "desc": "Design range",
                "unit": "m",
                "dtype": numerics,
            },
            "x_vtailroot_htail": {
                "definition": "x_vtailroot_htail",
                "value": 0.0,
                "desc": "Distance from Vertical Tail root to Horizontal Tail mounting",
                "unit": "m",
                "dtype": numerics,
            },
            "x_wing_span": {
                "definition": "x_wing_span",
                "value": 0.0,
                "desc": "Wing span",
                "unit": "m",
                "dtype": numerics,
            },
            "x_htail_span": {
                "definition": "x_htail_span",
                "value": 0.0,
                "desc": "Horizontal Tail Span(s)",
                "unit": "m",
                "dtype": numerics,
            },
            "x_vtail_span": {
                "definition": "x_vtail_span",
                "value": 0.0,
                "desc": "Vertical Tail Span(s)",
                "unit": "m",
                "dtype": numerics,
            },
            "x_wing_tail_chord": {
                "definition": "x_wing_tail_chord",
                "value": 0.0,
                "desc": "Distance from wing 1/4C to tail 1/4C",
                "unit": "m",
                "dtype": numerics,
            },
        }

        # computed mass outward
        self.add_outward("total_mass", 0.0, unit="kg")

        for inw in inward_list:
            self.add_inward(**inward_dict[inw])

    @abc.abstractmethod
    def compute_mass(self) -> None:
        """
        Compute the mass of the component.
        """
        pass

    def compute(self):
        """
        Compute the total mass.

        This method calculates the total mass by first calling the `compute_mass` method to calculate the mass, and then assigns the resulting value to the `total.mass` attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.compute_mass()
        self.total.mass = self.total_mass
