from cosapp.ports import Port


class MassPort(Port):
    """
    Standard port for mass properties
    """

    def setup(self):
        self.add_variable("mass", 1.0, unit="kg", desc="Object mass")
