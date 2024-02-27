from cosapp.ports import Port


class AeroPort(Port):
    """
    Standard port for vehicle aerodynamic components
    """

    def setup(self):
        """
        Set up the variables for an aerodynamic analysis.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Variables
        ---------
        L : float
            Lift force (default value: 1.0 N).
        D : float
            Drag force (default value: 1.0 N).
        Y : float
            Lateral aerodynamic force (default value: 1.0 N).
        l : float
            Aerodynamic moment (roll axis) (default value: 1.0 nm).
        m : float
            Aerodynamic moment (pitch axis) (default value: 1.0 nm).
        n : float
            Aerodynamic moment (yaw axis) (default value: 1.0 nm).
        CD : float
            Drag coefficient (default value: 1.0).
        CL : float
            Lift coefficient (default value: 1.0).
        CY: float
            Lateral coefficient (default value: 1.0).
        Cl : float
            Aerodynamic moment coefficient (roll axis) (default value: 1.0).
        Cm : float
            Aerodynamic moment coefficient (pitch axis) (default value: 1.0).
        Cn : float
            Aerodynamic moment coefficient (yaw axis) (default value: 1.0).

        Raises
        ------
        None
        """
        self.add_variable("L", 1.0, unit="N", desc="Lift force")
        self.add_variable("D", 1.0, unit="N", desc="Drag force")
        self.add_variable("Y", 1.0, unit="N", desc="Lateral aerodynamic force")
        self.add_variable("l", 1.0, unit="nm", desc="Aerodynamic moment (roll axis)")
        self.add_variable("m", 1.0, unit="nm", desc="Aerodynamic moment (pitch axis)")
        self.add_variable("n", 1.0, unit="nm", desc="Aerodynamic moment (yaw axis)")
        self.add_variable("CD", 1.0, unit="", desc="Drag coefficient")
        self.add_variable("CL", 1.0, unit="", desc="Lift coefficient")
        self.add_variable("CY", 1.0, unit="", desc="Lateral coefficient")
        self.add_variable(
            "Cl", 1.0, unit="", desc="Aerodynamic moment coefficient (roll axis)"
        )
        self.add_variable(
            "Cm", 1.0, unit="", desc="Aerodynamic moment coefficient (pitch axis)"
        )
        self.add_variable(
            "Cn", 1.0, unit="", desc="Aerodynamic moment coefficient (yaw axis)"
        )
