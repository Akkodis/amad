from cosapp.base import System
from amad.tools.pullingFilter import pulling_filter
from amad.disciplines.mass.systems import (
    WingMass,
    EmpennageMass,
    FuselageMass,
    NacelleMass,
    GearMass,
    PowerplantMass,
    SystemsMass,
    CompletionMass,
    PayloadMass,
    FuelMass,
)


class AircraftMass(System):
    """This system calculates the total mass of the aircraft.
    Models are hard-coded for the moment so there are no arguments
    """

    def setup(self):
        model_list = [
            WingMass(name="wing", model="torenbeek"),
            EmpennageMass(name="tail", model="torenbeek"),
            FuselageMass(name="fuse", model="torenbeek"),
            NacelleMass(name="nacelle", model="torenbeek"),
            GearMass(name="gear", model="torenbeek"),
            PowerplantMass(name="eng", model="mod-raymer"),
            SystemsMass(name="sys", model="flops"),
            CompletionMass(name="compl", model="combined"),
            PayloadMass(name="payl", model="internal"),
            FuelMass(name="fuel", model="standard"),
        ]

        for model in model_list:
            inward_list = pulling_filter(model.inwards, model.outwards)
            self.add_child(model, pulling=inward_list)

        self.add_outward("structure_mass", unit="kg")
        self.add_outward("powerplant_mass", unit="kg")
        self.add_outward("systems_mass", unit="kg")
        self.add_outward("payload_mass", unit="kg")
        self.add_outward("completion_mass", unit="kg")
        self.add_outward("total_mass", unit="kg")
        self.add_outward("m_zfw", unit="kg")

    def compute(self):
        # fuel mass
        self.m_fuel = self.m_fuel_out

        # calculate mass totals
        self.structure_mass = (
            self.wing.total.mass
            + self.tail.total.mass
            + self.fuse.total.mass
            + self.nacelle.total.mass
            + self.gear.total.mass
        )
        self.powerplant_mass = self.eng.total.mass
        self.systems_mass = self.sys.total.mass
        self.payload_mass = self.payl.total.mass
        self.completion_mass = self.compl.total.mass

        self.total_mass = (
            self.structure_mass
            + self.powerplant_mass
            + self.systems_mass
            + self.payload_mass
            + self.completion_mass
            + self.m_fuel
        )

        # port outputs
        self.m_zfw = self.total_mass - self.m_fuel
