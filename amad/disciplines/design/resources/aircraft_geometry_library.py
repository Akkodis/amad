from amad.disciplines.design.systems import GenerateAeroGeom


def ac_narrow_body_base_geom():
    from amad.disciplines.design.resources.nose_geoms import dreamer_nose
    from amad.disciplines.design.resources.tail_geoms import dreamer_tail
    from amad.disciplines.design.resources.nacelle_geoms import modern_nacelle

    ac_narrow_body_base = GenerateAeroGeom("ac_narrow_base")
    ac_narrow_body_base.nose_def = dreamer_nose()
    ac_narrow_body_base.tail_def = dreamer_tail()
    ac_narrow_body_base.canard_airfoils = ["naca0010", "naca0010"]
    ac_narrow_body_base.chord_canard_root = 2.5
    ac_narrow_body_base.chord_htail_root = 4.195
    ac_narrow_body_base.chord_vtail_root = 5.254
    ac_narrow_body_base.chord_wing_root = 7.32
    ac_narrow_body_base.delta_canard_sweep = [10]
    ac_narrow_body_base.delta_htail_sweep = [27]
    ac_narrow_body_base.delta_vtail_sweep = [35]
    ac_narrow_body_base.delta_wing_sweep = [25]
    ac_narrow_body_base.gamma_canard_dihedral = [5]
    ac_narrow_body_base.gamma_htail_dihedral = [7]
    ac_narrow_body_base.gamma_vtail_dihedral = [0]
    ac_narrow_body_base.gamma_wing_dihedral = [6]
    ac_narrow_body_base.h_fuse = 4.01
    ac_narrow_body_base.htail_airfoils = ["naca0010", "naca0010"]
    ac_narrow_body_base.n_eng = 2
    ac_narrow_body_base.n_eng_fuse = 0
    ac_narrow_body_base.n_fuse = 1
    ac_narrow_body_base.n_canard_sections = 0
    ac_narrow_body_base.n_htail_sections = 2
    ac_narrow_body_base.n_vtail_sections = 2
    ac_narrow_body_base.n_wing_sections = 2
    ac_narrow_body_base.r_canard_taper = [0.3]
    ac_narrow_body_base.r_htail_taper = [0.260]
    ac_narrow_body_base.r_vtail_taper = [0.288]
    ac_narrow_body_base.r_wing_taper = [0.266]
    ac_narrow_body_base.tech_highwing = "False"
    ac_narrow_body_base.vtail_airfoils = ["naca0010", "naca0010"]
    ac_narrow_body_base.w_fuse = 3.76
    ac_narrow_body_base.wing_airfoils = ["ac_narrow_a", "ac_narrow_d"]
    ac_narrow_body_base.x_canard_span = [10]
    ac_narrow_body_base.x_canard_X_le = 3
    ac_narrow_body_base.x_canard_Z_le = 1
    ac_narrow_body_base.x_fuse = 27.66
    ac_narrow_body_base.x_htail_span = [10.97]
    ac_narrow_body_base.x_htail_offset = 0
    ac_narrow_body_base.x_vtail_span = [6.15]
    ac_narrow_body_base.x_vtail_offset = 0
    # ac_narrow_body_base.x_wing_le = 8.
    ac_narrow_body_base.x_wing_span = [34.32]
    ac_narrow_body_base.tail_length_scaling = 1
    ac_narrow_body_base.ac_name = "Narrow Body Aircraft"
    ac_narrow_body_base.wing_twists = [7, 0]
    ac_narrow_body_base.canard_twists = [0, 0]
    ac_narrow_body_base.htail_twists = [0, 0]
    ac_narrow_body_base.vtail_twists = [0, 0]
    ac_narrow_body_base.d_nacelle = 1.5
    ac_narrow_body_base.x_nacelle = 2.5
    ac_narrow_body_base.nacelle_def = modern_nacelle()

    return ac_narrow_body_base


def generate_geom(geom_object):
    geom_object.run_once()
    return geom_object.asb_aircraft_geometry_out


def ac_narrow_body():
    return generate_geom(ac_narrow_body_base_geom())


def ac_narrow_body_base_nofuse():
    base_geom = ac_narrow_body_base_geom()
    base_geom.n_fuse = 0.0

    return generate_geom(base_geom)


def ac_narrow_body_nofuse_notail():
    base_geom = ac_narrow_body_base_geom()
    base_geom.n_fuse = 0.0
    base_geom.n_htail_sections = 0
    base_geom.n_vtail_sections = 0
    return generate_geom(base_geom)


def ac_narrow_body_long():
    base_geom = ac_narrow_body_base_geom()
    tail_trim = 0.0

    base_geom.wing_airfoils = ["b737a", "b737d", "b737d"]
    base_geom.n_wing_sections = 3
    base_geom.wing_twists = [7, 5.241, 0]
    base_geom.gamma_wing_dihedral = [6, 6]
    base_geom.delta_wing_sweep = [31.5, 23.5]
    base_geom.chord_wing_root = 8.57
    base_geom.n_eng = 2
    base_geom.r_htail_taper = [0.203]
    base_geom.r_vtail_taper = [0.271]
    base_geom.r_wing_taper = [0.631, 0.252]
    base_geom.x_fuse = 38.01
    base_geom.x_htail_span = [14.35]
    base_geom.x_htail_offset = 0
    base_geom.x_vtail_span = [7.16]
    base_geom.x_vtail_offset = 0
    # base_geom.x_wing_le = 14.4
    base_geom.x_wing_span = [8.62, 34.32]
    base_geom.tail_length_scaling = 1
    base_geom.ac_name = "Narrow Body Aircraft Long"
    base_geom.d_nacelle = 2.0
    base_geom.x_nacelle = 3.5
    base_geom.htail_twists = [tail_trim, tail_trim]

    return generate_geom(base_geom)


def ac_narrow_body_long_opti():
    base_geom = ac_narrow_body_base_geom()
    tail_trim = 0.0

    base_geom.wing_airfoils = ["b737a", "b737d", "b737d"]
    base_geom.n_wing_sections = 3
    base_geom.wing_twists = [7, 5.241, 0]
    base_geom.gamma_wing_dihedral = [6, 6]
    base_geom.delta_wing_sweep = [31.5, 24.0268]
    base_geom.chord_wing_root = 7.87731
    base_geom.n_eng = 2
    base_geom.r_htail_taper = [0.203]
    base_geom.r_vtail_taper = [0.271]
    base_geom.r_wing_taper = [0.631, 0.223609]
    base_geom.x_fuse = 38.01
    base_geom.x_htail_span = [14.35]
    base_geom.x_htail_offset = 0
    base_geom.x_vtail_span = [7.16]
    base_geom.x_vtail_offset = 0
    # base_geom.x_wing_le = 14.4
    base_geom.x_wing_span = [8.62, 34.32]
    base_geom.tail_length_scaling = 1
    base_geom.ac_name = "Narrow Body Aircraft Long"
    base_geom.d_nacelle = 2.0
    base_geom.x_nacelle = 3.5
    base_geom.htail_twists = [tail_trim, tail_trim]

    return generate_geom(base_geom)


def concept_front_swept_canard():
    from amad.disciplines.design.resources.nose_geoms import concept_nose
    from amad.disciplines.design.resources.tail_geoms import dreamer_tail
    from amad.disciplines.design.resources.nacelle_geoms import modern_nacelle

    concept = GenerateAeroGeom("concept")
    concept.nose_def = concept_nose()
    concept.tail_def = dreamer_tail()
    concept.canard_airfoils = ["naca0010", "naca0010"]
    concept.chord_canard_root = 2.5
    concept.chord_htail_root = 4.195
    concept.chord_vtail_root = 5.254
    concept.chord_wing_root = 10
    concept.delta_canard_sweep = [10]
    concept.delta_htail_sweep = [30]
    concept.delta_vtail_sweep = [35]
    concept.delta_wing_sweep = [-25]
    concept.gamma_canard_dihedral = [5]
    concept.gamma_htail_dihedral = [40]
    concept.gamma_vtail_dihedral = [0]
    concept.gamma_wing_dihedral = [-10]
    concept.h_fuse = 4.01
    concept.htail_airfoils = ["naca0010", "naca0010"]
    concept.n_fuse = 1
    concept.n_canard_sections = 2
    concept.n_htail_sections = 2
    concept.n_vtail_sections = 0
    concept.n_wing_sections = 2
    concept.r_canard_taper = [0.3]
    concept.r_htail_taper = [0.203]
    concept.r_vtail_taper = [0.271]
    concept.r_wing_taper = [0.129]
    concept.tech_highwing = "True"
    concept.vtail_airfoils = ["naca0010", "naca0010"]
    concept.w_fuse = 3.76
    concept.wing_airfoils = ["b737a", "b737d"]
    concept.x_canard_span = [10]
    concept.x_canard_X_le = 3
    concept.x_canard_Z_le = 1
    concept.x_fuse = 30.0
    concept.x_htail_span = [10]
    concept.x_htail_offset = 0
    concept.x_vtail_span = [7.16]
    concept.x_vtail_offset = 0
    # concept.x_wing_le = 13.
    concept.x_wing_span = [34.32]
    concept.tail_length_scaling = 1
    concept.ac_name = "Test Airplane"
    concept.wing_twists = [7, 0]
    concept.canard_twists = [0, 0]
    concept.htail_twists = [0, 0]
    concept.vtail_twists = [0, 0]
    concept.d_nacelle = 1.5
    concept.x_nacelle = 2.5
    concept.nacelle_def = modern_nacelle()

    return generate_geom(concept)


def little_wing():
    from amad.disciplines.design.resources.nose_geoms import dreamer_nose
    from amad.disciplines.design.resources.tail_geoms import dreamer_tail

    littlewing = GenerateAeroGeom("concept")
    littlewing.nose_def = dreamer_nose()
    littlewing.tail_def = dreamer_tail()
    littlewing.canard_airfoils = ["naca0010", "naca0010"]
    littlewing.chord_canard_root = 2.5
    littlewing.chord_htail_root = 4.195
    littlewing.chord_vtail_root = 5.254
    littlewing.chord_wing_root = 5
    littlewing.delta_canard_sweep = [10]
    littlewing.delta_htail_sweep = [30]
    littlewing.delta_vtail_sweep = [35]
    littlewing.delta_wing_sweep = [0]
    littlewing.gamma_canard_dihedral = [5]
    littlewing.gamma_htail_dihedral = [40]
    littlewing.gamma_vtail_dihedral = [0]
    littlewing.gamma_wing_dihedral = [0]
    littlewing.h_fuse = 0
    littlewing.htail_airfoils = ["naca0010", "naca0010"]
    littlewing.n_fuse = 0
    littlewing.n_canard_sections = 0
    littlewing.n_htail_sections = 0
    littlewing.n_vtail_sections = 0
    littlewing.n_wing_sections = 2
    littlewing.r_canard_taper = [0.3]
    littlewing.r_htail_taper = [0.203]
    littlewing.r_vtail_taper = [0.271]
    littlewing.r_wing_taper = [1]
    littlewing.tech_highwing = "True"
    littlewing.vtail_airfoils = ["naca0010", "naca0010"]
    littlewing.w_fuse = 3.76
    littlewing.wing_airfoils = ["naca0010", "naca0010"]
    littlewing.x_canard_span = [10]
    littlewing.x_canard_X_le = 3
    littlewing.x_canard_Z_le = 1
    littlewing.x_fuse = 0
    littlewing.x_htail_span = [10]
    littlewing.x_htail_offset = 0
    littlewing.x_vtail_span = [7.16]
    littlewing.x_vtail_offset = 0
    # littlewing.x_wing_le = 0.
    littlewing.x_wing_span = [20]
    littlewing.tail_length_scaling = 1
    littlewing.ac_name = "Test Wing"
    littlewing.wing_twists = [0, 0]
    littlewing.canard_twists = [0, 0]
    littlewing.htail_twists = [0, 0]
    littlewing.vtail_twists = [0, 0]
    littlewing.d_nacelle = 1.5
    littlewing.x_nacelle = 2.5
    littlewing.nacelle_def = ((0, 0, 0, 1), (1, 0, 0, 1))

    return generate_geom(littlewing)
