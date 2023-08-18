import pytest
from amad.disciplines.mass.systems import EmpennageMass
from amad.disciplines.mass.systems import AbstractMassComponent


@pytest.mark.parametrize(
    "expected_tail_mass, v_dive, tech_stabilizers, tech_htail_mounting",
    [
        (42.3578, 200.0, "fixed", "fuselage"),  # small aircraft < 250kt vdive
        (86.2793, 260.0, "fixed", "fuselage"),  # larger aircraft > 250kt vdive
        (92.3286, 260.0, "variable", "fuselage"),  # variable incidence stabs
        (111.6600, 260.0, "fixed", "fin"),  # fin-mounted h tail
    ],
)
def test_TailMass_run_once(
    expected_tail_mass,
    v_dive,
    tech_stabilizers,
    tech_htail_mounting,
):
    tailmass = EmpennageMass(name="tailmass", model="torenbeek")
    tailmass.v_dive = v_dive / 1.94384
    tailmass.tech_stabilizers = tech_stabilizers
    tailmass.tech_htail_mounting = tech_htail_mounting

    tailmass.x_htail_span = [4]
    tailmass.x_vtail_span = 2
    tailmass.r_htail_taper = [1]
    tailmass.r_vtail_taper = 1
    tailmass.chord_htail_root = 1.5
    tailmass.chord_vtail_root = 1.5
    tailmass.n_ult = 3.3
    tailmass.x_vtailroot_htail = 0.1524
    tailmass.delta_htail_sweep = [20]
    tailmass.delta_vtail_sweep = 20

    tailmass.run_once()
    result = tailmass.total.mass

    assert result == pytest.approx(expected_tail_mass, rel=1e-4)


def test_EmpMass_models():
    """Test available model dictionary"""
    models = EmpennageMass.models()
    assert list(models) == ["torenbeek", "specified"]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
