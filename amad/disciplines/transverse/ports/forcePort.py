from cosapp.ports import Port


class ForcePort(Port):
    """
    Standard port for forces
    """

    def setup(self):
        """
        Set up the object with a force variable.

        Parameters
        ----------
        self : object
            The object that the variable is being added to.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.add_variable("force", 1.0, unit="N", desc="Force")
