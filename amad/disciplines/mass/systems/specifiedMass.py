from amad.disciplines.mass.systems import AbstractMassComponent


class SpecifiedMass(AbstractMassComponent):
    """
    Allows the user to specify a mass for a particular component
    instead of using the estimation method

    Parameters
    ----------
    specified_mass : float
        User-specified mass
    """

    def setup(self):
        """
        Set up the object with a specified mass.

        Parameters
        ----------
        self : object
            The object to be set up.

        Returns
        -------
        None

        Notes
        -----
        This method should be called before using the object.

        Examples
        --------
        >>> obj = MyClass()
        >>> obj.setup()
        >>> obj.specified_mass
        123.0
        """
        super().setup(inward_list=[])
        self.add_inward("specified_mass", 123.0)

    def compute_mass(self):
        """
        Compute the mass of an object.

        Parameters
        ----------
        self : object
            The object for which the mass is being computed.

        Returns
        -------
        None

        Notes
        -----
        This function updates the `total_mass` attribute of the object with the value of the `specified_mass` attribute.
        """
        self.total_mass = self.specified_mass
