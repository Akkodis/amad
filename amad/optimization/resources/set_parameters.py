from amad.disciplines.design.resources.nose_geoms import dreamer_nose, concept_nose
from amad.disciplines.design.resources.tail_geoms import dreamer_tail
from amad.disciplines.design.resources.nacelle_geoms import modern_nacelle


def apply_parameters(parameter_dict, cosapp_system):
    for param in parameter_dict:
        try:
            cosapp_system[param] = parameter_dict[param]
        except KeyError:
            # TODO: prints in logger
            # print(f'Error with {param}')
            continue

    return cosapp_system


def single_aisle_concept(cosapp_system):
    # Geom and other params
    parameter_dict = {
        "a_control_surfaces": 21.77,
        "a_fuselage": 465,
        "ac_name": "Concept Single Aisle Aircraft",
        "alpha_takeoff": 0.0,
        "canard_airfoils": ["naca0010", "naca0010"],
        "canard_twists": [0, 0],
        "chord_canard_root": 2.5,
        "chord_htail_root": 4.195,
        "chord_vtail_root": 5.254,
        "chord_wing_root": 8.57,
        "d_nacelle": 2,
        "delta_canard_sweep": [10],
        "delta_htail_sweep": [27],
        "delta_vtail_sweep": [35],
        "delta_wing_sweep": [31.5, 23.5],
        "f_wing_var_sweep": 0,
        "gamma_canard_dihedral": [5],
        "gamma_htail_dihedral": [7],
        "gamma_vtail_dihedral": [0],
        "gamma_wing_dihedral": [6, 6],
        "h_fuse": 4.01,
        "htail_airfoils": ["naca0010", "naca0010"],
        "htail_twists": [0, 0],
        "m_cargo": 0,
        "m_mto": 79016,
        "m_mzf": 62721,
        "mach_mo": 0.82,
        "mach_takeoff": 0.45,
        "n_canard_sections": 0,
        "n_eng": 2,
        "n_eng_fuse": 0,
        "n_flatt": 4,
        "n_flcr": 2,
        "n_fuel_tanks": 3,
        "n_fuse": 1,
        "n_htail_sections": 2,
        "n_pax": 189,
        "n_pax_f": 0,
        "n_pax_j": 0,
        "n_pax_y": 189,
        "n_ult": 3.75,
        "n_vtail_sections": 2,
        "n_wing_sections": 3,
        "nacelle_def": modern_nacelle(),
        "nose_def": dreamer_nose(),
        "p_hydraulic": 20684000,
        "r_bypass": 5.3,
        "r_canard_taper": [0.3],
        "r_htail_taper": [0.203],
        "r_vtail_taper": [0.271],
        "r_wing_taper": [0.631, 0.252],
        "t_wing_root_chord": 1.21352,
        "tail_def": dreamer_tail(),
        "tail_length_scaling": 1,
        "tech_attached_gear": "False",
        "tech_cargo_floor": "False",
        "tech_highwing": "False",
        "tech_htail_mounting": "fuselage",
        "tech_pressurized_fuse": "True",
        "tech_retractable": "True",
        "tech_stabilizers": "fixed",
        "tech_tail_gear": "False",
        "type_aircraft": "transport",
        "v_dive": 205.778,
        "vtail_airfoils": ["naca0010", "naca0010"],
        "vtail_twists": [0, 0],
        "w_fuse": 3.76,
        "wing_airfoils": ["b737a", "b737d", "b737d"],
        "wing_twists": [7, 5.241, 0],
        "x_cabin": 30.02,
        "x_canard_span": [10],
        "x_canard_X_le": 3,
        "x_canard_Z_le": 1,
        "x_fuse": 38.01,
        "x_htail_offset": 0,
        "x_htail_span": [14.35],
        "x_nacelle": 3.5,
        "x_vtail_offset": 0,
        "x_vtail_span": [7.16],
        "x_vtailroot_htail": 0,
        "x_wing_le": 14.4,
        "x_wing_span": [8.62, 34.32],
        "x_wing_tail_chord": 18,
        "z_altitude_takeoff": 0.0,
    }

    cosapp_system_updated = apply_parameters(parameter_dict, cosapp_system)

    return cosapp_system_updated


def advanced_ac_concept(cosapp_system):
    # Geom and other params
    parameter_dict = {
        "nose_def": concept_nose(),
        "canard_airfoils": ["naca0010", "naca0010"],
        "chord_canard_root": 2.5,
        "chord_htail_root": 4.195,
        "chord_vtail_root": 5.254,
        "chord_wing_root": 10,
        "delta_canard_sweep": [10],
        "delta_htail_sweep": [30],
        "delta_vtail_sweep": [35],
        "delta_wing_sweep": [-25],
        "gamma_canard_dihedral": [5],
        "gamma_htail_dihedral": [40],
        "gamma_vtail_dihedral": [0],
        "gamma_wing_dihedral": [-10],
        "htail_airfoils": ["naca0010", "naca0010"],
        "n_canard_sections": 2,
        "n_htail_sections": 2,
        "n_vtail_sections": 0,
        "n_wing_sections": 2,
        "r_canard_taper": [0.3],
        "r_htail_taper": [0.203],
        "r_vtail_taper": [0.271],
        "r_wing_taper": [0.129],
        "tech_highwing": "True",
        "vtail_airfoils": ["naca0010", "naca0010"],
        "wing_airfoils": ["b737a", "b737d"],
        "x_canard_span": [10],
        "x_canard_X_le": 3,
        "x_canard_Z_le": 1,
        "x_htail_span": [10],
        "x_htail_offset": 0,
        "x_vtail_span": [7.16],
        "x_vtail_offset": 0,
        "x_wing_le": 17,
        "x_wing_span": [34.32],
        "ac_name": "Concept Airplane",
        "wing_twists": [7, 0],
        "canard_twists": [0, 0],
        "htail_twists": [0, 0],
        "vtail_twists": [0, 0],
    }

    cosapp_system_updated = apply_parameters(parameter_dict, cosapp_system)

    return cosapp_system_updated
