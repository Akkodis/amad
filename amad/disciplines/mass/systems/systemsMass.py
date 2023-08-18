import math
from typing import Dict
from amad.disciplines.mass.systems import (
    AbstractMassComponent,
    BaseMassClass,
    SpecifiedMass,
)
from amad.tools.unit_conversion import kg2lb, lb2kg, n2lb, m2ft, sqm2sqft, pa2psi, m2nm
from amad.disciplines.design.tools.averageSweep import average_sweep
from amad.disciplines.design.tools.liftingArea import lifting_area


class FLOPS(AbstractMassComponent):
    """FLOPS Systems Mass Models
    Reference NASA/TM-2017-219627/Volume I
    Influencing Parameters:
        x_fuse
        w_fuse
        h_fuse
        x_cabin
        n_flcr
        n_pax
        n_pax_f
        n_pax_j
        n_pax_y
        n_fuse
        f_wing_var_sweep
        delta_wing_sweep
        x_wing_span
        m_mto
        mach_mo
        x_range
        d_nacelle
        n_eng
        n_eng_fuse
        a_control_surfaces
        p_hydraulic
        m_fuel
        r_wing_taper
        chord_wing_root
    """

    def setup(self):
        inward_list = [
            "x_fuse",
            "w_fuse",
            "h_fuse",
            "x_cabin",
            "n_flcr",
            "n_pax",
            "n_pax_f",
            "n_pax_j",
            "n_pax_y",
            "n_fuse",
            "f_wing_var_sweep",
            "delta_wing_sweep",
            "x_wing_span",
            "m_mto",
            "mach_mo",
            "x_range",
            "d_nacelle",
            "n_eng",
            "n_eng_fuse",
            "a_control_surfaces",
            "p_hydraulic",
            "type_aircraft",
            "m_fuel",
            "r_wing_taper",
            "chord_wing_root",
        ]
        super().setup(inward_list)

        # calculated parameters used by FLOPS
        self.add_outward("fmxtot")
        self.add_outward("sflap")
        self.add_outward("dg")
        self.add_outward("fparea")
        self.add_outward("sw")
        self.add_outward("fnew")
        self.add_outward("xl")
        self.add_outward("wf")
        self.add_outward("b")
        self.add_outward("df")

        # calculated system weights
        self.add_outward("m_fuel_system")
        self.add_outward("m_surface_controls")
        self.add_outward("m_apu")
        self.add_outward("m_instruments")
        self.add_outward("m_hydraulics")
        self.add_outward("m_electrical")
        self.add_outward("m_avionics")
        self.add_outward("m_air_conditioning")
        self.add_outward("m_anti_ice")
        self.add_outward("m_furnishings")

    def compute_mass(self):
        # FLOPS intermediate parameters
        self.fparea = sqm2sqft(area=(self.n_fuse * self.x_fuse * self.w_fuse))
        self.fnew = self.n_eng - self.n_eng_fuse

        # unit conversions for FLOPS parameters
        self.xl = m2ft(length=self.x_fuse)
        self.wf = m2ft(length=self.w_fuse)
        self.df = m2ft(length=self.h_fuse)
        self.fmxtot = kg2lb(mass=self.m_fuel)
        self.sflap = sqm2sqft(area=self.a_control_surfaces)
        self.dg = kg2lb(mass=self.m_mto)

        # compute wing area
        self.sw = sqm2sqft(
            lifting_area(self.x_wing_span, self.r_wing_taper, self.chord_wing_root)
        )

        if isinstance(self.x_wing_span, list):
            self.b = m2ft(max(self.x_wing_span))
        else:
            self.b = m2ft(self.x_wing_span)

        # compute sweep
        if isinstance(self.delta_wing_sweep, list):
            delta_wing_sweep_av = average_sweep(
                spans=self.x_wing_span, sweeps=self.delta_wing_sweep
            )
        else:
            delta_wing_sweep_av = self.delta_wing_sweep

        if self.type_aircraft == "fighter":
            self.m_fuel_system = (
                36
                * (self.fmxtot**0.2)
                * (self.n_fuel_tanks**0.5)
                * (self.n_eng**0.4)
            )

            self.m_surface_controls = 2.95 * (self.sflap**0.45) * (self.dg**0.36)

            self.m_apu = 0.0
            print(f"INFO: No APU mass calculated for {self.type_aircraft} aircraft")

            self.m_instruments = (
                0.09
                * self.n_fuse
                * self.xl
                * self.wf
                * (
                    1
                    + (2.5 * self.n_flcr)
                    + (self.fnew * 0.1)
                    + (1.5 * self.n_eng_fuse)
                )
            )

            self.m_hydraulics = (
                0.55
                * (self.fparea + (0.27 * self.sw))
                * (1 + (0.03 * self.fnew) + (0.05 * self.n_eng_fuse))
                * ((3000 / pa2psi(pressure=self.p_hydraulic)) ** 0.35)
                * (1 + (0.04 * self.f_wing_var_sweep))
                * (self.mach_mo**0.01)
            )

            self.m_electrical = (
                10
                * ((self.xl + self.B) ** 0.85)
                * (self.n_fuse**0.27)
                * (self.mach_mo**0.1)
                * (1 + (0.1 * self.n_flcr))
            )

            self.m_avionics = (
                0.41
                * ((self.n_fuse * self.xl * self.df) ** 1.3)
                * (1 + (0.37 * self.techno_carrier))
                * self.mach_mo
            )

            self.m_air_conditioning = (0.075 * self.m_avionics) + (
                0.37
                * self.n_eng
                * (n2lb(force=self.thrust_eng) ** 0.6)
                * (self.mach_mo**0.57)
            )

            self.m_anti_ice = 0.0
            print("WARNING: Anti Ice system mass is user input for fighter aircraft")

            self.m_furnishings = (
                80 * self.n_flcr * (self.mach_mo**0.38) * (self.xl**0.25)
            )

        # transport or GA aircraft
        else:
            # specifics for GA aircraft
            if self.type_aircraft == "ga":
                self.m_fuel_system = 1.07 * (self.fmxtot**0.58) * (self.n_eng**0.43)
                self.m_surface_controls = 0.0
                self.m_apu = 0.0
                print(f"INFO: No APU mass calculated for {self.type_aircraft} aircraft")
                print("WARNING: GA Flight Controls Weight Estimation not implemented!")
            else:
                self.m_fuel_system = (
                    1.07
                    * (self.fmxtot**0.58)
                    * (self.n_eng**0.43)
                    * (self.mach_mo**0.34)
                )
                self.m_surface_controls = (
                    1.1
                    * (self.mach_mo**0.52)
                    * (self.sflap**0.6)
                    * (self.dg**0.32)
                )
                self.m_apu = (54 * (self.fparea**0.3)) + (5.4 * (self.n_pax**0.9))

            self.m_instruments = (
                0.48
                * (self.fparea**0.57)
                * (self.mach_mo**0.5)
                * (10 + (2.5 * self.n_flcr) + self.fnew + (0.15 * self.n_eng_fuse))
            )

            self.m_hydraulics = (
                0.57
                * (self.fparea + (0.27 * self.sw))
                * (1 + (0.03 * self.fnew) + (0.05 * self.n_eng_fuse))
                * ((3000 / pa2psi(pressure=self.p_hydraulic)) ** 0.35)
                * (1 + (0.04 * self.f_wing_var_sweep))
                * (self.mach_mo**0.33)
            )

            self.m_electrical = (
                92
                * (self.xl**0.4)
                * (self.wf**0.14)
                * (self.n_fuse**0.27)
                * (self.n_eng**0.69)
                * (1 + (0.044 * self.n_flcr) + (0.0015 * self.n_pax))
            )

            self.m_avionics = (
                15.8
                * (m2nm(length=self.x_range) ** 0.1)
                * (self.n_flcr**0.7)
                * (self.fparea**0.43)
            )

            self.m_air_conditioning = self.mach_mo * (
                (3.2 * ((self.fparea * self.df) ** 0.6) + (9 * (self.n_pax**0.83)))
            ) + (0.075 * self.m_avionics)

            self.m_anti_ice = (
                (self.b / math.cos(math.radians(delta_wing_sweep_av)))
                + (3.8 * m2ft(length=self.d_nacelle) * self.n_eng)
                + (1.5 * self.wf)
            )

            self.m_furnishings = (
                (127 * self.n_flcr)
                + (112 * self.n_pax_f)
                + (78 * self.n_pax_j)
                + (44 * self.n_pax_y)
                + (2.6 * m2ft(self.x_cabin) * (self.wf + self.df) * self.n_fuse)
            )

        # calculate total systems mass
        self.total_mass = lb2kg(
            mass=(
                self.m_fuel_system
                + self.m_surface_controls
                + self.m_apu
                + self.m_instruments
                + self.m_hydraulics
                + self.m_electrical
                + self.m_avionics
                + self.m_air_conditioning
                + self.m_anti_ice
                + self.m_furnishings
            )
        )


class SystemsMass(BaseMassClass):
    """Systems mass models for the following systems:


    Model List:
    ----------------------
    - name [str]: System name
    - model [str]: Computation algorithm. Options are:
        - cairns: Statistical model using thrust and bypass ratio
        - specified: User-specified mass

    Children:
    ---------
    - model:
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        super().setup(model=model, **parameters)

    @classmethod
    def models(cls) -> Dict[str, type]:
        """Dictionary of available models"""
        return {
            "flops": FLOPS,
            "specified": SpecifiedMass,
        }
