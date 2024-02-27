from cosapp.base import System
from amad.disciplines.transverse.ports import VolumePort


class FuelVolume_Weight(System):
    """
    A class representing the fuel volume and weight in an aircraft.

    Parameters
    ----------
    S : float
        The wing surface area.
    AR : float
        The aspect ratio.
    V_fuselage : float
        The volume of the fuselage in the generated aircraft by AeroSandbox.
    V_f_fuse_ratio : float, optional
        The estimated ratio between the total fuselage volume and the central fuel tank. Default is 0.05.
    tau : float, optional
        The airfoil thickness to chord ratio. Default is 0.12.
    rho_f : float
        The density of the fuel in kg/m**3.

    Outputs
    -------
    V_f_fuse : float
        The fuel volume in the fuselage.
    V_f_wing : float
        The fuel volume in the wing.
    W_f : float
        The maximum fuel weight in the aircraft based on the volume.
    """    
    def setup(self):
        # volume 'ports'
        """
        Set up the aircraft component and define its input and output ports.

        Parameters
        ----------
        self : object
            The instance of the aircraft component.

        Returns
        -------
        None

        Notes
        -----
        This method is called to set up the aircraft component and define its input and output ports. The input ports are defined using the `add_inward()` method, while the output ports are defined using the `add_output()` and `add_outward()` methods.

        - The `VolumePort` class is added as an output port with the name 'available'.
        - The wing surface area is added as an inward port named 'S' with unit 'm**2' and description 'wing surface area'.
        - The aspect ratio is added as an inward port named 'AR' with unit '' and description 'aspect ratio'.
        - The fuselage volume in the generated aircraft by AeroSandbox is added as an inward port named 'V_fuselage' with unit 'm**3' and description 'Fuselage volume in the generated aircraft by AeroSandbox'.
        - The estimated ratio between total fuselage volume and the central fuel tank is added as an inward port named 'V_f_fuse_ratio' with a default value of 0.05, unit '', and description 'Estimated ratio between total fuselage volume and the central fuel tank'.
        - The airfoil thickness to chord ratio is added as an inward port named 'tau' with a default value of 0.12 and description 'airfoil thickness to chord ratio'.
        - The density of fuel is added as an inward port named 'rho_f' with a default value of 817 kg/m**3 and description 'density of fuel'.
        - The fuel volume in the fuselage is added as an outward port named 'V_f_fuse' with unit 'm**3' and description 'fuel volume in the fuselage'.
        - The fuel volume in the wing is added as an outward port named 'V_f_wing' with unit 'm**3' and description 'fuel volume in the wing'.
        - The max fuel weight in the aircraft according to the volume in the aircraft is added as an outward port named 'W_f' with unit 'm**3' and description 'Max fuel weight in AC according to the volume in the AC'.
        """        
        self.add_output(VolumePort, "available")

        # free variables
        self.add_inward("S", unit="m**2", desc="wing surface area")
        self.add_inward("AR", unit="", desc="aspect ratio")
        self.add_inward(
            "V_fuselage",
            unit="m**3",
            desc="Fuselage volume in the  generated aircraft by AeroSandbox",
        )
        self.add_inward(
            "V_f_fuse_ratio",
            0.05,
            unit="",
            desc="Estimated ratio between total fuselage volume and the central fuel tank",
        )

        # constants
        self.add_inward("tau", 0.12, desc="airfoil thickness to chord ratio")
        self.add_inward("rho_f", 817, unit="kg/m**3", desc="density of fuel")

        # computed variables
        self.add_outward("V_f_fuse", unit="m**3", desc="fuel volume in the fuselage")
        self.add_outward("V_f_wing", unit="m**3", desc="fuel volume in the wing")
        self.add_outward(
            "W_f",
            unit="m**3",
            desc="Max fuel weight in AC according to the volume in the AC",
        )

    def compute(self):
        # compute variables
        """
        Compute the weight of the fuel.

        Parameters
        ----------
        self : object
            An instance of the class.
    
        Returns
        -------
        None
    
        Notes
        -----
        This method calculates the weight of the fuel based on the given inputs. It updates the following attributes of the instance:
        - `self.V_f_wing`: The volume of the fuel in the wings.
        - `self.V_f_fuse`: The volume of the fuel in the fuselage.
        - `self.available.volume`: The total available volume of fuel.
        - `self.W_f`: The weight of the fuel.

        The following attributes of the instance are required for the calculation:
        - `self.S`: The wing surface area.
        - `self.AR`: The wing aspect ratio.
        - `self.tau`: A coefficient.
        - `self.V_fuselage`: The volume of the fuel in the fuselage.
        - `self.V_f_fuse_ratio`: A ratio relating the fuel volume in the fuselage to the total fuel volume.
        - `self.rho_f`: The density of the fuel.

        The method does not return any result, it only updates the instance attributes.
        """        
        self.V_f_wing = (
            0.03 * self.S**1.5 / self.AR**0.5 * self.tau
        )  # linear with b and tau, quadratic with chord
        self.V_f_fuse = self.V_fuselage * self.V_f_fuse_ratio

        # output volume
        self.available.volume = self.V_f_wing + self.V_f_fuse

        # output maximum fuel mass
        self.W_f = self.available.volume * self.rho_f
