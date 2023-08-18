from cosapp.base import Port


class AsbGeomPort(Port):
    """
    Standard port for AeroSandbox Geometry properties
    """

    def setup(self):
        self.add_variable(
            "asb_aircraft_geometry", {}, desc="AeroSandBox Geometry definition"
        )
