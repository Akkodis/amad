import pandas as pd
import numpy as np
import math
import warnings
from scipy.interpolate import RegularGridInterpolator


def CL_Interpolation_function(
    alpha_list=[], mach_list=[], altitude_list=[], aero_csv="aero_results_787.csv"
):
    # print(aero_csv)
    aero_results_df = pd.read_csv(aero_csv, header=0)
    CL_list = aero_results_df["CL"].values.tolist()

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
    aero_results_df = pd.read_csv(aero_csv, header=0)
    CD_list = aero_results_df["CD"].values.tolist()

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
    aero_results_df = pd.read_csv(aero_csv, header=0)
    D_list = aero_results_df["D"].values.tolist()

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
