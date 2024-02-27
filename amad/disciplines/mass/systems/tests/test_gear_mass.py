import pytest
from amad.disciplines.mass.systems import GearMass
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.tools.unit_conversion import ft2m, lb2kg


@pytest.fixture
def factory():
    """
    Factory function for creating instances of GearMass objects.

    Parameters
    ----------
    model : str
        The model name for the GearMass object.
    tech_highwing : bool
        A flag indicating if the aircraft is a high-wing design.
    tech_retractable : bool
        A flag indicating if the aircraft has retractable landing gear.
    type_aircraft : str
        The type of the aircraft.
    mach_cruise : float
        The cruising speed in Mach number.

    Returns
    -------
    GearMass
        An instance of the GearMass object.

    Raises
    ------
    KeyError
        If any of the input parameters are not valid.

    Examples
    --------
    Create a GearMass object with a specified model and parameters:
        >>> factory('A380', True, False, 'Wide-body', 0.85)
        GearMass(name='gearmass', model='A380', m_mto=35153.7, m_mlw=22505.29, x_mlgoleo=2.7432, x_nlgoleo=3.3528, x_range=7000, tech_highwing=True, tech_retractable=False, type_aircraft='Wide-body', mach_cruise=0.85)
    """
    def factory_impl(
        model, tech_highwing, tech_retractable, type_aircraft, mach_cruise
    ):
        """
        Create a GearMass object with specified parameters.

        Parameters
        ----------
        model : str
            The name of the model for the GearMass object.
        tech_highwing : bool
            Specifies if the aircraft is a high-wing configuration.
        tech_retractable : bool
            Specifies if the landing gear is retractable.
        type_aircraft : str
            The type of the aircraft.
        mach_cruise : float
            The cruising mach number of the aircraft.

        Returns
        -------
        GearMass
            The GearMass object with the specified parameters.

        Raises
        ------
        None

        Note
        ----
        This function assumes the existence of the following conversion functions:
        - lb2kg(mass: float) -> float: Converts pounds to kilograms.
        - ft2m(length: float) -> float: Converts feet to meters.
        """
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
    """
    Test function for the calculation of the gear mass.

    Parameters
    ----------
    factory : function
        The function that creates the gear object.
    model : str
        The model of the gear.
    expected_gear_mass : float
        The expected gear mass.
    tech_highwing : str
        Whether the gear has high wing technology.
    tech_retractable : str
        Whether the gear is retractable.
    type_aircraft : str
        The type of the aircraft.
    mach_cruise : float
        The cruising Mach number.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the calculated gear mass does not match the expected gear mass.
    """
    gear = factory(model, tech_highwing, tech_retractable, type_aircraft, mach_cruise)
    gear.run_once()
    # print(gear.to_json())
    result = gear.total.mass
    assert result == pytest.approx(lb2kg(mass=expected_gear_mass), rel=1e-4)


def test_GearMass_models():
    """
    Test available model dictionary
    """
    models = GearMass.models()
    assert list(models) == [
        "torenbeek",
        "flops",
        "specified",
    ]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
