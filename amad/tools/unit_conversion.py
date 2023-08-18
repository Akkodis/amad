from typing import Union


# temperature conversion
def k2degc(temperature: Union[float, int]):
    """Temperature conversion Kelvin to DEG C

    Args:
        temperature (Union[float, int]): temperature [K]

    Returns:
        float: Temperature [DEG C]
    """
    return temperature - 273.15


def degc2k(temperature: Union[float, int]):
    """Temperature conversion DEG C to Kelvin

    Args:
        temperature (Union[float, int]): temperature [DEG C]

    Returns:
        float: temperature [K]
    """
    return temperature + 273.15


# mass conversions
def lb2kg(mass: Union[float, int]):
    """mass conversion from lbs to kg

    Args:
        mass (Union[float, int]): mass [lbs]

    Returns:
        float: mass [kg]
    """
    return mass * 0.453592


def kg2lb(mass: Union[float, int]):
    """mass conversion from kg to lbs

    Args:
        mass (Union[float, int]): mass [kg]

    Returns:
        float: mass [lbs]
    """
    return mass / 0.453592


# area conversions
def sqm2sqft(area: Union[float, int]):
    """conversion from square meter to square feet

    Args:
        area (Union[float, int]): area [m**2]

    Returns:
        float: area [ft**2]
    """
    return area * 10.7639


def sqft2sqm(area: Union[float, int]):
    """conversion from suqre feet to square meter

    Args:
        area (Union[float, int]): area [ft**2]

    Returns:
        float: area [m**2]
    """
    return area * 0.092903


# length conversions
def m2ft(length: Union[float, int]):
    """meter to feet conversion

    Args:
        length (Union[float, int]): length [m]

    Returns:
        float: length [ft]
    """
    return length * 3.28084


def ft2m(length: Union[float, int]):
    """feet to meter conversion

    Args:
        length (Union[float, int]): length [ft]

    Returns:
        float: length [m]
    """
    return length / 3.28084


def m2in(length: Union[float, int]):
    """meter to inch conversion

    Args:
        length (Union[float, int]): length [m]

    Returns:
        float: length [in]
    """
    return length * (12 * 3.28084)


def in2m(length: Union[float, int]):
    """in to meter conversion

    Args:
        length (Union[float, int]): length [in]

    Returns:
        float: length [m]
    """
    return length / (12 * 3.28084)


def m2nm(length: Union[float, int]):
    """Meter to Nautical Miles conversion

    Args:
        length (Union[float, int]): length [m]

    Returns:
        float: length [NM]
    """
    return length / 1852


def nm2m(length: Union[float, int]):
    """nautical miles to meter conversion

    Args:
        length (Union[float, int]): length [NM]

    Returns:
        float: length [m]
    """
    return length * 1852


# speed conversions
def ms2kt(speed: Union[float, int]):
    """Speed conversion from m/s to kt

    Args:
        speed (Union[float, int]): speed [m/s]

    Returns:
        float: speed [kt]
    """
    return speed * 1.94384


def kt2ms(speed: Union[float, int]):
    """Speed conversion from kt to m/s

    Args:
        speed (Union[float, int]): speed [kt]

    Returns:
        float: speed [m/s]
    """
    return speed / 1.94384


def ftm2ms(speed: Union[float, int]):
    """Speed conversion from ft/min to m/s

    Args:
        speed (Union[float, int]): speed [ft/min]

    Returns:
        float: speed [m/s]
    """
    return speed * 0.00508


def ms2ftm(speed: Union[float, int]):
    """Speed conversion from m/s to ft/min

    Args:
        speed (Union[float, int]): speed [m/s]

    Returns:
        float: speed [ft/min]
    """
    return speed / 0.00508


# force conversions
def n2lb(force: Union[float, int]):
    """Force conversion from Newton to lbf

    Args:
        force (Union[float, int]): force [N]

    Returns:
        float: force [lbf]
    """
    return force * 0.2248089431


def lb2n(force: Union[float, int]):
    """Force conversion from lbf to N

    Args:
        force (Union[float, int]): force [lbf]

    Returns:
        float: force [N]
    """
    return force / 0.2248089431


# pressure conversions
def pa2psi(pressure: Union[float, int]):
    """Pressure conversion from Pascal to PSI

    Args:
        pressure (Union[float, int]): pressure [Pa]

    Returns:
        float: pressure [psi]
    """
    return pressure / 6894.76


def psi2pa(pressure: Union[float, int]):
    """Pressure conversion from PSI to Pascal

    Args:
        pressure (Union[float, int]): pressure [psi]

    Returns:
        float: pressure [Pa]
    """
    return pressure * 6894.76


if __name__ == "__main__":
    m = 1.0
    print("Running tests...")
    print(f"{m}lb is {lb2kg(m)}kg")
    print(f"{m}lb is {lb2kg(int(m))}kg")
    print(f"{m}kg is {kg2lb(m)}lb")
    print(f"{m}kg is {kg2lb(int(m))}lb")
