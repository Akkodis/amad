import pytest
from amad.tools.atmosBADA import AtmosphereAMAD

# test values from https://aerotoolbox.com/atmcalc/
test_cases_atmos = [
    (0.0, 0.0, 288.15, 1.225, 101325.0),
    (0.0, 1000.0, 281.65, 1.11164, 89875.0),
    (0.0, 5000.0, 255.65, 0.73612, 54020.0),
    (10.0, 0.0, 298.15, 1.18391, 101325.0),
    (10.0, 1000.0, 291.65, 1.07353, 89875.0),
    (10.0, 5000.0, 265.65, 0.70841, 54020.0),
]


@pytest.mark.parametrize("disa, alt, temp, dens, p", test_cases_atmos)
def test_AtmosphereAMAD(disa, alt, temp, dens, p):
    atmos = AtmosphereAMAD(offset_deg=disa)

    assert atmos.airtemp_k(alt) == pytest.approx(temp, rel=1e-6)
    assert atmos.airdens_kgpm3(alt) == pytest.approx(dens, rel=1e-5)
    assert atmos.airpress_pa(alt) == pytest.approx(p, rel=1e-5)


def test_speed_conversions():
    # test values from https://aerotoolbox.com/airspeed-conversions/
    disa = 10.0
    altitude = 12000.0
    mach = 0.8
    cas = 126.444
    tas = 250.0
    isa = AtmosphereAMAD(offset_deg=disa)
    tas_res = isa.mach2tas(mach, altitude)
    mach_res = isa.tas2mach(tas, altitude)
    eas_res = isa.tas2eas(tas=tas, alt=altitude)
    tas_res2 = isa.cas2tas(cas, altitude)
    cas_res = isa.tas2cas(tas, altitude)
    cas_res2 = isa.mach2cas(mach, altitude)
    mach_res2 = isa.cas2mach(cas, altitude)
    assert tas_res == pytest.approx(241.442, rel=1e-5)
    assert mach_res == pytest.approx(0.828, rel=1e-3)
    assert eas_res == pytest.approx(123.121, rel=1e-5)
    assert tas_res2 == pytest.approx(241.442, rel=1e-3)
    assert cas_res == pytest.approx(131.475, rel=1e-5)
    assert cas_res2 == pytest.approx(126.444, rel=1e-3)
    assert mach_res2 == pytest.approx(0.8, rel=1e-3)


# test values from http://www.hochwarth.com/misc/AviationCalculator.html
test_cases_xover = [
    (10.0, 0.7, 250.0, 32259.79058),
    (0.0, 0.7, 250.0, 32259.79058),
    (10.0, 0.8, 280.0, 33710.15383),
    (0.0, 0.8, 280.0, 33710.15383),
    (15.0, 0.82, 275.0, 35707.6816),
]


@pytest.mark.parametrize("disa, Mach, casxover, xoveralt_ref", test_cases_xover)
def test_xoveralt(disa, Mach, casxover, xoveralt_ref):
    casxover = casxover * 0.51444  # [kt2m/s]
    atmos = AtmosphereAMAD()
    atmos.offset_deg = disa
    xovertalt = atmos.crossoveralt(cas=casxover, mach=Mach) / 0.3048  # [m2ft]
    assert xovertalt == pytest.approx(xoveralt_ref, rel=1e-4)
