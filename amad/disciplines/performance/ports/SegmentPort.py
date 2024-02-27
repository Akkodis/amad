from cosapp.ports import Port
import numpy as np


class SegmentPort(Port):
    """
    Standard port for performance properties
    """

    def setup(self):
        """
        Set up the variables for an object.

        Parameters
        ----------
        self : object
            The object to set up the variables for.

        Returns
        -------
        None

        Variables (attributes)
        ----------
        fuel_mass : float
            The mass of the object in kilograms.
        position : ndarray
            The position of the object in meters, represented as a numpy array of shape (3,).
        duration : float
            The duration of the object in seconds.
        TAS_speed : ndarray
            The speed of the object in True Air Speed in meters per second, represented as a numpy array of shape (3,).

        Raises
        ------
        None
        """
        self.add_variable("fuel_mass", 1.0, unit="kg", desc="Object mass")
        self.add_variable("position", np.zeros(3), unit="m", desc="AC position")
        self.add_variable("duration", 1.0, unit="s", desc="Object duration")
        self.add_variable("TAS_speed", np.zeros(3), unit="m/s", desc="AC speed in TAS")
