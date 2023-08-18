import pytest
from amad.disciplines.mass.systems import PowerplantMass
from amad.disciplines.mass.systems import AbstractMassComponent


@pytest.fixture
def factory():
    def factory_impl(model, thrust_eng, r_bypass, d_nacelle):
        syst = PowerplantMass(name="engmass", model=model)
        syst.n_eng = 2
        syst.mach_mo = 0.86
        syst.d_nacelle = d_nacelle
        syst.thrust_eng = thrust_eng
        syst.r_bypass = r_bypass

        return syst

    return factory_impl


@pytest.mark.parametrize(
    "model, expected_eng_mass, thrust_eng, r_bypass, d_nacelle",
    [
        ("mod-raymer", 7323.89, 160000, 12.5, 2.472),  # PW1100G
        ("mod-raymer", 13725.60, 374000, 8.7, 3.540),  # TRENT 900
        ("mod-raymer", 4930.53, 117870, 6.2, 2.076),  # CFM56-5
    ],
)
def test_PPmass_run_once(
    factory, model, expected_eng_mass, thrust_eng, r_bypass, d_nacelle
):
    eng = factory(model, thrust_eng, r_bypass, d_nacelle)
    eng.run_once()
    result = eng.total.mass
    assert result == pytest.approx(expected_eng_mass, rel=1e-4)


def test_PPmass_models():
    """Test available model dictionary"""
    models = PowerplantMass.models()
    assert list(models) == ["mod-raymer", "specified"]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
