from cosapp.base import System
import math
from amad.tools.unit_conversion import m2ft
from amad.tools.atmosBADA import AtmosphereAMAD


class EnginePerfoMattingly(System):
    """
    CoSApp Engine Perfo object is class for Mattingly Engine Perfo Calculation
    """

    def setup(self, altitude=0.0, dISA=0.0):
        # free variables
        """
        Set up the parameters for calculating various properties related to engine performance and aircraft conditions.

        Parameters
        ----------
        altitude : float, optional
            The altitude at which the calculations will be performed, in meters.
            Default is 0.0.
        dISA : float, optional
            The delta ISA (International Standard Atmosphere) temperature, in Kelvin.
            Default is 0.0.

        Variables
        ---------
        z_altitude : float
            Altitude value.
            Unit: meters
            Description: Altitude
        thrust_eng : float
            Maximum thrust value.
            Unit: Newtons
            Description: Maximum given thrust
        temp_delta_ISA : float
            Delta ISA temperature value.
            Unit: Kelvin
            Description: delta ISA temperature
        mach_current : float
            Current Mach number of the aircraft.
            Unit: None
            Description: Mach, current aircraft
        rating_eng : str
            Current engine rating.
            Description: Current Engine Rating
        anti_ice : str
            Current anti-ice setting.
            Description: Current Anti-Ice setting
        air_cond : str
            Current air conditioning setting.
            Description: Current Air Conditioning setting
        f_eng_efficiency : float
            Engine efficiency factor.
            Description: Engine efficiency factor

        Properties
        ----------
        thr_reduction : float
            Thrust reduction value.
        model_coeffs : dict
            Model coefficients.
        sfc_coeffs : dict
            Specific fuel consumption coefficients.
        rating_factors : dict
            Rating factors.
        anti_ice_bleed_reductions : dict
            Anti-ice bleed reductions.
        air_cond_bleed_reductions : dict
            Air conditioning bleed reductions.
        atmos_ISA : AtmosphereAMAD
            Instance of AtmosphereAMAD class for ISA calculations.
        temp_SL_ISA : float
            Temperature at sea level for ISA conditions.
        temp_SL_ISA_DEGC : float
            Temperature at sea level for ISA conditions, in degrees Celsius.

        Outward Variables
        -----------------
        THR : -
        THR_Mattingly : -
        SFC : -
        THR_Mattingly_max : -

        Returns
        -------
        None

        Note
        ----
        This function sets up the necessary parameters and properties for subsequent calculations related to engine performance and aircraft conditions.
        """
        self.add_inward("z_altitude", altitude, unit="m", desc="Altitude")
        self.add_inward("thrust_eng", 121000.0, unit="N", desc="Maximum given thrust")
        self.add_inward("temp_delta_ISA", dISA, unit="K", desc="delta ISA temperature")
        self.add_inward("mach_current", 0.1, unit="", desc="Mach, current aircraft")
        self.add_inward("rating_eng", "MCT", desc="Current Engine Rating")
        self.add_inward("anti_ice", "OFF", desc="Current Anti-Ice setting")
        self.add_inward("air_cond", "OFF", desc="Current Air Conditionning setting")
        self.add_inward("f_eng_efficiency", 1.0, desc="Engine efficiency factor")

        # constants
        self.add_property(
            "thr_reduction", 0.008
        )  # Thrust Reduction percentage due to ISA Temperature deviation
        self.add_property(
            "model_coeffs", {"k1": 0.6, "k2": 0.568, "k3": 0.25, "k4": 1.2}
        )  # Mattingly engine model coefficients
        self.add_property(
            "sfc_coeffs", {"k1": 1.13 * 10**-5, "k2": 1.25 * 10**-5}
        )  # Mattingly scpecific fuel flow coefficients
        self.add_property(
            "rating_factors",
            {"MTO": 0.9, "MCT": 0.88, "MCLB": 0.8, "MCRZ": 0.75, "IDLE": 0.1},
        )  # Mattingly engine rating factors
        self.add_property(
            "anti_ice_bleed_reductions",
            {"OFF": 0.0, "LOW": 0.04, "MEDIUM": 0.06, "HIGH": 0.08},
        )
        self.add_property(
            "air_cond_bleed_reductions",
            {"OFF": 0.0, "LOW": 0.03, "MEDIUM": 0.05, "HIGH": 0.07},
        )

        # local computed values
        self.add_property("atmos_ISA", AtmosphereAMAD(offset_deg=0.0))

        # Sea-level properties
        self.add_property("temp_SL_ISA", self.atmos_ISA.airtemp_k(0.0))
        self.add_property("temp_SL_ISA_DEGC", self.atmos_ISA.airtemp_k(0.0) - 273.15)

        # computed variables
        self.add_outward("THR")
        self.add_outward("THR_Mattingly")
        self.add_outward("SFC")
        self.add_outward("THR_Mattingly_max")

    def compute(self):
        """
        Compute the thrust and specific fuel consumption (SFC) for an aircraft engine.

        This function calculates the thrust and SFC based on various inputs such as altitude,
        temperature, density, engine ratings, and coefficients. The thrust is determined using
        the Mattingly thrust equation, which takes into account altitude, temperature deviation
        from ISA, Mach number, and model coefficients. The SFC is calculated using a combination of Mach number,
        temperature deviation from standard lapse rate, engine efficiency, and specific fuel consumption coefficients.

        Parameters
        ----------
        self : object
            An instance of the class containing the function.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        altitude_ft = m2ft(self.z_altitude)

        # dISA-specific properties
        temp_ALT_ISA_DEGC = self.atmos_ISA.airtemp_k(self.z_altitude) - 273.15
        atmos_DISA = AtmosphereAMAD(offset_deg=self.temp_delta_ISA)
        temp_ALT_dISA = atmos_DISA.airtemp_k(self.z_altitude)
        relative_density = atmos_DISA.airdens_kgpm3(
            self.z_altitude
        ) / atmos_DISA.airdens_kgpm3(0.0)

        # init THR
        self.THR = -99999.0
        # temperature abatement
        # Reference Temperature in DEG C for Kink point
        T_ref = -0.002 * altitude_ft + 30.0
        T_ISA_DEGC = temp_ALT_ISA_DEGC
        dISA_ref = T_ref - T_ISA_DEGC
        if self.temp_delta_ISA > dISA_ref:
            self.THR = self.thrust_eng * (
                1.0 - (self.thr_reduction * (self.temp_delta_ISA - dISA_ref))
            )
        else:
            self.THR = self.thrust_eng

        # max thrust at altitude
        self.THR_Mattingly_max = (
            self.THR
            * relative_density ** self.model_coeffs["k1"]
            * (
                self.model_coeffs["k2"]
                + self.model_coeffs["k3"]
                * (self.model_coeffs["k4"] - self.mach_current) ** 3.0
            )
        )
        self.THR_Mattingly = float(
            self.THR_Mattingly_max * self.rating_factors[self.rating_eng]
        )

        # Bleed integration
        bleed_abatement = (
            self.anti_ice_bleed_reductions[self.anti_ice]
            + self.air_cond_bleed_reductions[self.air_cond]
        )
        self.THR_Mattingly = (1.0 - bleed_abatement) * self.THR_Mattingly

        # Mattingly SFC calculation
        Tref = self.temp_SL_ISA + self.temp_delta_ISA
        teta = temp_ALT_dISA / Tref
        sqrt_teta = math.sqrt(teta)
        self.SFC = (
            (self.sfc_coeffs["k1"] + self.sfc_coeffs["k2"] * self.mach_current)
            * sqrt_teta
            * self.f_eng_efficiency
        )
