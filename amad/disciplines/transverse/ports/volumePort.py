from cosapp.ports import Port


class VolumePort(Port):
    """
    Standard port for volumes
    """

    def setup(self):
        """
        Set up a variable.

        Parameters
        ----------
        self : object
            The object to which the variable is being added.

        Attributes
        ----------
        volume : float
            The initial value of the volume variable.

        unit : str, optional
            The unit of the volume variable. Default is 'm**3'.

        desc : str, optional
            A description of the volume variable. Default is 'Volume'.
        """
        self.add_variable("volume", 1.0, unit="m**3", desc="Volume")
