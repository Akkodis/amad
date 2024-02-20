import pytest
from amad.disciplines.mass.systems import FuselageMass
from amad.disciplines.mass.systems import AbstractMassComponent


@pytest.fixture
def factory():
    """
    Create a factory function that generates instances of the `FuselageMass` class.

    Parameters
    ----------
    model : str
        The model of the fuselage.
    tech_pressurized_fuse : bool
        Specifies if the fuselage is pressurized or not.
    tech_attached_gear : bool
        Specifies if the gear is attached to the fuselage or not.
    tech_cargo_floor : bool
        Specifies if there is a cargo floor attached to the fuselage or not.

    Returns
    -------
    FuselageMass
        An instance of the `FuselageMass` class.

    Notes
    -----
    This factory function sets the parameters of the `FuselageMass` instance based on the input values. If a parameter is not provided, it will be skipped.

    Example
    -------
    >>> factory = factory()
    >>> system = factory('model1', True, False, True)
    """
    def factory_impl(
        model, tech_pressurized_fuse, tech_attached_gear, tech_cargo_floor
    ):
        """
        Factory implementation for creating a FuselageMass object.

        Parameters
        ----------
        model : str
            The name of the model.

        tech_pressurized_fuse : bool
            Flag indicating whether the fuselage is pressurized.

        tech_attached_gear : bool
            Flag indicating whether the gear is attached.

        tech_cargo_floor : bool
            Flag indicating whether the cargo floor is present.

        Returns
        -------
        FuselageMass
            The created FuselageMass object.

        Raises
        ------
        KeyError
            If any of the required parameters are missing.
        """
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
    """
    Test the 'run_once' method of the FuseMass class.

    Parameters
    ----------
    factory : function
        A function that creates an instance of the FuseMass class.
    model : str
        The model of the fuse.
    expected_fuse_mass : float
        The expected mass of the fuse after running 'run_once'.
    tech_pressurized_fuse : str
        A string indicating whether the fuse is pressurized or not.
    tech_attached_gear : str
        A string indicating whether gear is attached to the fuse or not.
    tech_cargo_floor : str
        A string indicating whether the cargo floor is present or not.

    Raises
    ------
    AssertionError
        If the result of 'run_once' is not equal to the expected fuse mass.
    """
    fuse = factory(model, tech_pressurized_fuse, tech_attached_gear, tech_cargo_floor)
    fuse.run_once()

    result = fuse.total.mass
    assert result == pytest.approx(expected_fuse_mass, rel=1e-4)


def test_FuseMass_models():
    """
    Test available model dictionary
    """
    models = FuselageMass.models()
    assert list(models) == [
        "torenbeek",
        "flops",
        "specified",
    ]
    for stype in models.values():
        assert issubclass(stype, AbstractMassComponent)
