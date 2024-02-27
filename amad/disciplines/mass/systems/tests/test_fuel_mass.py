from amad.disciplines.mass.systems import FuelMass


def test_fuel_mass_runonce():
    """
    Test the FuelMass class with a specific set of fuel mass values.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the total fuel mass calculated by the FuelMass class does not match the expected value.
    """
    fuel = FuelMass("fuel", model="standard")
    fuel.m_fuel_climb = 2300
    fuel.m_fuel_cruise = 17900
    fuel.m_fuel_descent = 300
    fuel.m_fuel_taxi = 500

    fuel.run_drivers()

    assert fuel.total.mass == 21000.0
