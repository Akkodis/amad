import math


class AtmosphereAMAD:
    """
    Atmosphere Parameters model ISA atmosphere
    This is based on BADA 3.8 User Manual Ch. 3.1

    Speed Conversions reference:
        https://aerotoolbox.com/airspeed-conversions/

    Atmosphere Data Reference:
        https://www.digitaldutch.com/atmoscalc/
    """

    def __init__(self, alt=0.0, offset_deg=0, alt_trop=11000.0):
        """AMAD ISA Atmosphere model object based on BADA guide.

        Args:
            alt (float, optional): Altitude [m]. Defaults to 0..
            offset_deg (float, optional): delta ISA temp [K]. Defaults to 0.
            alt_trop (float, optional): Tropopause altitude [m]. Defaults to 11000..
        """
        self.alt = alt
        self.dISA = offset_deg
        self.H_trop = alt_trop

        # Constants
        # Kappa [-]
        self.kappa = 1.4
        # Real Gas Constant R [m**2 / K*s**2]
        self.R = 287.05287
        # Gravitational acceleration [m/s**2]
        self.g0 = 9.80665
        # ISA temperature gradient with altitude below tropopause [K/m]
        self.beta_t = -0.0065

        # Sea-level Standard reference values without disa
        self.T0 = 288.15
        self.p0 = 101325.0
        self.rho0 = 1.225
        self.a0 = 340.294

        # Tropopause data
        self.T_trop = self.T0 + self.dISA + self.beta_t * self.H_trop
        self.T_ISA_trop = self.T0 + self.beta_t * self.H_trop
        self.p_trop = self.p0 * ((self.T_trop - self.dISA) / self.T0) ** -(
            self.g0 / (self.beta_t * self.R)
        )

    def airtemp_k(self, alt):
        """ISA air temperature in K as function of altitude

        Args:
            alt (float): altitude [m]

        Returns:
            float: temperature [K]
        """
        if alt < self.H_trop:
            T = self.T0 + self.dISA + self.beta_t * alt
        else:
            T = self.T_trop
        return T

    def airpress_pa(self, alt):
        """ISA air pressure in Pa as function of altitude

        Args:
            alt (float): altitude [m]

        Returns:
            float: pressure [Pa]
        """
        T = self.airtemp_k(alt)
        if alt < self.H_trop:
            p = self.p0 * ((T - self.dISA) / self.T0) ** -(
                self.g0 / (self.beta_t * self.R)
            )
        else:
            exp_value = -self.g0 / (self.R * self.T_ISA_trop) * (alt - self.H_trop)
            p = self.p_trop * math.exp(exp_value)
        return p

    def airdens_kgpm3(self, alt):
        """ISA air density [kg/m**3] as function of altitude

        Args:
            alt (float): altitude [m]

        Returns:
            float: density [kg/m**3]
        """
        T = self.airtemp_k(alt)
        p = self.airpress_pa(alt)
        density = p / (self.R * T)
        return density

    def vsound_mps(self, alt):
        """Speed of Sound [m/s] as function pf altitude

        Args:
            alt (float): altitude [m]

        Returns:
            float: Speed of sound [m/s]
        """
        T = self.airtemp_k(alt)
        speedofsound = math.sqrt(self.kappa * self.R * T)
        return speedofsound

    def tas2mach(self, tas, alt):
        """Speed conversion CAS [m/s] to MA [-] for given altitude [m]

        Args:
            tas (float): speed TAS [m/s]
            alt (float): altitude [m]

        Returns:
            float: Mach speed [-]
        """
        a = self.vsound_mps(alt)
        mach = tas / a
        return mach

    def mach2tas(self, M, alt):
        """Speed conversion MA to TAS for given altitude

        Args:
            M (float): Mach speed [-]
            alt (float): altitude [m]

        Returns:
            float: speed TAS [m/s]
        """
        a = self.vsound_mps(alt)
        tas = M * a
        return tas

    def eas2tas(self, eas, alt):
        """Speed conversion EAS to TAS for given altitude

        Args:
            eas (float): speed EAS [m/s]
            alt (float): altitude [m]

        Returns:
            float: Speed TAS [m/s]
        """
        rho = self.airdens_kgpm3(alt)
        tas = eas * math.sqrt(self.rho0 / rho)
        return tas

    def tas2eas(self, tas, alt):
        """Speed conversion TAS to EAS for given altitude

        Args:
            tas (float): speed TAS [m/s]
            alt (float): altitude [m]

        Returns:
            float: speed EAS [m/s]
        """
        rho = self.airdens_kgpm3(alt)
        eas = tas * math.sqrt(rho / self.rho0)
        return eas

    def cas2tas(self, cas, alt):
        """Speed conversion CAS to TAS for given altitude

        Args:
            cas (float): speed CAS [m/s]
            alt (float): altitude [m]

        Returns:
            float: speed TAS [m/s]
        """
        rho = self.airdens_kgpm3(alt)
        p = self.airpress_pa(alt)
        mu = (self.kappa - 1.0) / self.kappa
        part1 = (1.0 + mu / 2.0 * self.rho0 / self.p0 * cas**2.0) ** (1.0 / mu)
        part2 = (1.0 + self.p0 / p * (part1 - 1.0)) ** mu - 1.0
        tas = math.sqrt(2.0 / mu * p / rho * (part2))
        return tas

    def tas2cas(self, tas, alt):
        """Speed conversion TAS to CAS for given altitude

        Args:
            tas(float): speed TAS [m/s]
            alt (float): altitude [m]

        Returns:
            float: speed CAS [m/s]
        """
        rho = self.airdens_kgpm3(alt)
        p = self.airpress_pa(alt)
        mu = (self.kappa - 1.0) / self.kappa
        part1 = (1.0 + mu / 2.0 * rho / p * tas**2.0) ** (1.0 / mu)
        part2 = (1.0 + p / self.p0 * (part1 - 1.0)) ** mu - 1.0
        cas = math.sqrt(2.0 / mu * self.p0 / self.rho0 * (part2))
        return cas

    def mach2cas(self, M, alt):
        """Speed conversion Mach to CAS for given altitude

        Args:
            M (float): Mach speed [-]
            alt (float): altitude [m]

        Returns:
            float: speed CAS [m/s]
        """
        tas = self.mach2tas(M, alt)
        cas = self.tas2cas(tas, alt)
        return cas

    def cas2mach(self, cas, alt):
        """Speed conversion CAS to Mach for given altitude

        Args:
            cas (float): speed CAS [m/s]
            alt (float): altitude [m]

        Returns:
            float: Mach speed [-]
        """
        tas = self.cas2tas(cas, alt)
        M = self.tas2mach(tas, alt)
        return M

    def crossoveralt(self, cas, mach):
        """Calculate crossover altitude for given CAS and Mach number.

            Calculates the altitude where the given CAS and Mach values
            correspond to the same true airspeed.

            (BADA User Manual 3.12, p. 12)

            Reference:
            http://www.hochwarth.com/misc/AviationCalculator.html

        Args:
            cas (float): Calibrated airspeed [m/s]
            mach (float): Mach number [-]

        Returns:
            float: Altitude [m]
        """

        # Delta: pressure ratio at the transition altitude
        delta = (
            (1.0 + 0.5 * (self.kappa - 1.0) * (cas / self.a0) ** 2)
            ** (self.kappa / (self.kappa - 1.0))
            - 1.0
        ) / (
            (1.0 + 0.5 * (self.kappa - 1.0) * mach**2)
            ** (self.kappa / (self.kappa - 1.0))
            - 1.0
        )
        # Theta: Temperature ratio at the transition altitude
        theta = delta ** (-self.beta_t * self.R / self.g0)
        return 1000.0 / 6.5 * self.T0 * (1.0 - theta)
