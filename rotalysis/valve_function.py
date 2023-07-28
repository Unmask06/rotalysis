import pandas as pd


class ValveFunction:
    df_rated_cv = pd.DataFrame(
        {
            "valve_size": [0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 24],
            "equal": [
                7.35,
                11.67,
                29.17,
                46.68,
                73.52,
                116.7,
                186.7,
                291.7,
                466.8,
                735.2,
                1000,
                1521,
                2000,
                2560,
                4350,
                6000,
                8500,
            ],
            "linear": [
                8.05,
                12.84,
                20.54,
                51.35,
                80.52,
                128.4,
                205.4,
                320.9,
                513.5,
                805.2,
                1102,
                1680,
                2000,
                2560,
                4350,
                6000,
                8500,
            ],
        }
    )

    @classmethod
    def get_linear_cv(cls, valve_size):
        return cls.df_rated_cv.loc[cls.df_rated_cv["valve_size"] == valve_size, "linear"].iloc[0]

    @classmethod
    def get_equal_cv(cls, valve_size):
        return cls.df_rated_cv.loc[cls.df_rated_cv["valve_size"] == valve_size, "equal"].iloc[0]

    @classmethod
    def get_rated_cv(cls, valve_size, valve_character):
        if valve_character == "Linear":
            rated_cv = cls.get_linear_cv(valve_size)
        elif valve_character == "Equal Percentage":
            rated_cv = cls.get_equal_cv(valve_size)
        return rated_cv

    @staticmethod
    def get_actual_cv(rated_cv, cv_opening, valve_character):
        if valve_character == "Linear":
            actual_cv = rated_cv * (cv_opening / 100)
        elif valve_character == "Equal Percentage":
            actual_cv = rated_cv * (cv_opening / 100) ** 3
        elif valve_character == "Quick Opening":
            actual_cv = rated_cv * (cv_opening / 100) ** 0.5
        return actual_cv

    @staticmethod
    def get_pressure_drop(discharge_flowrate, Cv, density):
        """
        Args:
            discharge_flowrate (float): discharge_flowrate in m3/hr
            Cv (float): CV in gpm
            density (float): Density in kg.m3.

        Returns:
            float: Control valve pressure drop in bar.

        """
        Cv = Cv / 1.156
        cv_pressure_drop = (discharge_flowrate / Cv) ** 2 * (density / 1000)
        return cv_pressure_drop
