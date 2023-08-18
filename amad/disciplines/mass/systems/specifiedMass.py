from amad.disciplines.mass.systems import AbstractMassComponent


class SpecifiedMass(AbstractMassComponent):
    """Allows the user to specify a mass for a particular component
    instead of using the estimation method

    Inwards:
        specified_mass (float): user-specified mass
    """

    def setup(self):
        super().setup(inward_list=[])
        self.add_inward("specified_mass", 123.0)

    def compute_mass(self):
        self.total_mass = self.specified_mass
