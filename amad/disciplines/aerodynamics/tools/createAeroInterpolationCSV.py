import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator


def CL_Interpolation_function(
    alpha_list=[], mach_list=[], altitude_list=[], aero_csv="aero_results_787.csv"
):
    # print(aero_csv)
    """
    Interpolate the coefficient of lift (CL) from a given set of alpha, Mach, and altitude values.

    Parameters
    ----------
    alpha_list : list, optional
        A list of alpha (angle of attack) values. Default is an empty list.
    mach_list : list, optional
        A list of Mach number values. Default is an empty list.
    altitude_list : list, optional
        A list of altitude values. Default is an empty list.
    aero_csv : str, optional
        The filename of the CSV file containing the aerodynamic results. Default is 'aero_results_787.csv'.

    Returns
    -------
    RegularGridInterpolator
        A 3-dimensional spline interpolation function that can be used to obtain interpolated values of CL.

    Raises
    ------
    None

    Notes
    -----
    This function reads the aerodynamic results from the specified CSV file and builds a 3-dimensional spline interpolation function based on the input alpha, Mach, and altitude values.

    The interpolation function can then be used to obtain interpolated values of CL for any combination of alpha, Mach, and altitude within the specified ranges.

    The interpolation is performed using numpy's RegularGridInterpolator class.
    """
    aero_results_df = pd.read_csv(aero_csv, header=0)
    # CL_list = aero_results_df["CL"].values.tolist()

    alphaG, altG, MachG = np.meshgrid(alpha_list, mach_list, altitude_list, sparse=True)

    result = []
    for alpha in alpha_list:
        block = []
        for mach in mach_list:
            element = []
            for altitude in altitude_list:
                value = aero_results_df[
                    (abs(aero_results_df["alpha"] - alpha) <= 0.001)
                    & (abs(aero_results_df["Mach"] - mach) <= 0.001)
                    & (abs(aero_results_df["altitude"] - altitude) <= 0.1)
                ]["CL"].values[0]
                element.append(value)  # add CL value to element
            block.append(element)
        result.append(block)

    CLinterp = RegularGridInterpolator((alpha_list, mach_list, altitude_list), result)

    return CLinterp


def CD_Interpolation_function(
    alpha_list=[], mach_list=[], altitude_list=[], aero_csv="aero_results_787.csv"
):
    """
    CD_Interpolation_function creates a 3-dimensional interpolation function for the coefficient of drag (CD) using the provided inputs.

    Parameters
    ----------
    alpha_list : list, optional
        A list of alpha values for interpolation (default is an empty list).
    mach_list : list, optional
        A list of Mach number values for interpolation (default is an empty list).
    altitude_list : list, optional
        A list of altitude values for interpolation (default is an empty list).
    aero_csv : str, optional
        The file name of the CSV file containing the aerodynamic results (default is 'aero_results_787.csv').

    Returns
    -------
    RegularGridInterpolator
        The 3-dimensional interpolation function for CD based on the input values.

    Raises
    ------
    None

    Notes
    -----
    This function requires the numpy library and the pandas library.

    The aerodynamic results CSV file must have columns named 'alpha', 'Mach', 'altitude', and 'CD' in order for the function to work correctly.
    """
    aero_results_df = pd.read_csv(aero_csv, header=0)
    # CD_list = aero_results_df["CD"].values.tolist()

    alphaG, altG, MachG = np.meshgrid(alpha_list, mach_list, altitude_list, sparse=True)

    result = []
    for alpha in alpha_list:
        block = []
        for mach in mach_list:
            element = []
            for altitude in altitude_list:
                value = aero_results_df[
                    (abs(aero_results_df["alpha"] - alpha) <= 0.001)
                    & (abs(aero_results_df["Mach"] - mach) <= 0.0001)
                    & (abs(aero_results_df["altitude"] - altitude) <= 0.1)
                ]["CD"].values[0]
                element.append(value)
            block.append(element)
        result.append(block)

    CDinterp = RegularGridInterpolator((alpha_list, mach_list, altitude_list), result)

    return CDinterp


def Drag_Interpolation_function(
    alpha_list=[], mach_list=[], altitude_list=[], aero_csv="aero_results_787.csv"
):
    """
    Interpolate the drag values based on alpha, Mach, and altitude.

    Parameters
    ----------
    alpha_list : list, optional
        A list of alpha values.
        Default is an empty list.

    mach_list : list, optional
        A list of Mach values.
        Default is an empty list.

    altitude_list : list, optional
        A list of altitude values.
        Default is an empty list.

    aero_csv : str, optional
        The path to the CSV file containing the aerodynamic results.
        Default is 'aero_results_787.csv'.

    Returns
    -------
    scipy.interpolate.RegularGridInterpolator
        The interpolator object that can be used to calculate interpolated drag values.

    Raises
    ------
    None

    Note
    ----
    The CSV file should have the following columns: 'alpha', 'Mach', 'altitude', 'D'.

    Example Usage
    -------------
    >>> Drag_Interpolation_function([0, 5, 10], [0.2, 0.4, 0.6], [10000, 20000, 30000], 'aero_data.csv')
    """
    aero_results_df = pd.read_csv(aero_csv, header=0)
    # D_list = aero_results_df["D"].values.tolist()

    alphaG, altG, MachG = np.meshgrid(alpha_list, mach_list, altitude_list, sparse=True)

    result = []
    for alpha in alpha_list:
        block = []
        for mach in mach_list:
            element = []
            for altitude in altitude_list:
                value = aero_results_df[
                    (abs(aero_results_df["alpha"] - alpha) <= 0.001)
                    & (abs(aero_results_df["Mach"] - mach) <= 0.0001)
                    & (abs(aero_results_df["altitude"] - altitude) <= 0.1)
                ]["D"].values[0]
                element.append(value)
            block.append(element)
        result.append(block)

    Drag_interp = RegularGridInterpolator(
        (alpha_list, mach_list, altitude_list), result
    )

    return Drag_interp
