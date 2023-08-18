from cosapp.ports import Port


class ForcePort(Port):
    """
    Standard port for forces
    """

    def setup(self):
        self.add_variable("force", 1.0, unit="N", desc="Force")
