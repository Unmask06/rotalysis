from rotalysis import ValveFunction


class PumpFunction:
    @staticmethod
    def get_differential_pressure(discharge_pressure, suction_pressure):
        return discharge_pressure - suction_pressure

    @staticmethod
    def get_actual_cv(valve_size, cv_opening, valve_character):
        rated_cv = ValveFunction.get_rated_cv(valve_size, valve_character)
        actual_cv = ValveFunction.get_actual_cv(rated_cv, cv_opening, valve_character)
        return actual_cv

    @staticmethod
    def get_calculated_cv_drop(discharge_flowrate, actual_cv, density):
        calculated_cv_drop = ValveFunction.get_pressure_drop(discharge_flowrate, actual_cv, density)
        return calculated_cv_drop

    @staticmethod
    def get_measured_cv_drop(discharge_pressure, downstream_pressure):
        measured_cv_drop = discharge_pressure - downstream_pressure
        return measured_cv_drop

    @staticmethod
    def get_speed_variation(old_pressure, new_pressure):
        speed_variation = (new_pressure / old_pressure) ** (1 / 3)
        return speed_variation

    @staticmethod
    def get_base_hydraulic_power(discharge_flowrate, differential_pressure):
        """
        Args: discharge_flowrate in m3/hr, differential_pressure in bar
        Returns: hydraulic_power in MW
        """

        base_hydraulic_power = (
            (discharge_flowrate / 3600) * (differential_pressure * 10**5) / (10**6)
        )
        return base_hydraulic_power

    @staticmethod
    def get_proposed_hydraulic_power(base_hydralic_power, speed_variation):
        proposed_hydraulic_power = base_hydralic_power * (speed_variation**3)
        return proposed_hydraulic_power

    @staticmethod
    def get_pump_efficiency(BEP_flowrate, BEP_efficiency, actual_flowrate):
        correction_factor = 1 - ((1 - (actual_flowrate / BEP_flowrate)) ** 2)
        pump_efficiency = correction_factor * BEP_efficiency
        return pump_efficiency
