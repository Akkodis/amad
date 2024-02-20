from cosapp.base import Port


class AsbGeomPort(Port):
    """
    Standard port for AeroSandbox Geometry properties
    """

    def setup(self):
        """
        Set up the AeroSandBox Geometry definition.

        Parameters
        ----------
        self : object
            The object that the function is being called on.

        Returns
        -------
        None

        Raises
        ------
        N/A

        Other Parameters
        ----------------
        asb_aircraft_geometry : dictionary, optional
            The AeroSandBox Geometry definition.

        desc : str, optional
            A description of the AeroSandBox Geometry definition.
        """
        self.add_variable(
            "asb_aircraft_geometry", {}, desc="AeroSandBox Geometry definition"
        )
