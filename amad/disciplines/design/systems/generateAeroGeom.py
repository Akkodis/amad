import math
from amad.disciplines.design.systems import BaseDesignComponent
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane
from amad.disciplines.design.ports import AsbGeomPort
from scipy.interpolate import interp1d


class GenerateAeroGeom(BaseDesignComponent):
    """This system creates a dictionary of design properties which will be used
    to create an AeroSandBox airplane object for aero analysis
    """

    def setup(self):
        super().setup()

        self.add_output(AsbGeomPort, "geom_out")

        self.add_inward("nose_def", value=[], dtype=(tuple, list))
        self.add_inward("tail_def", value=[], dtype=(tuple, list))
        self.add_inward("nacelle_def", value=[], dtype=(tuple, list))

        # Output Parameters
        self.add_outward("asb_aircraft_geometry_out", value={}, dtype=(dict))
        self.add_outward("x_fuse_out", unit="m")

        self.add_property(
            "flight_vehicle", CreateAirplane(generate_airfoil_polars=False)
        )

    def tip_displacement(self, span, angle, root_chord, tip_chord):
        return (
            (math.tan(math.radians(angle)) * span)
            + (0.25 * root_chord)
            - (0.25 * tip_chord)
        )

    def tip_position(self, spans, sweeps, dihedrals, chords, half_span=True):
        # root position
        tip_x = [0]
        tip_y = [0]
        tip_z = [0]

        span_ratio = 0.5 if half_span is True else 1.0

        # tip Y displacements due to span
        for span in spans:
            tip_y.append(span_ratio * span)

        # tip X displacements due to sweep
        for index, sweep in enumerate(sweeps):
            tip_x.append(
                tip_x[index]
                + self.tip_displacement(
                    span=(tip_y[index + 1] - tip_y[index]),
                    angle=sweep,
                    root_chord=chords[index],
                    tip_chord=chords[index + 1],
                )
            )

        # tip z displacements due to dihedral
        for index, dihedral in enumerate(dihedrals):
            tip_z.append(
                tip_z[index]
                + math.tan(math.radians(dihedral)) * (tip_y[index + 1] - tip_y[index])
            )

        return tip_x, tip_y, tip_z

    def tip_position_combine(self, tip_x, tip_y, tip_z, axis="Y"):
        if axis == "Z":  # axis is Z for rudders and vertical appendages
            tip_xyz = list(map(list, zip(*[tip_x, tip_z, tip_y])))
        else:
            tip_xyz = list(map(list, zip(*[tip_x, tip_y, tip_z])))

        return tip_xyz

    def calculate_chords(self, root_chord, taper_ratios):
        # create list of individual wing chords
        component_chords = [root_chord]
        for index, ratio in enumerate(taper_ratios):
            component_chords.append(ratio * component_chords[index])
        return component_chords

    def calculate_fuselage_len(self):
        if self.x_fuse <= 1:
            # compute fuselage length based on no. passengers
            # note: only applicable to single aisle!
            # TODO: replace this with something *much* better

            n_rows = math.ceil(self.n_pax / 6)  # 6 seats per row
            x_fuse = n_rows * 1.19  # statistically derived from B737

        else:
            x_fuse = self.x_fuse

        return x_fuse

    def compute(self):
        # TODO: add possibility to define multiple fuse sections
        # find lengths of external fuselage geometry definitions
        nose_def_len = self.nose_def[-1][0]
        tail_def_len = self.tail_def[-1][0]

        # compute fuselage length
        self.x_fuse_out = self.calculate_fuselage_len()

        # calculate fuselage scaled geometric paramters
        rad_fuse = (self.w_fuse + self.h_fuse) / 4  # fuse radius
        x_nose = nose_def_len * rad_fuse
        x_tail = tail_def_len * rad_fuse * self.tail_length_scaling
        x_mid = max(self.x_fuse_out - x_nose - x_tail, 0.0)

        # scale nose to fuselage radius
        nose_def_scaled = [
            [s[0] * rad_fuse, s[1] * rad_fuse, s[2] * rad_fuse, s[3] * rad_fuse]
            for s in self.nose_def
        ]

        # scale tail to fuselage radius and position on X axis correctly
        tail_def_scaled = [
            [
                (s[0] * rad_fuse) + x_nose + x_mid,
                s[1] * rad_fuse,
                s[2] * rad_fuse,
                s[3] * rad_fuse,
            ]
            for s in self.tail_def
        ]

        # concatenate all fuse sections
        if self.n_fuse < 1:
            fuse_def = None
        else:
            fuse_def = nose_def_scaled + tail_def_scaled

        # compute wing and control surface chords
        wing_chords = self.calculate_chords(
            root_chord=self.chord_wing_root, taper_ratios=self.r_wing_taper
        )
        vtail_chords = self.calculate_chords(
            root_chord=self.chord_vtail_root, taper_ratios=self.r_vtail_taper
        )
        htail_chords = self.calculate_chords(
            root_chord=self.chord_htail_root, taper_ratios=self.r_htail_taper
        )
        canard_chords = self.calculate_chords(
            root_chord=self.chord_canard_root, taper_ratios=self.r_canard_taper
        )

        # compute wing vertical position depending if high or low wing. May not be a good method.
        if self.tech_highwing == "True":
            x_wing_vert_displ = 0.8 * rad_fuse
        else:
            x_wing_vert_displ = -0.45 * rad_fuse

        # compute wing tip positions
        wingtip_x, wingtip_y, wingtip_z = self.tip_position(
            spans=self.x_wing_span,
            sweeps=self.delta_wing_sweep,
            dihedrals=self.gamma_wing_dihedral,
            chords=wing_chords,
        )
        x_wing_xyz = self.tip_position_combine(
            tip_x=wingtip_x, tip_y=wingtip_y, tip_z=wingtip_z
        )

        # compute vertical position of the empennage
        x_emp_v_displ = self.tail_def[-1][2] * rad_fuse

        # compute horizontal position of the empennage
        x_htail_le = self.x_fuse_out - self.chord_htail_root - self.x_htail_offset
        x_vtail_le = self.x_fuse_out - self.chord_vtail_root - self.x_vtail_offset

        self.asb_aircraft_geometry_out = {
            "ac_name": self.ac_name,
            "rad_fuse": rad_fuse,
            "tail_length_scaling": self.tail_length_scaling,
            "n_wing_sections": self.n_wing_sections,
            "n_htail_sections": self.n_htail_sections,
            "n_vtail_sections": self.n_vtail_sections,
            "n_canard_sections": self.n_canard_sections,
            "fuse_def": [fuse_def],
            "nacelle_def": [],
            "nacelle_xyz": [],
            "d_nacelle": self.d_nacelle,
            "n_eng": self.n_eng,
            "x_wing_disp": [0, 0, x_wing_vert_displ],
            "x_htail_disp": [x_htail_le, 0, x_emp_v_displ],
            "x_vtail_disp": [x_vtail_le, 0, x_emp_v_displ],
            "x_canard_disp": [self.x_canard_X_le, 0, self.x_canard_Z_le - rad_fuse],
            "wing_chords": wing_chords,
            "htail_chords": htail_chords,
            "vtail_chords": vtail_chords,
            "canard_chords": canard_chords,
            "wing_twists": self.wing_twists,
            "htail_twists": self.htail_twists,
            "vtail_twists": self.vtail_twists,
            "canard_twists": self.canard_twists,
            "wing_airfoils": self.wing_airfoils,
            "htail_airfoils": self.htail_airfoils,
            "vtail_airfoils": self.vtail_airfoils,
            "canard_airfoils": self.canard_airfoils,
            "x_wing_xyz": x_wing_xyz,
            "x_htail_xyz": self.tip_position_combine(
                *self.tip_position(
                    spans=self.x_htail_span,
                    sweeps=self.delta_htail_sweep,
                    dihedrals=self.gamma_htail_dihedral,
                    chords=htail_chords,
                )
            ),
            "x_vtail_xyz": self.tip_position_combine(
                *self.tip_position(
                    spans=self.x_vtail_span,
                    sweeps=self.delta_vtail_sweep,
                    dihedrals=self.gamma_vtail_dihedral,
                    chords=vtail_chords,
                    half_span=False,
                ),
                axis="Z"
            ),
            "x_canard_xyz": self.tip_position_combine(
                *self.tip_position(
                    spans=self.x_canard_span,
                    sweeps=self.delta_canard_sweep,
                    dihedrals=self.gamma_canard_dihedral,
                    chords=canard_chords,
                )
            ),
        }

        # generate asb geometry
        self.flight_vehicle.ag = self.asb_aircraft_geometry_out
        self.flight_vehicle.generate()

        # fetch aero centers
        x_aerodynamic_center = [
            w.aerodynamic_center() for w in self.flight_vehicle.airplane.wings
        ]

        # compute wing leading edge position
        position_cg = (
            0.525 * self.x_fuse_out
        )  # Very rough approximation for demo purposes only! TODO: improve CG calculation
        x_wing_le = position_cg - x_aerodynamic_center[0][0]

        # compute nacelles (only wing mounted for now)
        r_nacelle = 0.5 * self.d_nacelle
        wing_x_interp = interp1d(wingtip_y, wingtip_x)
        wing_z_interp = interp1d(wingtip_y, wingtip_z)

        n_eng_per_wing = int((self.n_eng - self.n_eng_fuse) / 2)
        nac_xyz = []

        for eng in range(1, n_eng_per_wing + 1):
            nac_y_pos = [
                (eng * 0.3) * max(wingtip_y)
            ]  # TODO: replace this with a better algorithm
            nac_x_pos = [
                wing_x_interp(y) - (self.x_nacelle * 0.75) + x_wing_le
                for y in nac_y_pos
            ]
            nac_z_pos = [
                wing_z_interp(y) - (1.1 * r_nacelle) + x_wing_vert_displ
                for y in nac_y_pos
            ]
            nac_xyz = [
                [nac_x_pos[i], nac_y_pos[i], nac_z_pos[i]]
                for i in range(len(nac_y_pos))
            ]
            nac_xyz_symmetry = [[nac[0], nac[1] * -1, nac[2]] for nac in nac_xyz]
            nac_xyz = nac_xyz + nac_xyz_symmetry

        nacelle_x_scale = self.x_nacelle / max(self.nacelle_def)[0]

        nacelle_def_scaled = [
            [
                n[0] * nacelle_x_scale,
                n[1] * r_nacelle,
                n[2] * r_nacelle,
                n[3] * r_nacelle,
            ]
            for n in self.nacelle_def
        ]

        # update the dictionary with nacelle and wing position data
        self.asb_aircraft_geometry_out["x_wing_disp"] = [
            x_wing_le,
            0,
            x_wing_vert_displ,
        ]
        self.asb_aircraft_geometry_out["nacelle_def"] = nacelle_def_scaled
        self.asb_aircraft_geometry_out["nac_xyz"] = nac_xyz

        self.geom_out.asb_aircraft_geometry = self.asb_aircraft_geometry_out


if __name__ == "__main__":
    import json
    from amad.disciplines.design.resources.nose_geoms import dreamer_nose
    from amad.disciplines.design.resources.tail_geoms import dreamer_tail

    ACGeom = GenerateAeroGeom("ACGeom")

    ACGeom.nose_def = dreamer_nose()
    ACGeom.tail_def = dreamer_tail()
    ACGeom.canard_airfoils = ["naca0010", "naca0010"]
    ACGeom.chord_canard_root = 2.5
    ACGeom.chord_htail_root = 4.195
    ACGeom.chord_vtail_root = 5.254
    ACGeom.chord_wing_root = 10
    ACGeom.delta_canard_sweep = [10]
    ACGeom.delta_htail_sweep = [30]
    ACGeom.delta_vtail_sweep = [35]
    ACGeom.delta_wing_sweep = [-25]
    ACGeom.gamma_canard_dihedral = [5]
    ACGeom.gamma_htail_dihedral = [40]
    ACGeom.gamma_vtail_dihedral = [0]
    ACGeom.gamma_wing_dihedral = [-10]
    ACGeom.h_fuse = 4.01
    ACGeom.htail_airfoils = ["naca0010", "naca0010"]
    ACGeom.n_fuse = 1
    ACGeom.n_canard_sections = 2
    ACGeom.n_htail_sections = 2
    ACGeom.n_vtail_sections = 0
    ACGeom.n_wing_sections = 2
    ACGeom.r_canard_taper = [0.3]
    ACGeom.r_htail_taper = [0.203]
    ACGeom.r_vtail_taper = [0.271]
    ACGeom.r_wing_taper = [0.129]
    ACGeom.tech_highwing = "True"
    ACGeom.vtail_airfoils = ["naca0010", "naca0010"]
    ACGeom.w_fuse = 3.76
    ACGeom.wing_airfoils = ["b737a", "b737d"]
    ACGeom.x_canard_span = [10]
    ACGeom.x_canard_X_le = 3
    ACGeom.x_canard_Z_le = 1
    ACGeom.x_fuse = 30.0
    ACGeom.x_htail_span = [10]
    ACGeom.x_htail_offset = 0
    ACGeom.x_vtail_span = [7.16]
    ACGeom.x_vtail_offset = 0
    ACGeom.x_wing_span = [34.32]
    ACGeom.tail_length_scaling = 1
    ACGeom.ac_name = "Test Airplane"
    ACGeom.wing_twists = [7, 0]
    ACGeom.canard_twists = [0, 0]
    ACGeom.htail_twists = [0, 0]
    ACGeom.vtail_twists = [0, 0]
    ACGeom.d_nacelle = 1.5
    ACGeom.x_nacelle = 2.5
    ACGeom.nacelle_def = ((0, 0, 0, 1), (1, 0, 0, 1))
    ACGeom.n_eng = 2
    ACGeom.n_eng_fuse = 0
    ACGeom.n_pax = 200

    ACGeom.run_once()
    aero_geom = ACGeom.asb_aircraft_geometry_out

    test_airplane = CreateAirplane(
        aero_geom=aero_geom, nacelles_enabled=True, generate_airfoil_polars=False
    )
    test_airplane.generate()
    airplane = test_airplane.output()

    draw_airplane = airplane.draw(backend="plotly", show=True)

    print("Outputting aircraft definition...")
    print(json.dumps(aero_geom, sort_keys=False, indent=4))
