"""pump_function.py"""

from rotalysis import ValveFunction
from rotalysis.definitions import ValveCharacter

BAR_TO_PASCAL = 10**5
HOUR_TO_SECOND = 3600
WATT_TO_MEGAWATT = 10**6


class PumpFunction:
    """This class contains static functions for pump calculations."""

    @staticmethod
    def get_differential_pressure(discharge_pressure, suction_pressure):
        """
        Calculates the differential pressure across the pump.

        Args:
            discharge_pressure (float): Discharge pressure of the pump in bar.
            suction_pressure (float): Suction pressure of the pump in bar.

        Returns:
            float: Differential pressure in bar.
        """
        
        return discharge_pressure - suction_pressure

    @staticmethod
    def get_actual_cv(valve_size, cv_opening, valve_character: ValveCharacter):
        """
        Calculates the actual Cv of a valve based on its opening and character.

        Args:
            valve_size (float): Size of the valve.
            cv_opening (float): Opening of the valve in percentage.
            valve_character (str): Characteristic of the valve.

        Returns:
            float: Actual Cv of the valve.
        """
        rated_cv = ValveFunction.get_rated_cv(valve_size, valve_character)
        return ValveFunction.get_actual_cv(rated_cv, cv_opening, valve_character)

    @staticmethod
    def get_calculated_cv_drop(discharge_flowrate, actual_cv, density):
        """
        Calculates the pressure drop across a valve using its Cv and the fluid's density.

        Args:
            discharge_flowrate (float): Flow rate through the valve in m3/hr.
            actual_cv (float): Actual Cv of the valve.
            density (float): Density of the fluid in kg/m3.

        Returns:
            float: Calculated pressure drop across the valve in bar.
        """
        return ValveFunction.get_pressure_drop(discharge_flowrate, actual_cv, density)

    @staticmethod
    def get_measured_cv_drop(discharge_pressure, downstream_pressure):
        """
        Calculates the measured pressure drop across the valve.

        Args:
            discharge_pressure (float): Discharge pressure in bar.
            downstream_pressure (float): Downstream pressure in bar.

        Returns:
            float: Measured pressure drop in bar.
        """
        return discharge_pressure - downstream_pressure

    @staticmethod
    def get_speed_variation(old_pressure, new_pressure):
        """
        Calculates the required speed variation to achieve a new pressure.

        Args:
            old_pressure (float): Original pressure before variation in bar.
            new_pressure (float): Desired pressure after variation in bar.

        Returns:
            float: Required speed variation as a fraction.
        """
        return (new_pressure / old_pressure) ** (1 / 3)

    @staticmethod
    def get_base_hydraulic_power(discharge_flowrate, differential_pressure):
        """
        Calculates the hydraulic power of the pump.

        Args:
            discharge_flowrate (float): Discharge flow rate of the pump in m3/hr.
            differential_pressure (float): Differential pressure across the pump in bar.

        Returns:
            float: Hydraulic power in MW.
        """
        return (
            (discharge_flowrate / HOUR_TO_SECOND)
            * (differential_pressure * BAR_TO_PASCAL)
            / WATT_TO_MEGAWATT
        )

    @staticmethod
    def get_proposed_hydraulic_power(base_hydraulic_power, speed_variation):
        """
        Calculates the proposed hydraulic power based on speed variation.

        Args:
            base_hydraulic_power (float): Base hydraulic power in MW.
            speed_variation (float): Speed variation as a fraction.

        Returns:
            float: Proposed hydraulic power in MW.
        """
        return base_hydraulic_power * (speed_variation**3)

    @staticmethod
    def get_pump_efficiency(bep_flowrate, bep_efficiency, actual_flowrate):
        """
        Calculates the efficiency of the pump based on its actual flow rate.

        Args:
            bep_flowrate (float): Best Efficiency Point (BEP) flow rate of the pump in m3/hr.
            bep_efficiency (float): BEP efficiency of the pump as a fraction.
            actual_flowrate (float): Actual flow rate of the pump in m3/hr.

        Returns:
            float: Pump efficiency as a fraction.
        """
        correction_factor = 1 - ((1 - (actual_flowrate / bep_flowrate)) ** 2)
        return correction_factor * bep_efficiency
