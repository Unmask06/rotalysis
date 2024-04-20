"""
rotalysis.pump.curve_generator
This module contains the class PumpCurveGenerator, which generates pump and system curves.
"""

from typing import List, Tuple, Union

import numpy as np
from plotly import graph_objects as go
from scipy.optimize import curve_fit, fsolve
from .pump import Pump


def head_curve(
    flow: Union[float, List[float], np.ndarray],
    a: float,
    b: float = 0,
    noflow_head: float = 0,
):
    """
    Calculates the head curve for a given flow rate.

    Parameters:
    - flow: The flow rate at which to calculate the head curve. Can be a single value or a list/ndarray of values.
    - a: Coefficient 'a' in the head curve equation.
    - b: Coefficient 'b' in the head curve equation. Default is 0.
    - noflow_head: The head value when there is no flow. Default is 0.

    Returns:
    - The head value(s) corresponding to the given flow rate(s).
    """
    if isinstance(flow, (list, np.ndarray)):
        return [(a * q**2) + (b * q) + noflow_head for q in flow]
    return (a * flow**2) + (b * flow) + noflow_head


def solve_coefficient(
    flow: float, head: float, initial_guess: float, b: float = 0, noflow_head: float = 0
) -> float:
    """
    Solve for the coefficient 'a' in the head curve equation.

    Parameters:
    - flow: The flow rate.
    - head: The desired head value.
    - initial_guess: The initial guess for the coefficient.
    - b: Coefficient 'b' in the head curve equation, if applicable.
    - noflow_head: The head value when there is no flow.

    Returns:
    - The solution for the coefficient 'a'.
    """
    equation = lambda a: head_curve(flow, a, b, noflow_head) - head  # type: ignore
    solution = fsolve(equation, x0=initial_guess)
    return solution[0]


def get_headcurve_coefficients(flow, head) -> Tuple:
    """
    Fits a quadratic polynomial to the provided flow and head data.
    Used to generate the pump curve and system curve.

    Parameters:
    flow (list or np.array): The flow rate data points.
    head (list or np.array): The corresponding head data points.

    Returns:
    tuple: Coefficients (a, b, c) of the fitted polynomial head = a*flow^2 + b*flow + c.

    Raises:
    ValueError: If the length of flow and head arrays do not match or are empty.
    """
    flow = np.asarray(flow)
    head = np.asarray(head)

    if len(flow) != len(head):
        raise ValueError("Flow and head arrays must be of the same length.")

    if len(flow) == 0:
        raise ValueError("Flow and head arrays must not be empty.")

    if flow[0] == 0:

        constant = head[0]
        equation = lambda Q, a, b: (a * Q**2) + (b * Q) + constant
        params, _ = curve_fit(equation, flow, head)
        return (params[0], params[1], constant)

    equation = lambda Q, a, b, c: (a * Q**2) + (b * Q) + c
    params, _ = curve_fit(equation, flow, head)
    return tuple(params)
