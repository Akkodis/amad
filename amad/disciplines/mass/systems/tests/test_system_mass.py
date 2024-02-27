import pytest
from amad.tools.unit_conversion import lb2kg
from amad.tools.aircraft_params_reader import CSVFileProcess
from amad.disciplines.mass.systems import SystemsMass


def system_mass():
    """
    Calculate the system mass based on input values.

    Returns
    -------
    sysm : SystemsMass
        The system mass object containing the calculated mass information.
    """
    filename = r"amad/disciplines/mass/systems/tests/system_inputs.csv"
    pfp = CSVFileProcess(file_name_path=filename)
    input_definition = pfp.read_parameters(
        category="Mass", columns=["Parameter", "Value", "Unit"]
    )

    sysm = SystemsMass("sysm", model="flops")

    # inwards
    for parameter in input_definition:
        if input_definition[parameter]["Unit"] == "STR":
            sysm[parameter] = input_definition[parameter]["Value"]
        else:
            sysm[parameter] = float(input_definition[parameter]["Value"])

    return sysm


@pytest.mark.parametrize(
    "calc_mass, expected_sys_mass",
    [
        ("m_fuel_system", 310.6061416),
        ("m_surface_controls", 565.2935292),
        ("m_apu", 495.5996676),
        ("m_instruments", 219.957868),
        ("m_hydraulics", 523.816613294876),
        ("m_electrical", 905.3087635),
        ("m_avionics", 626.6526465),
        ("m_air_conditioning", 763.4257341),
        ("m_anti_ice", 88.05473638),
        ("m_furnishings", 6848.298004),
    ],
)
def test_system_mass_run_once(calc_mass, expected_sys_mass):
    """
    Test function for the `system_mass` function.

    Parameters
    ----------
    calc_mass : str
        The name of the system to calculate the mass for.

    expected_sys_mass : float
        The expected mass of the system.

    Raises
    ------
    AssertionError
        If the calculated mass does not match the expected mass.
    """
    sysm = system_mass()
    sysm.run_once()
    assert lb2kg(sysm.model[calc_mass]) == pytest.approx(expected_sys_mass, rel=1e-8)
