import pytest
from amad.disciplines.mass.systems import GearMass
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.tools.unit_conversion import ft2m, lb2kg


@pytest.fixture
def factory():
    def factory_impl(
        model, tech_highwing, tech_retractable, type_aircraft, mach_cruise
    ):
        syst = GearMass(name="gearmass", model=model)
        parameters = {
            "m_mto": lb2kg(mass=775000),
            "m_mlw": lb2kg(mass=496400),
            "x_mlgoleo": ft2m(length=9),
            "x_nlgoleo": ft2m(length=11),
            "x_range": 7000,
            "tech_highwing": tech_highwing,
            "tech_retractable": tech_retractable,
            "type_aircraft": type_aircraft,
            "mach_cruise": mach_cruise,
        }

        for p in parameters:
            try:
                syst[p] = parameters[p]
            except KeyError:
                continue

        return syst

    return factory_impl


@pytest.mark.parametrize(
    "model, expected_gear_mass, tech_highwing, tech_retractable, type_aircraft, mach_cruise",
    [
        ("flops", 25139.69, "False", "True", "transport", 0.8),
        ("flops", 22396.76, "False", "True", "fighter", 0.8),
        ("torenbeek", 35582.24, "False", "True", "transport", 0.8),
        ("torenbeek", 36130.74, "True", "True", "transport", 0.8),
        ("torenbeek", 21111.02, "False", "False", "transport", 0.8),
        ("torenbeek", 0.0, "False", "False", "bizjet", 0.8),
        ("torenbeek", 18932.02, "False", "True", "bizjet", 0.8),
    ],
)
def test_GearMass_run_once(
    factory,
    model,
    expected_gear_mass,
    tech_highwing,
    tech_retractable,
    type_aircraft,
    mach_cruise,
):
    gear = factory(model, tech_highwing, tech_retractable, type_aircraft, mach_cruise)
    gear.run_once()
    # print(gear.to_json())
    result = gear.total.mass
    assert result == pytest.approx(lb2kg(mass=expected_gear_mass), rel=1e-4)


def test_GearMass_models():
    """Test available model dictionary"""
    models = GearMass.models()
    assert list(models) == [
        "torenbeek",
        "flops",
        "specified",
    ]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
