from amad.disciplines.design.systems import GenerateAeroGeom


def ac_narrow_body_base_geom():
    """
    Generate the base geometry parameters for a narrow body aircraft.

    Returns
    -------
    ac_narrow_body_base : GenerateAeroGeom object
        Contains the base geometry parameters for the aircraft.

    Notes
    -----
    This function imports the following modules:
    - `amad.disciplines.design.resources.nose_geoms`
    - `amad.disciplines.design.resources.tail_geoms`
    - `amad.disciplines.design.resources.nacelle_geoms`

    The function sets the following parameters in the `ac_narrow_body_base` object:
    - `nose_def`
    - `tail_def`
    - `canard_airfoils`
    - `chord_canard_root`
    - `chord_htail_root`
    - `chord_vtail_root`
    - `chord_wing_root`
    - `delta_canard_sweep`
    - `delta_htail_sweep`
    - `delta_vtail_sweep`
    - `delta_wing_sweep`
    - `gamma_canard_dihedral`
    - `gamma_htail_dihedral`
    - `gamma_vtail_dihedral`
    - `gamma_wing_dihedral`
    - `h_fuse`
    - `htail_airfoils`
    - `n_eng`
    - `n_eng_fuse`
    - `n_fuse`
    - `n_canard_sections`
    - `n_htail_sections`
    - `n_vtail_sections`
    - `n_wing_sections`
    - `r_canard_taper`
    - `r_htail_taper`
    - `r_vtail_taper`
    - `r_wing_taper`
    - `tech_highwing`
    - `vtail_airfoils`
    - `w_fuse`
    - `wing_airfoils`
    - `x_canard_span`
    - `x_canard_X_le`
    - `x_canard_Z_le`
    - `x_fuse`
    - `x_htail_span`
    - `x_htail_offset`
    - `x_vtail_span`
    - `x_vtail_offset`
    - `x_wing_span`
    - `tail_length_scaling`
    - `ac_name`
    - `wing_twists`
    - `canard_twists`
    - `htail_twists`
    - `vtail_twists`
    - `d_nacelle`
    - `x_nacelle`
    - `nacelle_def`
    """
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
    """
    Generate the aircraft geometry using a geometric object.

    Parameters
    ----------
    geom_object : object
        An object that has a `run_once` method and an `asb_aircraft_geometry_out` attribute.

    Returns
    -------
    object
        The `asb_aircraft_geometry_out` attribute of the input geometric object.

    Raises
    ------
    None
    """
    geom_object.run_once()
    return geom_object.asb_aircraft_geometry_out


def ac_narrow_body():
    """
    Generate a narrow-body aircraft geometry.

    Returns
    -------
    geometry : object
        The geometric representation of a narrow-body aircraft.

    Raises
    ------
    None
    """
    return generate_geom(ac_narrow_body_base_geom())


def ac_narrow_body_base_nofuse():
    """
    Generate the geometry of a narrow body aircraft without fuselage.

    Returns
    -------
    geometry : obj
        The generated geometry object.

    Notes
    -----
    This function uses the `ac_narrow_body_base_geom()` function to obtain the base geometry.
    It sets the `n_fuse` attribute of the base geometry object to 0.0 and then generates the final geometry using the updated base geometry.
    """
    base_geom = ac_narrow_body_base_geom()
    base_geom.n_fuse = 0.0

    return generate_geom(base_geom)


def ac_narrow_body_nofuse_notail():
    """
    Generate the geometry of a narrow-body aircraft without a fuselage or tail.

    Returns
    -------
    obj
        The generated aircraft geometry.

    "obj" is the type of object returned by the "generate_geom" function, as it was not specified in the given code.

    Raises
    ------
    None
        This function does not raise any exceptions.
    """
    base_geom = ac_narrow_body_base_geom()
    base_geom.n_fuse = 0.0
    base_geom.n_htail_sections = 0
    base_geom.n_vtail_sections = 0
    return generate_geom(base_geom)


def ac_narrow_body_long():
    """
    Generate the geometry of a long narrow body aircraft.

    Returns
    -------
    dict
        A dictionary containing the generated geometry data.

    Notes
    -----
    This function calls the `ac_narrow_body_base_geom` function to initialize the base geometry data,
    and then assigns specific values to different parameters of the base geometry. It sets the wing airfoils,
    number of wing sections, wing twists, wing dihedral, wing sweep, wing root chord, number of engines, rudder htail taper,
    rudder vtail taper, wing taper, fuselage x position, horizontal tail x position, vertical tail x position, wing span,
    tail length scaling factor, aircraft name, nacelle diameter, nacelle x position, and horizontal tail twists.

    It then calls the `generate_geom` function to generate the final geometry based on the modified base geometry.

    The generated geometry data is returned as a dictionary.
    """
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
    """
    Generate the geometric data for a narrow body aircraft with long optimization.

    Returns
    -------
    GeomData
        The geometric data for the generated aircraft.

    Notes
    -----
    This function uses a base geometry object from ac_narrow_body_base_geom() and modifies it with specific parameters for a narrow body aircraft with long optimization. The resulting geometry is then generated using generate_geom().

    The following parameters are modified in the base geometry object:
        - wing_airfoils: A list of three airfoil names for the wings.
        - n_wing_sections: The number of sections for the wings.
        - wing_twists: A list of twist angles for each wing section.
        - gamma_wing_dihedral: A list of dihedral angles for each wing section.
        - delta_wing_sweep: A list of sweep angles for each wing section.
        - chord_wing_root: The root chord length for the wings.
        - n_eng: The number of engines.
        - r_htail_taper: A list of taper ratios for the horizontal tail.
        - r_vtail_taper: A list of taper ratios for the vertical tail.
        - r_wing_taper: A list of taper ratios for each wing section.
        - x_fuse: The fuselage x-location.
        - x_htail_span: A list of span locations for the horizontal tail.
        - x_htail_offset: The x-location offset for the horizontal tail.
        - x_vtail_span: A list of span locations for the vertical tail.
        - x_vtail_offset: The x-location offset for the vertical tail.
        - x_wing_span: A list of span locations for the wings.
        - tail_length_scaling: The scaling factor for the tail length.
        - ac_name: The name of the aircraft.
        - d_nacelle: The diameter of the nacelle.
        - x_nacelle: The x-location of the nacelle.
        - htail_twists: A list of twist angles for the horizontal tail.

    Example
    -------
    >>> geom = ac_narrow_body_long_opti()
    >>> print(geom)
    GeomData(ac_name='Narrow Body Aircraft Long', ...)
    """
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
    """
    Generate the aerodynamic geometry for a concept front-swept canard.

    Returns
    -------
    aero_geom : AeroGeom
        The generated aerodynamic geometry.

    Notes
    -----
    This function imports various modules and defines several variables to generate the aerodynamic geometry for a concept front-swept canard. It then calls the `generate_geom` function with the `concept` object as input to generate the aerodynamic geometry.

    The `concept` object is defined as follows:

        - `concept.nose_def` is set using the `concept_nose()` function from the `amad.disciplines.design.resources.nose_geoms` module.
        - `concept.tail_def` is set using the `dreamer_tail()` function from the `amad.disciplines.design.resources.tail_geoms` module.
        - `concept.canard_airfoils` is a list of two airfoil names for the canard.
        - `concept.chord_canard_root` is the root chord length of the canard.
        - `concept.chord_htail_root` is the root chord length of the horizontal tail.
        - `concept.chord_vtail_root` is the root chord length of the vertical tail.
        - `concept.chord_wing_root` is the root chord length of the wing.
        - `concept.delta_canard_sweep` is a list containing the sweep angles (in degrees) of the canard.
        - `concept.delta_htail_sweep` is a list containing the sweep angles (in degrees) of the horizontal tail.
        - `concept.delta_vtail_sweep` is a list containing the sweep angles (in degrees) of the vertical tail.
        - `concept.delta_wing_sweep` is a list containing the sweep angles (in degrees) of the wing.
        - `concept.gamma_canard_dihedral` is a list containing the dihedral angles (in degrees) of the canard.
        - `concept.gamma_htail_dihedral` is a list containing the dihedral angles (in degrees) of the horizontal tail.
        - `concept.gamma_vtail_dihedral` is a list containing the dihedral angles (in degrees) of the vertical tail.
        - `concept.gamma_wing_dihedral` is a list containing the dihedral angles (in degrees) of the wing.
        - `concept.h_fuse` is the height of the fuselage.
        - `concept.htail_airfoils` is a list of two airfoil names for the horizontal tail.
        - `concept.n_fuse` is the number of fuselage sections.
        - `concept.n_canard_sections` is the number of canard sections.
        - `concept.n_htail_sections` is the number of horizontal tail sections.
        - `concept.n_vtail_sections` is the number of vertical tail sections.
        - `concept.n_wing_sections` is the number of wing sections.
        - `concept.r_canard_taper` is a list containing the taper ratios of the canard.
        - `concept.r_htail_taper` is a list containing the taper ratios of the horizontal tail.
        - `concept.r_vtail_taper` is a list containing the taper ratios of the vertical tail.
        - `concept.r_wing_taper` is a list containing the taper ratios of the wing.
        - `concept.tech_highwing` is a boolean value indicating whether the concept is a high-wing or not.
        - `concept.vtail_airfoils` is a list of two airfoil names for the vertical tail.
        - `concept.w_fuse` is the width of the fuselage.
        - `concept.wing_airfoils` is a list of two airfoil names for the wing.
        - `concept.x_canard_span` is a list containing the span locations (in meters) of the canard.
        - `concept.x_canard_X_le` is the X-coordinate location (in meters) of the leading edge of the canard.
        - `concept.x_canard_Z_le` is the Z-coordinate location (in meters) of the leading edge of the canard.
        - `concept.x_fuse` is the X-coordinate location (in meters) of the fuselage.
        - `concept.x_htail_span` is a list containing the span locations (in meters) of the horizontal tail.
        - `concept.x_htail_offset` is the offset distance (in meters) of the horizontal tail.
        - `concept.x_vtail_span` is a list containing the span locations (in meters) of the vertical tail.
        - `concept.x_vtail_offset` is the offset distance (in meters) of the vertical tail.
        - `concept.x_wing_span` is a list containing the span locations (in meters) of the wing.
        - `concept.tail_length_scaling` is the scaling factor for the tail length.
        - `concept.ac_name` is the name of the test airplane.
        - `concept.wing_twists` is a list containing the twist angles (in degrees) of the wing.
        - `concept.canard_twists` is a list containing the twist angles (in degrees) of the canard.
        - `concept.htail_twists` is a list containing the twist angles (in degrees) of the horizontal tail.
        - `concept.vtail_twists` is a list containing the twist angles (in degrees) of the vertical tail.
        - `concept.d_nacelle` is the diameter of the nacelle.
        - `concept.x_nacelle` is the X-coordinate location (in meters) of the nacelle.
        - `concept.nacelle_def` is set using the `modern_nacelle()` function from the `amad.disciplines.design.resources.nacelle_geoms` module.
    """
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
    """
    Generate a geometry for a little wing aircraft.

    Returns
    -------
    amad.disciplines.design.resources.geom.Geometry
        The generated aircraft geometry.

    Raises
    ------
    TypeError
        If any of the required modules or classes are not imported.

    Notes
    -----
    This function generates a little wing aircraft geometry by setting various parameters and calling the `generate_geom` function.

    The parameters are set as follows:
    - nose_def: The definition of the nose geometry obtained from `amad.disciplines.design.resources.nose_geoms.dreamer_nose` function.
    - tail_def: The definition of the tail geometry obtained from `amad.disciplines.design.resources.tail_geoms.dreamer_tail` function.
    - canard_airfoils: A list of airfoil names for the canard.
    - chord_canard_root: The root chord length of the canard.
    - chord_htail_root: The root chord length of the horizontal tail.
    - chord_vtail_root: The root chord length of the vertical tail.
    - chord_wing_root: The root chord length of the wing.
    - delta_canard_sweep: The sweep angle of the canard.
    - delta_htail_sweep: The sweep angle of the horizontal tail.
    - delta_vtail_sweep: The sweep angle of the vertical tail.
    - delta_wing_sweep: The sweep angle of the wing.
    - gamma_canard_dihedral: The dihedral angle of the canard.
    - gamma_htail_dihedral: The dihedral angle of the horizontal tail.
    - gamma_vtail_dihedral: The dihedral angle of the vertical tail.
    - gamma_wing_dihedral: The dihedral angle of the wing.
    - h_fuse: The height of the fuselage.
    - htail_airfoils: A list of airfoil names for the horizontal tail.
    - n_canard_sections: The number of sections for the canard.
    - n_htail_sections: The number of sections for the horizontal tail.
    - n_vtail_sections: The number of sections for the vertical tail.
    - n_wing_sections: The number of sections for the wing.
    - r_canard_taper: The taper ratio of the canard.
    - r_htail_taper: The taper ratio of the horizontal tail.
    - r_vtail_taper: The taper ratio of the vertical tail.
    - r_wing_taper: The taper ratio of the wing.
    - tech_highwing: A boolean indicating whether the aircraft is a high-wing design.
    - vtail_airfoils: A list of airfoil names for the vertical tail.
    - w_fuse: The width of the fuselage.
    - wing_airfoils: A list of airfoil names for the wing.
    - x_canard_span: The spanwise location of the canard.
    - x_canard_X_le: The longitudinal location of the canard's leading edge.
    - x_canard_Z_le: The vertical location of the canard's leading edge.
    - x_fuse: The longitudinal location of the fuselage.
    - x_htail_span: The spanwise location of the horizontal tail.
    - x_htail_offset: The horizontal offset of the horizontal tail.
    - x_vtail_span: The spanwise location of the vertical tail.
    - x_vtail_offset: The horizontal offset of the vertical tail.
    - x_wing_span: The spanwise location of the wing.
    - tail_length_scaling: A scaling factor for the tail length.
    - ac_name: The name of the aircraft.
    - wing_twists: A list of twist angles for each section of the wing.
    - canard_twists: A list of twist angles for each section of the canard.
    - htail_twists: A list of twist angles for each section of the horizontal tail.
    - vtail_twists: A list of twist angles for each section of the vertical tail.
    - d_nacelle: The diameter of the nacelle.
    - x_nacelle: The longitudinal location of the nacelle.
    - nacelle_def: The definition of the nacelle geometry.

    These parameters are used to initialize a `GenerateAeroGeom` object named `littlewing`, and the `generate_geom` function is called with this object to obtain the aircraft geometry.

    Note: This docstring assumes that the `amad.disciplines.design.resources.geom` module and the `generate_geom` function are imported correctly.
    """
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
