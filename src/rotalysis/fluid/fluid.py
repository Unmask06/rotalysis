"""
This module contains the class Fluid, which represents a fluid object.
"""

class Fluid:
    """
    Fluid class to represent a fluid object.
    Follows SI units for all calculations.
    m, kg, s, J, W, Pa, N, etc.
    """

    def __init__(self, density: float = 1000.0, viscosity: float = 1.0):
        """
        Initialize a Fluid object.

        Args:
            density (float, optional): kg/m^3. Defaults to 1000.0.
            viscosity (float, optional): mPa.s. Defaults to 1.0.
        """
        self.density = density
        self.viscosity = viscosity

    def __repr__(self):
        return f"Fluid(density={self.density}, viscosity={self.viscosity})"