from cosapp.base import System
from amad.disciplines.transverse.ports import ForcePort
import numpy


class Drag(System):
    """
    CoSApp Drag object is class for Sandbox Drag calculation.
    """

    def setup(self):
        # force 'port'
        """
        Set up the inputs and outputs for the function.

        Parameters
        ----------
        self : object
            The instance of the class.

        Returns
        -------
        None

        Outputs
        -------
        total : ForcePort
            The total force output.

        Re : float
            The Reynolds number.

        C_f : float
            The skin friction coefficient.

        CDA0 : float
            The zero drag coefficient times the projected area.

        C_D_fuse : float
            The drag coefficient of the fuselage.

        C_D_wpar : float
            The drag coefficient of the wing parasite.

        C_D_ind : float
            The drag coefficient of the induced drag.

        C_D : float
            The total drag coefficient.

        Inputs
        ------
        S : float
            Wing surface area.

        V : float
            Cruise speed in meters per second.

        AR : float
            Aspect ratio.

        V_f_fuse : float
            Fuel volume in the fuselage in cubic meters.

        C_L : float
            Lift coefficient.

        rho : float
            Density of air in kilograms per cubic meter.

        mu : float
            Air viscosity in kilograms per meter per second.

        g : float
            Gravitational acceleration in meters per second squared.

        k : float
            Form factor.

        S_wetratio : float
            Wetted area ratio.

        e : float
            Oswald efficiency factor.
        """
        self.add_output(ForcePort, "total")

        # free variables
        self.add_inward("S", desc="wing surface area")
        self.add_inward("V", desc="cruise speed, m/s")
        self.add_inward("AR", desc="aspect ratio")
        self.add_inward("V_f_fuse", desc="fuel volume in the fuselage, m^3")
        self.add_inward("C_L", desc="lift coefficient")

        # constants
        self.add_inward("rho", 1.23, desc="density of air, kg/m^3")
        self.add_inward("mu", 1.775e-5, desc="air viscosity, kg/m/s")
        self.add_inward("g", 9.81, desc="gravitational acceleration, m/s^2")
        self.add_inward("k", 1.17, desc="form factor")
        self.add_inward("S_wetratio", 2.075, desc="wetted area ratio")
        self.add_inward("e", 0.92, desc="Oswald efficiency factor")

        # computed variables
        self.add_outward("Re")
        self.add_outward("C_f")
        self.add_outward("CDA0")
        self.add_outward("C_D_fuse")
        self.add_outward("C_D_wpar")
        self.add_outward("C_D_ind")
        self.add_outward("C_D")

    def compute(self):
        # compute variables
        """
        Compute the total force on a vehicle.

        This function calculates the total force acting on a vehicle based on various parameters.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.Re = (self.rho / self.mu) * self.V * (self.S / self.AR) ** 0.5
        self.C_f = 0.074 / self.Re**0.2

        self.CDA0 = self.V_f_fuse / 10

        self.C_D_fuse = self.CDA0 / self.S
        self.C_D_wpar = self.k * self.C_f * self.S_wetratio
        self.C_D_ind = self.C_L**2 / (numpy.pi * self.AR * self.e)
        self.C_D = self.C_D_fuse + self.C_D_wpar + self.C_D_ind

        # output drag
        self.total.force = 0.5 * self.rho * self.S * self.C_D * self.V**2


if __name__ == "__main__":
    syst_drag = Drag("syst_drag")
    syst_drag.S = 14.1542
    syst_drag.V = 57.106
    syst_drag.AR = 12.1049
    syst_drag.V_f_fuse = 0.0619038
    syst_drag.C_L = 0.290128
    syst_drag.run_once()
    # TODO: avoid print
    print("Total Drag Force:", syst_drag.total.force)
