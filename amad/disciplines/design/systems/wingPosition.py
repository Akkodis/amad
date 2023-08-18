import zlib
from cosapp.base import System
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane
from amad.disciplines.design.ports import AsbGeomPort


class WingPosition(System):
    """This system computes the position of the wing, using the aerodynamic center
    and design rules to position the wing correctly
    """

    def setup(self):
        self.add_input(AsbGeomPort, "geom_in")

        # self.add_inward('x_wing_le', desc='Distance from nose to wing leading edge', unit='m')
        self.add_inward("x_fuse", desc="Total Fuselage Length", unit="m")

        # Output Parameters
        self.add_outward("x_wing_le_out", unit="m")
        self.add_outward("x_ac_cache", {})
        self.add_outward("x_aerodynamic_center", dtype=(list, int, float))

        self.add_property(
            "flight_vehicle", CreateAirplane(generate_airfoil_polars=False)
        )

    def clear_cache(self):
        self.x_ac_cache.clear()

    def compute(self):
        # create a checksum from the geometry
        check_string = str(self.geom_in.asb_aircraft_geometry)
        checksum = zlib.adler32(check_string.encode("utf-8"))

        # check cache file to see if aero center values exist
        try:
            self.x_aerodynamic_center = self.x_ac_cache[checksum][
                "x_aerodynamic_center"
            ]
        except KeyError:
            # generate asb geometry
            self.flight_vehicle.ag = self.geom_in.asb_aircraft_geometry
            self.flight_vehicle.generate()

            # fetch aero centers
            self.x_aerodynamic_center = [
                w.aerodynamic_center() for w in self.flight_vehicle.airplane.wings
            ]

            # store them in the cache for later use
            self.x_ac_cache[checksum] = {
                "x_aerodynamic_center": self.x_aerodynamic_center
            }

        position_cg = (
            0.525 * self.x_fuse
        )  # Very rough approximation for demo purposes only! TODO: improve CG calculation

        # compute wing leading edge position based on aero center
        x_wing_le = self.geom_in.asb_aircraft_geometry["x_wing_disp"][0]
        self.x_wing_le_out = position_cg - (self.x_aerodynamic_center[0][0] - x_wing_le)

        # Debug
        print(
            f"aero center = {self.x_aerodynamic_center[0][0]:.2f}, x_wing_le = {x_wing_le:.5f}, x_fuse = {self.x_fuse:.2f}"
        )


if __name__ == "__main__":
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        ac_narrow_body_long as airplane_geom,
    )

    wp = WingPosition("wp")
    wp.geom_in.asb_aircraft_geometry = airplane_geom()
    wp.x_fuse = 38.01

    wp.run_once()
    print(
        f"aero center = {wp.x_aerodynamic_center[0][0]:.5f}, old wing LE = 14.4 new wing LE = {wp.x_wing_le_out:.1f}"
    )
