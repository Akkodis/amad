import pytest
from amad.disciplines.mass.systems import PowerplantMass
from amad.disciplines.mass.systems import AbstractMassComponent


@pytest.fixture
def factory():
    """
    Factory function to create an instance of PowerplantMass with specific parameters.

    Parameters
    ----------
    model : str
        The model of the powerplant.
    thrust_eng : float
        The thrust of the engine.
    r_bypass : float
        The bypass ratio of the engine.
    d_nacelle : float
        The diameter of the nacelle.

    Returns
    -------
    PowerplantMass
        An instance of PowerplantMass with the specified parameters.
    """
    def factory_impl(model, thrust_eng, r_bypass, d_nacelle):
        """
        Create a powerplant object with specified parameters.

        Parameters
        ----------
        model : str
            The model of the powerplant.
        thrust_eng : float
            The thrust produced by each engine in the powerplant.
        r_bypass : float
            The bypass ratio of the powerplant.
        d_nacelle : float
            The diameter of the nacelle in the powerplant.

        Returns
        -------
        PowerplantMass
            The created powerplant object.
        """
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
    """
    Test the calculation of the mass of a propulsion system.

    Parameters
    ----------
    factory : function
        A factory function that creates an instance of the engine model.
    model : str
        The engine model to be used.
    expected_eng_mass : float
        The expected mass of the engine.
    thrust_eng : float
        The thrust produced by the engine.
    r_bypass : float
        The bypass ratio of the engine.
    d_nacelle : float
        The diameter of the engine nacelle.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the calculated engine mass does not match the expected value.
    """
    eng = factory(model, thrust_eng, r_bypass, d_nacelle)
    eng.run_once()
    result = eng.total.mass
    assert result == pytest.approx(expected_eng_mass, rel=1e-4)


def test_PPmass_models():
    """
    Test available model dictionary
    """
    models = PowerplantMass.models()
    assert list(models) == ["mod-raymer", "specified"]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
