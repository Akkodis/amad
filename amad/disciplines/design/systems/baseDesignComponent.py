from cosapp.base import System


class BaseDesignComponent(System):
    """The base component for design systems
    Inward parameters are input automatically from a configuration file

    """

    def setup(self):
        input_definition = {
            "ac_name": {"Description": "", "Unit": "STR"},
            "canard_airfoils": {
                "Description": "List of airfoils used on the canard from root to tip",
                "Unit": "",
            },
            "canard_twists": {
                "Description": "List of canard twists from root to tip. Normally zero!",
                "Unit": "deg",
            },
            "chord_canard_root": {"Description": "Canard root chord", "Unit": "m"},
            "chord_htail_root": {
                "Description": "Horizontal Tail root chord",
                "Unit": "m",
            },
            "chord_vtail_root": {
                "Description": "Vertical Tail root chord",
                "Unit": "m",
            },
            "chord_wing": {"Description": "Wing chord(s)", "Unit": "m"},
            "chord_wing_root": {"Description": "Wing root chord", "Unit": "m"},
            "d_nacelle": {"Description": "Nacelle maximum diameter", "Unit": "m"},
            "delta_canard_sweep": {
                "Description": "Canard sweep angle(s)",
                "Unit": "deg",
            },
            "delta_htail_sweep": {
                "Description": "Horizontal Tail Sweep(s)",
                "Unit": "deg",
            },
            "delta_vtail_sweep": {
                "Description": "Vertical Tail Sweep(s)",
                "Unit": "deg",
            },
            "delta_wing_sweep": {"Description": "Wing sweep", "Unit": "deg"},
            "gamma_canard_dihedral": {
                "Description": "Canard dihedral angle(s)",
                "Unit": "deg",
            },
            "gamma_htail_dihedral": {
                "Description": "Horizontal Tail Dihedral angle(s)",
                "Unit": "deg",
            },
            "gamma_vtail_dihedral": {
                "Description": "Vertail Tail Dihedral angle(s)",
                "Unit": "deg",
            },
            "gamma_wing_dihedral": {
                "Description": "Wing dihedral angle(s)",
                "Unit": "deg",
            },
            "h_fuse": {"Description": "Maximum fuselage height", "Unit": "m"},
            "htail_airfoils": {
                "Description": "List of airfoils used on the htp from root to tip",
                "Unit": "",
            },
            "htail_twists": {
                "Description": "List of horizontal tail twists from root to tip",
                "Unit": "deg",
            },
            "n_canard_sections": {
                "Description": "Number of canard sections from root to tip. Minimum 2",
                "Unit": "",
            },
            "n_eng": {"Description": "Number of engines, total", "Unit": ""},
            "n_eng_fuse": {
                "Description": "Number of fuselage-mounted engines",
                "Unit": "",
            },
            "n_fuse": {"Description": "Number of fuselages", "Unit": ""},
            "n_htail_sections": {
                "Description": "Number of htp sections from root to tip. Minimum 2",
                "Unit": "",
            },
            "n_vtail_sections": {
                "Description": "Number of htp sections from root to tip. Minimum 2",
                "Unit": "",
            },
            "n_wing_sections": {
                "Description": "Number of wing sections from root to tip. Minimum 2",
                "Unit": "",
            },
            "n_pax": {"Description": "Number of passengers (max)", "Unit": ""},
            "r_canard_taper": {"Description": "Canard taper ratio(s)", "Unit": ""},
            "r_htail_taper": {
                "Description": "Horizontal Tail Taper ratio(s)",
                "Unit": "",
            },
            "r_vtail_taper": {
                "Description": "Vertical Tail Taper ratio(s)",
                "Unit": "",
            },
            "r_wing_taper": {"Description": "Wing taper ratio(s)", "Unit": ""},
            "tail_length_scaling": {
                "Description": "Scaling factor to apply to the tail in the X (length) axis",
                "Unit": "",
            },
            "tech_highwing": {
                "Description": "Specifies if wing is highwing or not",
                "Unit": "STR",
            },
            "vtail_airfoils": {
                "Description": "List of airfoils used on the vtp from root to tip",
                "Unit": "",
            },
            "vtail_twists": {
                "Description": "List of vertical tail twists from root to tip. Normally zero!",
                "Unit": "deg",
            },
            "w_fuse": {"Description": "Maximum fuselage width", "Unit": "m"},
            "wing_airfoils": {
                "Description": "List of airfoils used on the wing from root to tip",
                "Unit": "",
            },
            "wing_twists": {
                "Description": "List of wing twists from root to tip",
                "Unit": "deg",
            },
            "x_canard_X_le": {
                "Description": "Distance from nose to canard leading edge",
                "Unit": "m",
            },
            "x_canard_Z_le": {
                "Description": "distance from fuselage base to canard leading edge",
                "Unit": "m",
            },
            "x_canard_span": {"Description": "Canard span(s)", "Unit": "m"},
            "x_fuse": {"Description": "Total Fuselage Length", "Unit": "m"},
            "x_htail_offset": {
                "Description": "Horizontal Tail offset distance to fuselage end",
                "Unit": "m",
            },
            "x_htail_span": {"Description": "Horizontal Tail Span(s)", "Unit": "m"},
            "x_nacelle": {"Description": "Nacelle length", "Unit": "m"},
            "x_vtail_offset": {
                "Description": "Vertical Tail offset distance to fuselage end",
                "Unit": "m",
            },
            "x_vtail_span": {"Description": "Vertical Tail Span(s)", "Unit": "m"},
            "x_vtailroot_htail": {
                "Description": "Distance from Vertical Tail root to Horizontal Tail mounting",
                "Unit": "m",
            },
            "x_wing_span": {"Description": "Wing span(s)", "Unit": "m"},
        }

        # inwards
        for parameter in input_definition:
            if input_definition[parameter]["Unit"] == "STR":
                unit = ""
                value = "-"
                dtype = str
            else:
                unit = input_definition[parameter]["Unit"]
                value = 1.0
                dtype = (int, float, list)

            self.add_inward(
                parameter,
                unit=unit,
                desc=input_definition[parameter]["Description"],
                value=value,
                dtype=dtype,
            )
