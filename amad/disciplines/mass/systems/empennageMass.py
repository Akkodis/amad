from typing import Dict
import math
from amad.disciplines.mass.systems import AbstractMassComponent
from amad.disciplines.mass.systems import BaseMassClass
from amad.disciplines.mass.systems import SpecifiedMass
from amad.tools.unit_conversion import lb2kg, sqm2sqft, m2ft, ms2kt
from amad.disciplines.design.tools.averageSweep import average_sweep
from amad.disciplines.design.tools.liftingArea import lifting_area


class Torenbeek(AbstractMassComponent):
    """
    Torenbeek Empennage Mass estimation method for transport aircraft

    Parameters
    ----------
    x_htail_span : float
        The horizontal tail span.
    x_vtail_span : float
        The vertical tail span.
    delta_htail_sweep : float
        The horizontal tail sweep.
    delta_vtail_sweep : float
        The vertical tail sweep.
    r_htail_taper : float
        The horizontal tail taper ratio.
    r_vtail_taper : float
        The vertical tail taper ratio.
    chord_htail_root : float
        The chord of the horizontal tail root.
    chord_vtail_root : float
        The chord of the vertical tail root.
    v_dive : float
        The diving speed of the aircraft.
    tech_stabilizers : str
        The technology used for the stabilizers.
    tech_htail_mounting : str
        The technology used for the horizontal tail mounting.
    x_vtailroot_htail : float
        The distance between the vertical tail root and the horizontal tail.
    n_ult : int
        The ultimate load factor.
    """

    def setup(self):
        """
        Setup the object and define the lists used for calculations.

        Parameters
        ----------
        self : object
            The object being initialized.

        Returns
        -------
        None
            This function does not return anything.

        Raises
        ------
        None
            This function does not raise any exceptions.
        """
        inward_list = [
            "x_htail_span",
            "x_vtail_span",
            "delta_htail_sweep",
            "delta_vtail_sweep",
            "r_htail_taper",
            "r_vtail_taper",
            "chord_htail_root",
            "chord_vtail_root",
            "v_dive",
            "tech_stabilizers",
            "tech_htail_mounting",
            "x_vtailroot_htail",
            "n_ult",
        ]
        super().setup(inward_list)

        # computed variables
        self.add_outward("coeff_K_h")
        self.add_outward("coeff_K_v")
        self.add_outward("m_vtail")
        self.add_outward("m_htail")
        self.add_outward("m_empennage")

    # function for larger aircraft empennage
    def emp_comp_mass(self, sweep, K, area, v_dive):
        """
        Calculate the equivalent mass of the empennage components.

        Parameters
        ----------
        sweep : float
            The sweep angle of the empennage components in radians.
        K : float
            A constant factor.
        area : float
            The area of the empennage components in square meters.
        v_dive : float
            The dive speed in meters per second.

        Returns
        -------
        float
            The equivalent mass of the empennage components.
        """
        a = ((area**0.2) * v_dive) / (1000 * (math.cos(sweep) ** 0.5))
        return K * area * ((3.81 * a) - 0.287)

    def compute_mass(self):
        # tail areas
        """
        Compute the mass of the empennage (tail section) of an aircraft.

        Parameters
        ----------
        self : object
            The object representing the aircraft.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        a_htail = lifting_area(
            self.x_htail_span, self.r_htail_taper, self.chord_htail_root
        )
        a_vtail = lifting_area(
            self.x_vtail_span, self.r_vtail_taper, self.chord_vtail_root
        )

        # sweeps
        delta_htail_sweep = math.radians(
            average_sweep(spans=self.x_htail_span, sweeps=self.delta_htail_sweep)
        )
        delta_vtail_sweep = math.radians(
            average_sweep(spans=self.x_vtail_span, sweeps=self.delta_vtail_sweep)
        )

        # vtail span
        if isinstance(self.x_vtail_span, list):
            x_vtail_span = m2ft(max(self.x_vtail_span))
        else:
            x_vtail_span = m2ft(self.x_vtail_span)

        # unit conversions
        a_htail = sqm2sqft(a_htail)
        a_vtail = sqm2sqft(a_vtail)
        v_dive = ms2kt(self.v_dive)

        # calculate intermediates
        self.coeff_K_h = 1.0 if self.tech_stabilizers == "fixed" else 1.1

        if self.tech_htail_mounting == "fin":
            self.coeff_K_v = 1 + 0.15 * (
                a_htail * m2ft(self.x_vtailroot_htail) / a_vtail * x_vtail_span
            )
        else:
            self.coeff_K_v = 1.0

        # calculate empennage mass
        if v_dive <= 250.0:
            self.m_empennage = 0.04 * (self.n_ult * (a_vtail + a_htail) ** 2) ** 0.75
        else:
            self.m_htail = self.emp_comp_mass(
                sweep=delta_htail_sweep,
                K=self.coeff_K_h,
                area=a_htail,
                v_dive=v_dive,
            )
            self.m_vtail = self.emp_comp_mass(
                sweep=delta_vtail_sweep,
                K=self.coeff_K_v,
                area=a_vtail,
                v_dive=v_dive,
            )
            self.m_empennage = self.m_vtail + self.m_htail

        self.total_mass = lb2kg(mass=(self.m_empennage))


class EmpennageMass(BaseMassClass):
    """
    Empennage Mass model

    Parameters
    ----------
    name : str
        System name.
    model : str
        Computation algorithm. Options are:
            - torenbeek: Egbeert Torenbeek

    Children
    --------
    model : AbstractMassComponent
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        """
        Set up the function with the specified model and parameters.

        Parameters
        ----------
        model : str
            The model used for setup.
        **parameters : dict
            Additional parameters used for setup.

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
        Dictionary of available models.
        """
        return {
            "torenbeek": Torenbeek,
            "specified": SpecifiedMass,
        }
