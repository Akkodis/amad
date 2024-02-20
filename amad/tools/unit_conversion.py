from typing import Union


# temperature conversion
def k2degc(temperature: Union[float, int]):
    """
    Temperature conversion Kelvin to DEG C

    Parameters
    ----------
    temperature : Union[float, int]
        temperature [K]

    Returns
    -------
    float
        Temperature [DEG C]
    """
    return temperature - 273.15


def degc2k(temperature: Union[float, int]):
    """
    Temperature conversion DEG C to Kelvin

    Parameters
    ----------
    temperature : Union[float, int]
        temperature [DEG C]

    Returns
    -------
    float
        temperature [K]
    """
    return temperature + 273.15


# mass conversions
def lb2kg(mass: Union[float, int]):
    """
    mass conversion from lbs to kg

    Parameters
    ----------
    mass : Union[float, int]
        mass in lbs

    Returns
    -------
    float
        mass in kg
    """
    return mass * 0.453592


def kg2lb(mass: Union[float, int]):
    """
    mass conversion from kg to lbs

    Parameters
    ----------
    mass : Union[float, int]
        The mass in kilograms.

    Returns
    -------
    float
        The mass in pounds.
    """
    return mass / 0.453592


# area conversions
def sqm2sqft(area: Union[float, int]):
    """
    conversion from square meter to square feet

    Parameters
    ----------
    area : Union[float, int]
        Area in square meters.

    Returns
    -------
    float
        Area in square feet.
    """
    return area * 10.7639


def sqft2sqm(area: Union[float, int]):
    """
    Conversion from square feet to square meters.

    Parameters
    ----------
    area : Union[float, int]
        The area in square feet.

    Returns
    -------
    float
        The area in square meters.
    """
    return area * 0.092903


# length conversions
def m2ft(length: Union[float, int]):
    """
    Meter to feet conversion.

    Parameters
    ----------
    length : Union[float, int]
        The length in meters.

    Returns
    -------
    float
        The length in feet.
    """
    return length * 3.28084


def ft2m(length: Union[float, int]):
    """
    feet to meter conversion

    Parameters
    ----------
    length : float or int
        Length in feet.

    Returns
    -------
    float
        Length in meters.
    """
    return length / 3.28084


def m2in(length: Union[float, int]):
    """
    meter to inch conversion

    Parameters
    ----------
    length : Union[float, int]
        The length in meters.

    Returns
    -------
    float
        The length in inches.
    """
    return length * (12 * 3.28084)


def in2m(length: Union[float, int]):
    """
    in to meter conversion

    Parameters
    ----------
    length : Union[float, int]
        Length in [in]

    Returns
    -------
    float
        Length in [m]
    """
    return length / (12 * 3.28084)


def m2nm(length: Union[float, int]):
    """
    Meter to Nautical Miles conversion.

    Parameters
    ----------
    length : Union[float, int]
        Length in meters.

    Returns
    -------
    float
        Length in nautical miles.
    """
    return length / 1852


def nm2m(length: Union[float, int]):
    """
    Nautical miles to meter conversion

    Parameters
    ----------
    length : Union[float, int]
        Length in nautical miles [NM].

    Returns
    -------
    float
        Length in meters [m].
    """
    return length * 1852


# speed conversions
def ms2kt(speed: Union[float, int]):
    """
    Speed conversion from m/s to kt.

    Parameters
    ----------
    speed : Union[float, int]
        The speed in meters per second [m/s].

    Returns
    -------
    float
        The speed in knots [kt].
    """
    return speed * 1.94384


def kt2ms(speed: Union[float, int]):
    """
    Speed conversion from kt to m/s

    Parameters
    ----------
    speed : Union[float, int]
        Speed in knots [kt]

    Returns
    -------
    float
        Speed in meters per second [m/s]
    """
    return speed / 1.94384


def ftm2ms(speed: Union[float, int]):
    """
    Speed conversion from ft/min to m/s

    Parameters
    ----------
    speed : Union[float, int]
        Speed in ft/min

    Returns
    -------
    float
        Speed in m/s
    """
    return speed * 0.00508


def ms2ftm(speed: Union[float, int]):
    """
    Speed conversion from m/s to ft/min

    Parameters
    ----------
    speed : Union[float, int]
        speed [m/s]

    Returns
    -------
    float
        speed [ft/min]
    """
    return speed / 0.00508


# force conversions
def n2lb(force: Union[float, int]):
    """
    Force conversion from Newton to lbf

    Parameters
    ----------
    force : Union[float, int]
        force [N]

    Returns
    -------
    float
        force [lbf]
    """
    return force * 0.2248089431


def lb2n(force: Union[float, int]):
    """
    Force conversion from lbf to N.

    Parameters
    ----------
    force : Union[float, int]
        The force in pounds force (lbf).

    Returns
    -------
    float
        The force in newtons (N).
    """
    return force / 0.2248089431


# pressure conversions
def pa2psi(pressure: Union[float, int]):
    """
    Pressure conversion from Pascal to PSI

    Parameters
    ----------
    pressure : Union[float, int]
        pressure [Pa]

    Returns
    -------
    float
        pressure [psi]
    """
    return pressure / 6894.76


def psi2pa(pressure: Union[float, int]):
    """
    Pressure conversion from PSI to Pascal

    Parameters
    ----------
    pressure : Union[float, int]
        pressure [psi]

    Returns
    -------
    float
        pressure [Pa]
    """
    return pressure * 6894.76


if __name__ == "__main__":
    m = 1.0
    print("Running tests...")
    print(f"{m}lb is {lb2kg(m)}kg")
    print(f"{m}lb is {lb2kg(int(m))}kg")
    print(f"{m}kg is {kg2lb(m)}lb")
    print(f"{m}kg is {kg2lb(int(m))}lb")
