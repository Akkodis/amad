import pytest
from amad.disciplines.mass.systems import FuselageMass
from amad.disciplines.mass.systems import AbstractMassComponent


@pytest.fixture
def factory():
    def factory_impl(
        model, tech_pressurized_fuse, tech_attached_gear, tech_cargo_floor
    ):
        syst = FuselageMass(name="fusemass", model=model)

        parameters = {
            "v_dive": 300 / 1.94384,
            "x_wing_tail_chord": 20,
            "w_fuse": 2.5,
            "h_fuse": 2.5,
            "x_fuse": 30,
            "a_fuselage": 500,
            "n_eng_fuse": 0,
            "n_fuse": 1,
            "tech_pressurized_fuse": tech_pressurized_fuse,
            "tech_attached_gear": tech_attached_gear,
            "tech_cargo_floor": tech_cargo_floor,
        }

        for p in parameters:
            try:
                syst[p] = parameters[p]
            except KeyError:
                continue

        return syst

    return factory_impl


@pytest.mark.parametrize(
    "model, expected_fuse_mass, tech_pressurized_fuse, tech_attached_gear, tech_cargo_floor",
    [
        ("torenbeek", 8280.8391, "False", "False", "False"),
        ("flops", 3221.0636, "False", "False", "False"),
        ("flops", 4445.0677, "False", "False", "True"),
    ],
)
def test_FuseMass_run_once(
    factory,
    model,
    expected_fuse_mass,
    tech_pressurized_fuse,
    tech_attached_gear,
    tech_cargo_floor,
):
    fuse = factory(model, tech_pressurized_fuse, tech_attached_gear, tech_cargo_floor)
    fuse.run_once()

    result = fuse.total.mass
    assert result == pytest.approx(expected_fuse_mass, rel=1e-4)


def test_FuseMass_models():
    """Test available model dictionary"""
    models = FuselageMass.models()
    assert list(models) == [
        "torenbeek",
        "flops",
        "specified",
    ]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
