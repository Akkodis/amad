from cosapp.ports import Port
import numpy as np


class SegmentPort(Port):
    """
    Standard port for performance properties
    """

    def setup(self):
        self.add_variable("fuel_mass", 1.0, unit="kg", desc="Object mass")
        self.add_variable("position", np.zeros(3), unit="m", desc="AC position")
        self.add_variable("duration", 1.0, unit="s", desc="Object duration")
        self.add_variable("TAS_speed", np.zeros(3), unit="m/s", desc="AC speed in TAS")
