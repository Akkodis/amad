import pytest
from cosapp.drivers import NonLinearSolver
from amad.disciplines.mass.systems import AircraftMass


def test_ac_mass_runonce():
    acmass = AircraftMass("acmass")
    acmass.type_aircraft = "transport"
    acmass.x_fuse = 38.08
    acmass.w_fuse = 3.76
    acmass.h_fuse = 4.01
    acmass.x_cabin = 30.02
    acmass.n_flcr = 2
    acmass.n_flatt = 4
    acmass.n_pax = 189
    acmass.n_pax_f = 0
    acmass.n_pax_j = 0
    acmass.n_pax_y = 189
    acmass.n_fuse = 1
    acmass.f_wing_var_sweep = 0
    acmass.delta_wing_sweep = [31.5, 23.5]
    acmass.delta_htail_sweep = 27
    acmass.delta_vtail_sweep = 35
    acmass.x_wing_span = [8.62, 34.32]
    acmass.x_htail_span = 14.35
    acmass.x_vtail_span = 7.16
    acmass.t_wing_root_chord = 1.21352
    acmass.tech_highwing = "False"
    acmass.delta_htail_sweep = 30
    acmass.delta_vtail_sweep = 35
    acmass.x_vtailroot_htail = 0
    acmass.tech_stabilizers = "fixed"
    acmass.tech_htail_mounting = "fuselage"
    acmass.m_mto = 79016
    acmass.m_mzf = 62721
    acmass.m_cargo = 0
    acmass.v_dive = 205.778
    acmass.mach_mo = 0.82
    acmass.x_range = 7408000
    acmass.n_ult = 3.75
    acmass.d_nacelle = 2.06
    acmass.n_eng = 2
    acmass.n_eng_fuse = 0
    acmass.r_bypass = 5.3
    acmass.thrust_eng = 107000
    acmass.tech_retractable = "True"
    acmass.tech_tail_gear = "False"
    acmass.a_fuselage = 465
    acmass.x_wing_tail_chord = 18
    acmass.tech_pressurized_fuse = "True"
    acmass.tech_attached_gear = "False"
    acmass.tech_cargo_floor = "False"
    acmass.n_fuel_tanks = 3
    acmass.a_control_surfaces = 21.77
    acmass.p_hydraulic = 20684000
    acmass.chord_wing_root = 7.88
    acmass.chord_htail_root = 4.195
    acmass.chord_vtail_root = 5.254
    acmass.r_wing_taper = [0.631, 0.252]
    acmass.r_htail_taper = 0.203
    acmass.r_vtail_taper = 0.271
    acmass.m_fuel_climb = 2300
    acmass.m_fuel_cruise = 17900
    acmass.m_fuel_descent = 300
    acmass.m_fuel_taxi = 500

    acmass.add_driver(NonLinearSolver("nls"))
    acmass.run_drivers()

    assert acmass.structure_mass == pytest.approx(22513.30886678838)
    assert acmass.powerplant_mass == pytest.approx(4467.153662024479)
    assert acmass.systems_mass == pytest.approx(11044.372644717361)
    assert acmass.payload_mass == pytest.approx(19288.9998)
    assert acmass.completion_mass == pytest.approx(818.3594619797046)
    assert acmass.total_mass == pytest.approx(79132.19443550993)
    assert acmass.m_zfw == pytest.approx(58132.194435509926)
