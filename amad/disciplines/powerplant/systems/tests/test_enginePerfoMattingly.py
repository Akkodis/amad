import pytest
from amad.disciplines.powerplant.systems import EnginePerfoMattingly
from amad.tools.unit_conversion import ft2m


@pytest.fixture
def factory():
    def factory_impl(dISA, Mach, altitude, max_thrust, rating, anti_ice, air_cond):
        syst = EnginePerfoMattingly(name="mattingly", altitude=altitude, dISA=dISA)
        syst.mach_current = Mach
        syst.thrust_eng = max_thrust
        syst.rating_eng = rating
        syst.anti_ice = anti_ice
        syst.air_cond = air_cond

        return syst

    return factory_impl


@pytest.mark.parametrize(
    "expected_THR, expected_THR_Mattingly, expected_CSR_Mattingly, dISA, Mach, altitude, max_thrust, rating, anti_ice, air_cond",
    [
        (
            130410.0,
            88100.10563,
            0.00001255,
            0.0,
            0.1,
            ft2m(0.0),
            130410.0,
            "MCRZ",
            "OFF",
            "OFF",
        ),
        (
            124605.0,
            29954.8367463313,
            1.91373e-05,
            20.0,
            0.8,
            ft2m(30000.0),
            130410.0,
            "MCRZ",
            "OFF",
            "OFF",
        ),
        (
            95460.12,
            17610.01803 * 0.92,
            1.88371e-05,
            40.0,
            0.8,
            ft2m(40000.0),
            130410.0,
            "MCRZ",
            "HIGH",
            "OFF",
        ),
    ],
)
def test_enginePerfo_run_once(
    factory,
    expected_THR,
    expected_THR_Mattingly,
    expected_CSR_Mattingly,
    dISA,
    Mach,
    altitude,
    max_thrust,
    rating,
    anti_ice,
    air_cond,
):
    enginemodel = factory(dISA, Mach, altitude, max_thrust, rating, anti_ice, air_cond)
    enginemodel.run_once()
    THR = enginemodel.THR
    THR_Mattingly = enginemodel.THR_Mattingly
    CSR_Mattingly = enginemodel.SFC
    # print(enginemodel.to_json())
    assert THR == pytest.approx(expected_THR, rel=1e-5)
    assert THR_Mattingly == pytest.approx(expected_THR_Mattingly, rel=1e-4)
    assert CSR_Mattingly == pytest.approx(expected_CSR_Mattingly, rel=1e-4)
