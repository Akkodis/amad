def cylinder():
    """
    Generate the vertices of a cylinder.

    Returns
    -------
    tuple
        A tuple containing two tuples. Each inner tuple represents the coordinates of a vertex of the cylinder.
        The first three values of each vertex tuple represent the (x, y, z) coordinates, and the last value represents
        the radius of the cylinder at that point.
    """
    return (
        (0, 0, 0, 1),
        (1, 0, 0, 1),
    )


def modern_nacelle():
    """
    Create a modern nacelle configuration for a wind turbine.

    Returns
    -------
    tuple
        A tuple of tuples, where each inner tuple represents a nacelle configuration. Each inner tuple has four values, representing the position (x, y, z) and the yaw angle of the nacelle.

        - (0, 0, 0, 0.85)
        - (0, 0, 0, 0.87)
        - (0.02, 0, 0, 0.89)
        - (0.04, 0, 0, 0.905)
        - (0.08, 0, 0, 0.93)
        - (0.12, 0, 0, 0.95)
        - (0.16, 0, 0, 0.97)
        - (0.2, 0, 0, 0.98)
        - (0.4, 0, 0, 0.99)
        - (0.6, 0, 0, 1)
        - (0.8, 0, 0, 1)
        - (1.1, 0, 0, 0.99)
        - (1.4, 0, 0, 0.96)
        - (1.6, 0, 0, 0.94)
        - (2, 0, 0, 0.9)
        - (2.4, 0, 0, 0.83)
        - (2.5, 0, 0, 0.805)
        - (2.66, 0, 0, 0.75)
    """
    return (
        (0, 0, 0, 0.85),
        (0, 0, 0, 0.87),
        (0.02, 0, 0, 0.89),
        (0.04, 0, 0, 0.905),
        (0.08, 0, 0, 0.93),
        (0.12, 0, 0, 0.95),
        (0.16, 0, 0, 0.97),
        (0.2, 0, 0, 0.98),
        (0.4, 0, 0, 0.99),
        (0.6, 0, 0, 1),
        (0.8, 0, 0, 1),
        (1.1, 0, 0, 0.99),
        (1.4, 0, 0, 0.96),
        (1.6, 0, 0, 0.94),
        (2, 0, 0, 0.9),
        (2.4, 0, 0, 0.83),
        (2.5, 0, 0, 0.805),
        (2.66, 0, 0, 0.75),
    )
