from typing import Dict
from amad.disciplines.mass.systems import (
    AbstractMassComponent,
    BaseMassClass,
    SpecifiedMass,
)
from amad.tools.unit_conversion import lb2kg, kg2lb, m2ft, m2in


class FLOPS(AbstractMassComponent):
    """
    FLOPS Gear Mass estimation method for various aircraft

    Parameters
    ----------
    type_aircraft : str
        The type of the aircraft.
    mach_cruise : float
        The cruise Mach number.
    m_mlw : float
        The maximum landing weight.
    m_mto : float
        The maximum takeoff weight.
    x_range : int
        The range of the aircraft.
    x_mlgoleo : int
        The location of the main landing gear oleo.
    x_nlgoleo : int
        The location of the nose landing gear oleo.
    """

    def setup(self):
        """
        Set up the class with initial values.

        Parameters
        ----------
        self : object
            The object that needs to be set up.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        inward_list = [
            "type_aircraft",
            "mach_cruise",
            "m_mlw",
            "m_mto",
            "x_range",
            "x_mlgoleo",
            "x_nlgoleo",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("wldg")
        self.add_outward("rfact")
        self.add_outward("xmlg")
        self.add_outward("xnlg")
        self.add_outward("dfte")
        self.add_outward("m_mlg")
        self.add_outward("m_nlg")
        self.add_outward("m_lg")

    def lg_mass(self, k, xlg):
        """
        Calculate the mass of a large object.

        Parameters
        ----------
        self : object
            The object instance.
        k : list or tuple
            A list or tuple of four numbers representing the parameters for the mass calculation.
        xlg : float
            The value of the large object.

        Returns
        -------
        float
            The mass of the large object.
        """
        m_lg = (k[0] - (k[1] * self.dfte)) * (self.wldg ** k[2]) * (xlg ** k[3])
        return m_lg

    def compute_mass(self):
        # calculate intermediates
        """
        Calculate the mass of an aircraft.

        Parameters
        ----------
        self : object
            The aircraft object.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.dfte = 1.0 if self.type_aircraft == "fighter" else 0.0
        self.rfact = 4e-5 if self.mach_cruise >= 1.0 else 9e-5

        if self.m_mlw == 0:
            self.wldg = kg2lb(mass=self.m_mto) * (
                1 - (self.rfact * m2ft(length=self.x_range))
            )
        else:
            self.wldg = kg2lb(mass=self.m_mlw)

        # calculate mass
        k_mlg = (0.0117, 0.0012, 0.95, 0.43)  # MLG coefficients constants exponents
        k_nlg = (0.0480, 0.0080, 0.67, 0.43)  # NLG coefficients constants exponents

        self.m_mlg = self.lg_mass(k=k_mlg, xlg=m2in(length=self.x_mlgoleo))
        self.m_nlg = self.lg_mass(k=k_nlg, xlg=m2in(length=self.x_nlgoleo))
        self.m_lg = self.m_mlg + self.m_nlg
        self.total_mass = lb2kg(mass=(self.m_lg))


class Torenbeek(AbstractMassComponent):
    """
    Torenbeek Gear estimation method for transport aircraft

    Parameters
    ----------
    m_mto : float
        Mass of the aircraft at takeoff.

    tech_highwing : bool
        True if the aircraft has a high-wing configuration, False otherwise.

    tech_retractable : bool
        True if the aircraft has retractable gear, False otherwise.

    type_aircraft : str
        Type of the aircraft.

    tech_tail_gear : bool
        True if the aircraft has a tail gear, False otherwise.
    """

    def setup(self):
        """
        Set up the class object with initial values.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        This function should be called before using any other functions of the class.

        References
        ----------
        [1] Class documentation: https://example.com/class-documentation

        Examples
        --------
        >>> obj = ClassName()
        >>> obj.setup()
        """
        inward_list = [
            "m_mto",
            "tech_highwing",
            "tech_retractable",
            "type_aircraft",
            "tech_tail_gear",
        ]
        super().setup(inward_list)

        model_constants = {
            "trainer_bizjet": {  # jet trainers and business jets
                "retractable": {
                    "main": {"A": 33.0, "B": 0.04, "C": 0.021, "D": 0},
                    "nose": {"A": 12.0, "B": 0.06, "C": 0, "D": 0},
                    "tail": {"A": 0, "B": 0, "C": 0, "D": 0},
                },
                "fixed": {  # No fixed gear model for this ac type
                    "main": {"A": 0, "B": 0, "C": 0, "D": 0},
                    "nose": {"A": 0, "B": 0, "C": 0, "D": 0},
                    "tail": {"A": 0, "B": 0, "C": 0, "D": 0},
                },
            },
            "transport": {  # Other civil airplanes
                "retractable": {
                    "main": {"A": 40, "B": 0.16, "C": 0.019, "D": 1.5e-5},
                    "nose": {"A": 20, "B": 0.1, "C": 0, "D": 2e-6},
                    "tail": {"A": 5, "B": 0, "C": 0.0031, "D": 0},
                },
                "fixed": {
                    "main": {"A": 20, "B": 0.1, "C": 0.019, "D": 0},
                    "nose": {"A": 25, "B": 0, "C": 0.0024, "D": 0},
                    "tail": {"A": 9, "B": 0, "C": 0.0024, "D": 0},
                },
            },
        }
        self.add_inward("model_lgear_constants", model_constants)

        # computed variables
        self.add_outward("k_gr")
        self.add_outward("m_mlg")
        self.add_outward("m_nlg")
        self.add_outward("m_tlg")
        self.add_outward("m_lg")

    def lg_mass(self, k, m_mto, A, B, C, D):
        """
        Calculate the mass of the liquid/gas mixture.

        Parameters
        ----------
        self : object
            The object on which this method is called.
        k : float
            Coefficient for the term (A + B * m_mto ** 0.75).
        m_mto : float
            The mass of the mixture.
        A, B, C, D : float
            Coefficients used in the calculation.

        Returns
        -------
        float
            The mass of the liquid/gas mixture.
        """
        m_lg = (
            k * ((A + (B * (m_mto**0.75)))) + (C * m_mto) + (D * (m_mto ** (3 / 2)))
        )
        return m_lg

    def compute_mass(self):
        # unit conversions
        """
        Compute the mass of an aircraft.

        Parameters
        ----------
        self : object
            The object on which the method is called.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        m_mto = kg2lb(mass=self.m_mto)

        # calculate intermediates
        self.k_gr = 1.08 if self.tech_highwing == "True" else 1.0
        retract = "retractable" if self.tech_retractable == "True" else "fixed"

        if self.type_aircraft == "trainer" or self.type_aircraft == "bizjet":
            actype = "trainer_bizjet"
        else:
            actype = "transport"

        # calculate mass
        self.m_mlg = self.lg_mass(
            k=self.k_gr,
            m_mto=m_mto,
            A=self.model_lgear_constants[actype][retract]["main"]["A"],
            B=self.model_lgear_constants[actype][retract]["main"]["B"],
            C=self.model_lgear_constants[actype][retract]["main"]["C"],
            D=self.model_lgear_constants[actype][retract]["main"]["D"],
        )
        self.m_nlg = self.lg_mass(
            k=self.k_gr,
            m_mto=m_mto,
            A=self.model_lgear_constants[actype][retract]["nose"]["A"],
            B=self.model_lgear_constants[actype][retract]["nose"]["B"],
            C=self.model_lgear_constants[actype][retract]["nose"]["C"],
            D=self.model_lgear_constants[actype][retract]["nose"]["D"],
        )

        if self.tech_tail_gear == "False":
            self.m_tlg = 0.0
        else:
            self.m_tlg = self.lg_mass(
                k=self.k_gr,
                m_mto=m_mto,
                A=self.model_lgear_constants[actype][retract]["tail"]["A"],
                B=self.model_lgear_constants[actype][retract]["tail"]["B"],
                C=self.model_lgear_constants[actype][retract]["tail"]["C"],
                D=self.model_lgear_constants[actype][retract]["tail"]["D"],
            )
        self.m_lg = self.m_mlg + self.m_nlg + self.m_tlg
        self.total_mass = lb2kg(mass=(self.m_lg))


class GearMass(BaseMassClass):
    """
    Landing Gear Mass model

    Parameters
    ----------
    name : str
        System name
    model : str
        Computation algorithm. Options are:
            - torenbeek: Egbeert Torenbeek
            - flops: NASA FLOPS
            - specified: User-specified mass

    Children
    --------
    model : AbstractMassComponent
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        """
        Setup the model with the specified parameters.

        Parameters
        ----------
        model : str
            The name of the model to set up.

        **parameters : keyword arguments
            Additional parameters for setting up the model.

        Raises
        ------
        None

        Returns
        -------
        None
        """
        super().setup(model=model, **parameters)

    @classmethod
    def models(cls) -> Dict[str, type]:
        """
        Dictionary of available models
        """
        return {
            "torenbeek": Torenbeek,
            "flops": FLOPS,
            "specified": SpecifiedMass,
        }
