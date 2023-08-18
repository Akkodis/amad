from cosapp.ports import Port


class VolumePort(Port):
    """
    Standard port for volumes
    """

    def setup(self):
        self.add_variable("volume", 1.0, unit="m**3", desc="Volume")
