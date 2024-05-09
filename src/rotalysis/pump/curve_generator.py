"""
rotalysis.pump.curve_generator
This module contains the class PumpCurveGenerator, which generates pump and system curves.
"""

from typing import Callable, NamedTuple

import numpy as np
from scipy.optimize import curve_fit, fsolve


class QuadCoeffs(NamedTuple):
    """
    Represents the coefficients of a quadratic equation.

    Attributes:
        a (float): The coefficient of the quadratic term.
        b (float): The coefficient of the linear term.
        c (float): The constant term.
    """

    a: float
    b: float
    c: float


def get_quadratic_equation(coeffs: QuadCoeffs) -> Callable[[float], float]:
    """
    Returns a quadratic equation as a lambda function based on given coefficients.

    Args:
        coeffs (QuadCoeffs): The coefficients of the quadratic equation.

    Returns:
        Callable[[float], float]: A lambda function representing the quadratic equation.
    """
    return lambda x: (coeffs.a * x**2) + (coeffs.b * x) + coeffs.c


def get_y_from_curve(flow: float, coeffs: QuadCoeffs) -> float:
    """
    Calculates the head or efficiency value at a given flow rate using the quadratic equation.

    Args:
        flow (float): The flow rate at which to calculate the head.
        coeffs (QuadCoeffs): The coefficients of the quadratic equation.

    Returns:
        float: The calculated head value.
    """
    return get_quadratic_equation(coeffs)(flow)


def get_headcurve_coeff_from_threepoints(
    flow: float,
    head: float,
    initial_guess: float = 1,
    b: float = 0,
    noflow_head: float = 0,
) -> QuadCoeffs:
    """
    Calculates the coefficients of the head curve equation from three points.

    Args:
        flow (float): The flow rate.
        head (float): The head value at the flow rate.
        initial_guess (float): Initial guess for coefficient 'a'.
        b (float, optional): Linear coefficient. Defaults to 0.
        noflow_head (float, optional): Head value at zero flow. Defaults to 0.

    Returns:
        QuadCoeffs: The coefficients of the head curve equation.
    """
    equation = lambda a: get_y_from_curve(flow, QuadCoeffs(a, b, noflow_head)) - head
    a = fsolve(equation, x0=initial_guess)[0]
    return QuadCoeffs(a, b, noflow_head)


def get_headcurve_coeff_from_twopoint(
    rated_flow: float, rated_head: float
) -> QuadCoeffs:
    """
    Calculates coefficients of the head curve equation from two points.

    Args:
        rated_flow (float): The rated flow rate.
        rated_head (float): The rated head value.

    Returns:
        QuadCoeffs: The coefficients of the head curve equation.
    """
    shutoff_head = rated_head * 1.3
    return get_headcurve_coeff_from_threepoints(
        rated_flow, rated_head, initial_guess=1, b=0, noflow_head=shutoff_head
    )


def get_headcurve_coeff_from_multipoint(flow, head) -> QuadCoeffs:
    """
    Fits a quadratic polynomial to the provided flow and head data.

    Args:
        flow (list or np.array): Flow rate data points.
        head (list or np.array): Corresponding head data points.

    Returns:
        QuadCoeffs: Coefficients of the fitted polynomial.

    Raises:
        ValueError: If the length of flow and head arrays do not match or are empty.
    """
    flow = np.asarray(flow)
    head = np.asarray(head)

    if len(flow) != len(head):
        raise ValueError("Flow and head arrays must be of the same length.")
    if len(flow) == 0:
        raise ValueError("Flow and head arrays must not be empty.")

    # Use the quadratic equation fit
    equation = lambda Q, a, b, c: get_quadratic_equation(QuadCoeffs(a, b, c))(Q)
    popt, _ = curve_fit(equation, flow, head)  # pylint: disable=W0632
    return QuadCoeffs(*popt)
