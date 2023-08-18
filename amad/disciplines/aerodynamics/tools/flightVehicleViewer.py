import pyvista
from amad.disciplines.aerodynamics.tools.createFlightVehicle import CreateAirplane


def FlightVehicleViewer(flight_vehicle_geom=None, plot=True, backend="pyvista"):
    if flight_vehicle_geom is None:
        print("No flight vehicle provided")
        return None

    generator = CreateAirplane(
        aero_geom=flight_vehicle_geom,
        nacelles_enabled=True,
        generate_airfoil_polars=False,
    )
    generator.generate()
    flight_vehicle = generator.output()

    pyvista.global_theme.color = "white"
    pyvista.global_theme.background = "white"

    figure = flight_vehicle.draw(backend=backend, show=False)

    if plot is True:
        figure.plot(
            cpos="iso",
            # cpos='xy',
            # parallel_projection=True,
            pbr=True,
            metallic=1.0,
            roughness=0.4,
            zoom=1.25,
            render=True,
            lighting=True,
            ambient=0.5,
            use_transparency=True,
            opacity=0.0,
            window_size=[1280, 720],
        )

    return figure


if __name__ == "__main__":
    import os

    print(os.getcwd())
    from amad.disciplines.design.resources.aircraft_geometry_library import (
        concept_front_swept_canard as airplane_geom,
    )

    FlightVehicleViewer(flight_vehicle_geom=airplane_geom())
