from cosapp.ports import Port


class MassPort(Port):
    """
    Standard port for mass properties

    Parameters
    ----------
    None

    Returns
    -------
    int
        The standard port for mass properties.

    Raises
    ------
    None
    """

    def setup(self):
        """
        Set up the object with a mass variable.

        Parameters
        ----------
        self : object
            The object being set up.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.add_variable("mass", 1.0, unit="kg", desc="Object mass")
