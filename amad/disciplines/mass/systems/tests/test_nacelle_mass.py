import pytest
from amad.disciplines.mass.systems import NacelleMass
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.tools.unit_conversion import lb2n, ft2m, lb2kg


@pytest.fixture
def factory():
    """
    Return a factory function that creates a NacelleMass object.

    Parameters
    ----------
    model : str
        The model of the NacelleMass object.
    tech_center_eng : float
        The tech center of the engine.
    r_bypass : float
        The bypass ratio.

    Returns
    -------
    callable
        A factory function that creates a NacelleMass object.

    Raises
    ------
    None
    """
    def factory_impl(model, tech_center_eng, r_bypass):
        """
        Create a NacelleMass object with specified parameters.

        Parameters
        ----------
        model : str
            The name of the model for the NacelleMass object.
        tech_center_eng : float
            The technical center of the engine.
        r_bypass : float
            The bypass ratio.

        Returns
        -------
        NacelleMass
            The created NacelleMass object with the specified parameters.

        Raises
        ------
        KeyError
            If a parameter is not found in the parameters dictionary.
        """
        syst = NacelleMass(name="nacmass", model=model)

        parameters = {
            "thrust_eng": lb2n(force=115600.0),
            "x_nacelle": ft2m(length=23.8),
            "d_nacelle": ft2m(length=13.6),
            "n_eng": 2,
            "tech_center_eng": tech_center_eng,
            "r_bypass": r_bypass,
        }

        for p in parameters:
            try:
                syst[p] = parameters[p]
            except KeyError:
                continue

        return syst

    return factory_impl


@pytest.mark.parametrize(
    "model, expected_nac_mass, tech_center_eng, r_bypass",
    [
        ("flops", 10758.4743, "False", 9.0),
        ("torenbeek", 15028.0000, "False", 9.0),
        ("torenbeek", 12716.0000, "False", 1.5),
    ],
)
def test_NacMass_run_once(
    factory,
    model,
    expected_nac_mass,
    tech_center_eng,
    r_bypass,
):
    """
    Test the `run_once()` method of the NacMass class.

    Parameters
    ----------
    factory : function
        A factory function that creates an instance of the NacMass class.
    model : str
        The model to use for creating the NacMass instance.
    expected_nac_mass : float
        The expected NacMass value in pounds.
    tech_center_eng : str
        A string representing whether tech center engineering is used.
    r_bypass : float
        The value of the R bypass parameter.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the resulting NacMass value is not equal to the expected value.
    """
    nac = factory(model, tech_center_eng, r_bypass)
    nac.run_once()
    print(nac.to_json())
    result = nac.total.mass
    assert result == pytest.approx(lb2kg(mass=expected_nac_mass), rel=1e-4)


def test_NacMass_models():
    """
    Test available model dictionary
    """
    models = NacelleMass.models()
    assert list(models) == [
        "torenbeek",
        "flops",
        "specified",
    ]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
