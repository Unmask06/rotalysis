# pump.py in rotalysis folder
import os
import sys
import traceback
from pathlib import Path

sys.path.append("..")

import numpy as np
import numpy_financial as npf
import pandas as pd
import xlwings as xw

from rotalysis import Economics as ec
from rotalysis import PumpFunction as PF
from rotalysis import UtilityFunction as uf
from utils import logger


class CustomException(Exception):
    pass


class Pump:

    """
    Calculates the energy savings potential of a pump upon conversion to variable speed drive or trimming the impeller
    based on the operating data of the pump.

    Args:
        data_path (str): Path of the Excel file containing the operating data of the pump with the following sheets:
            1. process data
            2. operational data
            3. unit
            4. pump curve (optional)
        config_path (str, optional): Path of the Config.xlsx file. Defaults to "Config.xlsx".

    Returns:
        Dataframe: Energy savings summary of the pump for both VSD and impeller trimming case.

    Dependencies:
        - pump_function.py in rotalysis folder for pump static functions
        - utility_function.py in rotalysis folder for helper functions
        - valve_function.py in rotalysis folder
        - unit_converter.py in utils folder uses pint library for unit conversion
    """

    # ** Columns with units in Class Level
    mandatory_columns = {"suction_pressure": "barg", "discharge_pressure": "barg", "discharge_flowrate": "m3/h"}
    optional_columns = {
        "cv_opening": "%",
        "downstream_pressure": "barg",
        "motor_power": "kW",
        "recirculation_flow": "m3/h",
        "power_factor": "",
        "run_status": "",
        "speed": "rpm",
        "motor_amp": "A",
    }

    computed_columns = {
        "flowrate_percent": "%",
        "differential_pressure": "bar",
        "actual_cv": "gpm",
        "calculated_cv_drop": "bar",
        "measured_cv_drop": "bar",
        "cv_pressure_drop": "bar",
        "inherent_piping_loss": "bar",
        "required_differential_pressure": "bar",
        "required_speed_variation": "%",
        "base_hydraulic_power": "MW",
        "old_pump_efficiency": "%",
        "old_motor_efficiency": "%",
        "base_motor_power": "MW",
        "working_hours": "h",
        "working_percent": "%",
    }
    energy_columns = {
        "selected_measure": "",
        "selected_speed_variation": "%",
        "new_pump_efficiency": "%",
        "new_motor_efficiency": "%",
        "base_case_energy_consumption": "MWh",
        "proposed_case_energy_consumption": "MWh",
        "annual_energy_saving": "MWh",
    }
    emission_columns = {
        "base_case_emission": "tCO2e",
        "proposed_case_emission": "tCO2e",
        "ghg_reduction": "tCO2e",
        "ghg_reduction_percent": "%",
    }
    relevant_columns = list(mandatory_columns.keys()) + list(optional_columns.keys())

    def __init__(self, config_path="Config.xlsx", data_path=None):
        self.data_path = data_path
        self.config_path = config_path
        self.__set_data()
        self.logger = logger
        self.__set_config()
        self.get_emission_factor()
        self.__check_mandatory_columns()

    def __set_config(self):
        """
        INIT METHOD - Sets the config dictionary from the Config.xlsx file.
        """

        dfconfig = pd.read_excel(self.config_path, sheet_name="PumpConfig1", header=0)
        dfconfig = dfconfig.iloc[:, :3].dropna(subset=["parameter"])
        dfconfig.set_index("parameter", inplace=True)
        self.config = dfconfig.to_dict("index")

    def get_emission_factor(self):
        """
        Returns the emission factor from the config file.

        Returns:
            float: emission factor
        """
        dfemission_factor = pd.read_excel(self.config_path, sheet_name="EmissionFactor", header=0)
        dfemission_factor = dfemission_factor.iloc[:, :2].dropna(subset=["emission_factor"])
        dfemission_factor.set_index("site", inplace=True)
        self.dfemission_factor = dfemission_factor.to_dict("index")

    def __set_data(self):
        """
        INIT METHOD - Sets the process data, operational data and unit dictionary from the Excel file.

        """
        if self.data_path is None:
            raise ValueError("data_path is not defined.")

        # Set Pump's process data
        dfprocess = pd.read_excel(self.data_path, sheet_name="process data", header=0)
        dfprocess = dfprocess.iloc[:, :3].dropna(subset=["process_data"])
        dfprocess.set_index("process_data", inplace=True)
        self.process_data = dfprocess.to_dict("index")

        # Set Pump operational data
        self.dfoperation = pd.read_excel(
            self.data_path, sheet_name="operational data", header=self.process_data["header_row"]["value"] - 1
        )

        # Set Pump unit
        dfunit = pd.read_excel(self.data_path, sheet_name="unit", header=0)
        dfunit = dfunit.iloc[:, :2].dropna(subset=["unit"])
        self.unit = dict(zip(dfunit["parameter"], dfunit["unit"]))

    def __check_mandatory_columns(self):
        """
        INIT METHOD - Checks if the operational data excel sheet contains the mandatory columns.

        Raises:
            ValueError: If the operational data excel sheet is missing the mandatory columns.
        """
        missing_columns = [col for col in list(Pump.mandatory_columns.keys()) if col not in self.dfoperation.columns]
        if len(missing_columns) > 0:
            missing_columns_error = (
                f"The operational data excel sheet is missing the following required columns: {', '.join(missing_columns)}."
            )
            raise CustomException(missing_columns_error)

    def clean_non_numeric_data(self):
        """
        Cleans the non-numeric data from the operational data excel sheet

            ** Method called from utlity function module.
        """
        self.dfoperation = uf.Clean_dataframe(self.dfoperation)
        self.logger.info("Data cleaning completed")

    def remove_irrelevant_columns(self):
        irrelevant_columns = [col for col in self.dfoperation.columns if col not in Pump.relevant_columns]
        self.dfoperation = self.dfoperation.drop(columns=irrelevant_columns)
        self.logger.info("Irrelevant columns removed")

    def convert_default_unit(self):
        flowrate_conversion = {"m3/hr": 1, "default": 1, "bpd": 0.0066245, "gpm": 0.22712, "bph": 0.15899, "mbph": 158.99}

        flowrate_unit = self.unit["flowrate"].lower()
        if flowrate_unit not in flowrate_conversion.keys():
            error_msg = (
                f"Flowrate unit {flowrate_unit} is not supported.Supported units are {', '.join(flowrate_conversion.keys())}"
            )
            self.logger.error(error_msg)
            raise CustomException(error_msg)

        self.dfoperation["discharge_flowrate"] = self.dfoperation["discharge_flowrate"] * flowrate_conversion.get(
            flowrate_unit, 1
        )

        self.process_data["rated_flow"]["value"] = self.process_data["rated_flow"]["value"] * flowrate_conversion.get(
            flowrate_unit, 1
        )

        pressure_unit = self.unit["pressure"]
        pressure_conversion = {"bar": 1, "psi": 0.0689476}

        self.dfoperation[["suction_pressure", "discharge_pressure"]] = self.dfoperation[
            ["suction_pressure", "discharge_pressure"]
        ] * pressure_conversion.get(pressure_unit, 1)

        if "downstream_pressure" in self.dfoperation.columns:
            self.dfoperation["downstream_pressure"] = self.dfoperation["downstream_pressure"] * pressure_conversion.get(
                pressure_unit, 1
            )

        self.logger.info("unit conversion completed")

    def remove_non_operating_rows(self):
        """
        Remove rows non operating rows from dfoperationbasaed on the following criteria:
        1. discharge_flowrate > 0
        2. suction_pressure < discharge_pressure
        3. downstream_pressure < discharge_pressure

        """
        try:
            self.dfoperation.dropna(subset=list(Pump.mandatory_columns.keys()), inplace=True)

            calculation_method = self.process_data["calculation_method"]["value"]

            mask = pd.Series(True, index=self.dfoperation.index)  # Initialize mask as True for all rows
            mask &= self.dfoperation["discharge_flowrate"] > 0
            mask &= self.dfoperation["suction_pressure"] < self.dfoperation["discharge_pressure"]

            if uf.is_empty_value(calculation_method):
                raise CustomException("calculation_method is not defined in config file.")

            if (calculation_method == "downstream_pressure") and ("downstream_pressure" in self.dfoperation.columns):
                downstream_pressure = pd.to_numeric(self.dfoperation["downstream_pressure"], errors="coerce").notna()
                mask &= (self.dfoperation["downstream_pressure"] < self.dfoperation["discharge_pressure"]) & (
                    downstream_pressure
                )

            elif calculation_method == "cv_opening" and "cv_opening" in self.dfoperation.columns:
                cv_opening = pd.to_numeric(self.dfoperation["cv_opening"], errors="coerce")
                mask &= (cv_opening.notna()) & (cv_opening > self.config["min_cv_opening"]["value"])

            elif "downstream_pressure|cv_opening" not in self.dfoperation.columns:
                error_msg = f"Can't find '{calculation_method}' column in the operational data sheet.\n \
            Try changing the calculation_method or Add some data that column in operational data sheet."

                raise CustomException(error_msg)

            self.dfoperation = self.dfoperation.loc[mask].reset_index(drop=True)

        except (CustomException, KeyError) as e:
            raise CustomException(e)

    def __get_flowrate_percent(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Calculates the flowrate percentage for each row in the dataframe
        - Group the values based on the bin_percent specified in config file
        - The resulting binned values are stored in a new column 'flowrate_percent'
        """
        percent = self.config["bin_percent"]["value"]
        self.dfoperation["flowrate_percent"] = (
            self.dfoperation["discharge_flowrate"] / self.process_data["rated_flow"]["value"]
        )

        bins = np.arange(0.275, 1 + (5 * percent), percent)
        labels = np.arange(0.30, 1 + (5 * percent), percent)
        self.dfoperation["flowrate_percent"] = pd.cut(
            self.dfoperation["flowrate_percent"], bins=bins, labels=labels, right=True
        )

    def __check_recirculation(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Check if recirculation flow is greater than the discharge flow
        """
        if "recirculation_flow" in self.dfoperation.columns:
            if (self.dfoperation["recirculation_flow"] > self.dfoperation["discharge_flowrate"]).all():
                self.logger.warning("Recirculation flow is greater than discharge flow")

    def get_computed_columns(self):
        """
        - Computed columns for the pump operation data
        - Group the dfoperarion dataframe based on the flowrate percentage and create a new datframe "dfcalculation"

        ** Core functions are stored in the PumpFunction class
        """

        self.__add_computed_columns()
        self.__get_cv_drop()
        self.__get_required_differential_pressure()
        self.__get_required_speed_varation()
        self.__get_base_hydraulic_power()
        self.__get_efficiency()
        self.__get_base_motor_power()
        self.__check_recirculation()
        self.__check_discharge_flow()
        self.__get_flowrate_percent()

        self.logger.info("Computed columns added")

    def __add_computed_columns(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()

        """

        self.dfoperation = self.dfoperation.reindex(
            columns=self.dfoperation.columns.tolist() + list(Pump.computed_columns.keys())
        )

        self.dfoperation["differential_pressure"] = PF.get_differential_pressure(
            self.dfoperation["discharge_pressure"], self.dfoperation["suction_pressure"]
        )

    def __get_cv_drop(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Calculates the cv_drop and inherant pipe loss based on the calculation_method
            1. downstream_pressure
            2. cv_opening
        """

        density = self.process_data["density"]["value"]
        valve_size = self.process_data["valve_size"]["value"]
        valve_character = self.process_data["valve_character"]["value"]
        calculation_method = self.process_data["calculation_method"]["value"]

        if calculation_method == "cv_opening":
            if not uf.is_empty_value(valve_size):
                self.dfoperation["actual_cv"] = PF.get_actual_cv(valve_size, self.dfoperation["cv_opening"], valve_character)

                self.dfoperation["calculated_cv_drop"] = PF.get_calculated_cv_drop(
                    self.dfoperation["discharge_flowrate"], self.dfoperation["actual_cv"], density
                )
                self.dfoperation["cv_pressure_drop"] = self.dfoperation["calculated_cv_drop"]
                self.dfoperation["inherent_piping_loss"] = 0
            else:
                error_msg = "valve_size is not defined in config file."
                self.logger.error(error_msg)
                raise CustomException(error_msg)

        elif calculation_method == "downstream_pressure":
            self.dfoperation["measured_cv_drop"] = PF.get_measured_cv_drop(
                self.dfoperation["discharge_pressure"], self.dfoperation["downstream_pressure"]
            )

            self.dfoperation["cv_pressure_drop"] = self.dfoperation["measured_cv_drop"]
            self.dfoperation["inherent_piping_loss"] = (
                self.dfoperation["cv_pressure_drop"] * self.config["pipe_loss"]["value"]
            )

    def __get_required_differential_pressure(self):
        self.dfoperation["required_differential_pressure"] = (
            self.dfoperation["differential_pressure"]
            + self.dfoperation["inherent_piping_loss"]
            - self.dfoperation["cv_pressure_drop"]
        )

    def __get_required_speed_varation(self):
        self.dfoperation["required_speed_variation"] = PF.get_speed_variation(
            self.dfoperation["differential_pressure"], self.dfoperation["required_differential_pressure"]
        )

    def __get_base_hydraulic_power(self):
        self.dfoperation["base_hydraulic_power"] = PF.get_base_hydraulic_power(
            self.dfoperation["discharge_flowrate"], self.dfoperation["differential_pressure"]
        )

    def __get_BEP_flowrate(self):
        """
        PRIVATE METHOD USED IN __get_efficiency()
        """

        if uf.is_empty_value(self.process_data["BEP_flowrate"]["value"]):
            BEP_flowrate = self.process_data["rated_flow"]["value"]
        elif isinstance(self.process_data["BEP_flowrate"]["value"], str):
            BEP_flowrate = self.process_data["rated_flow"]["value"]
            self.logger.warning(
                f"BEP_flowrate should be empty or numeric. Please don't string values next time. \nRated flowrate is used as BEP_flowrate."
            )
        else:
            BEP_flowrate = self.process_data["BEP_flowrate"]["value"]

        return BEP_flowrate

    def __get_BEP_efficiency(self):
        """
        PRIVATE METHOD USED IN __get_efficiency()
        """

        if self.process_data["BEP_efficiency"]["value"] == "" or (np.nan or None):
            BEP_efficiency = self.config["pump_efficiency"]["value"]
        elif isinstance(self.process_data["BEP_efficiency"]["value"], str):
            BEP_efficiency = self.config["pump_efficiency"]["value"]
            self.logger.warning(
                f"BEP_efficiency should be empty or numeric. Please don't string values next time. \nDefault pump efficiency is used as BEP_efficiency."
            )

        return BEP_efficiency

    def __get_efficiency(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        Calculates
            1. old_pump_efficiency
            2. old_motor_efficiency
        """
        BEP_flowrate = self.__get_BEP_flowrate()
        BEP_efficiency = self.__get_BEP_efficiency()

        self.dfoperation["old_pump_efficiency"] = PF.get_pump_efficiency(
            BEP_flowrate, BEP_efficiency, self.dfoperation["discharge_flowrate"]
        )

        # calculate old_motor_efficiency
        if uf.is_empty_value(self.process_data["motor_efficiency"]["value"]):
            self.process_data["motor_efficiency"]["value"] = 0.9
            self.logger.warning(f"motor_efficiency is empty. \n motor efficiency is considered 90% by default")

        self.dfoperation["old_motor_efficiency"] = self.process_data["motor_efficiency"]["value"]

    def __get_base_motor_power(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        """
        self.dfoperation["base_motor_power"] = (
            self.dfoperation["base_hydraulic_power"]
            / self.dfoperation["old_pump_efficiency"]
            / self.dfoperation["old_motor_efficiency"]
        )

    def __check_discharge_flow(self):
        """
        PRIVATE METHOD USED IN get_computed_columns() as quality check

        Raises:
            CustomException if the discharge flowrate is less than 30% of the rated flowrate
        """

        if self.dfoperation["discharge_flowrate"].max() < 0.3 * self.process_data["rated_flow"]["value"]:
            error_msg = "The maximum flowrate is less than 30% of the rated flowrate. \nPlease check the flowrate unit."
            self.logger.warning(error_msg)

            raise CustomException("Analysis stopped since VFD and Impeller trimming will not be effective.")

    def group_by_flowrate_percent(self):
        """
        - Group the dfoperation dataframe based on the flowrate percentage
        - Create a new datframe "dfcalculation"
        """
        df2 = self.dfoperation.groupby(by=["flowrate_percent"], as_index=False, dropna=False).mean(numeric_only=True)
        working_hours = self.dfoperation.groupby(by=["flowrate_percent"], as_index=False, dropna=False)[
            "discharge_flowrate"
        ].size()
        df2["working_hours"] = working_hours["size"]
        df2["working_percent"] = df2["working_hours"] / df2["working_hours"].sum()

        df2.loc[
            df2["working_percent"] < self.config["min_working_percent"]["value"], ["working_hours", "working_percent"]
        ] = 0
        df2["working_percent"] = df2["working_hours"] / df2["working_hours"].sum()
        df2["working_hours"] = df2["working_percent"] * 8760
        df2 = df2.loc[df2["working_percent"] > 0].reset_index(drop=True)
        df2["working_percent"] = df2["working_hours"] / df2["working_hours"].sum()
        df2["working_hours"] = df2["working_percent"] * 8760

        self.dfcalculation = df2

    def __select_speed_reduction(self):
        """
        Private method used in create_energy_calculation() method to select the speed reduction based on the options
        """

        self.dfcalculation.loc[
            self.dfcalculation["selected_measure"] == "Vsd", "selected_speed_variation"
        ] = self.dfcalculation["required_speed_variation"]

        self.dfcalculation.loc[
            (self.dfcalculation["selected_measure"] == "Impeller") & (self.dfcalculation["working_percent"] > 0),
            "selected_speed_variation",
        ] = (self.dfcalculation.loc[self.dfcalculation["working_percent"] > 0, "required_speed_variation"].dropna().max())

        self.dfcalculation.loc[(self.dfcalculation["working_percent"] <= 0), "selected_speed_variation"] = 0

    def __get_energy_columns(self):
        """
        Private method used in create_energy_calculation() method to create energy related columns in dfcalculation dataframe.
        """

        # calculate base case annual energy consumption
        self.dfcalculation["base_case_energy_consumption"] = (
            self.dfcalculation["base_motor_power"] * self.dfcalculation["working_hours"]
        )

        # calculate proposed case efficiency
        self.dfcalculation["new_pump_efficiency"] = self.dfcalculation["old_pump_efficiency"]
        self.dfcalculation["new_motor_efficiency"] = self.dfcalculation["old_motor_efficiency"]

        # calculate proposed case annual energy consumption
        eff_factor = (self.dfcalculation["new_pump_efficiency"] * self.dfcalculation["new_motor_efficiency"]) / (
            self.dfcalculation["old_pump_efficiency"] * self.dfcalculation["old_motor_efficiency"]
        )

        self.dfcalculation["proposed_case_energy_consumption"] = (
            self.dfcalculation["base_case_energy_consumption"]
            * (self.dfcalculation["selected_speed_variation"] ** 3)
            * eff_factor
        )

        # calculate annual energy savings
        self.dfcalculation["annual_energy_saving"] = (
            self.dfcalculation["base_case_energy_consumption"] - self.dfcalculation["proposed_case_energy_consumption"]
        )

    def __get_emissions_columns(self, site):
        """
        Private method used in create_energy_calculation() method to create emissions related columns in dfcalculation dataframe.
        """
        emission_factor = self.dfemission_factor[site]["emission_factor"]

        self.dfcalculation["base_case_emission"] = self.dfcalculation["base_case_energy_consumption"] * emission_factor

        self.dfcalculation["proposed_case_emission"] = (
            self.dfcalculation["proposed_case_energy_consumption"] * emission_factor
        )

        self.dfcalculation["ghg_reduction"] = (
            self.dfcalculation["base_case_emission"] - self.dfcalculation["proposed_case_emission"]
        )

        self.dfcalculation["ghg_reduction_percent"] = (
            self.dfcalculation["ghg_reduction"] / self.dfcalculation["base_case_emission"]
        )

    def create_energy_calculation(self, site):
        """
        - Create energy calculation dataframe for VSD and Impeller options.
        - Create summary dataframe for VSD and Impeller options.
        - Finally, renames the columns of all the dataframes from snake_case to Proper Case.
        """
        for option in ["Vsd", "Impeller"]:
            self.dfcalculation["selected_measure"] = option
            self.__select_speed_reduction()
            self.__get_energy_columns()
            self.__get_emissions_columns(site)

            if option == "Vsd":
                self.VSDCalculation = self.dfcalculation.copy()
                self.VSDSummary = self.__summarize(self.VSDCalculation, site)
                self.VSDSummary.columns = [option]
            elif option == "Impeller":
                self.ImpellerCalculation = self.dfcalculation.copy()
                self.ImpellerSummary = self.__summarize(self.ImpellerCalculation, site)
                self.ImpellerSummary.columns = [option]

        self.dfSummary = pd.concat([self.VSDSummary, self.ImpellerSummary], axis=1)

        if self.dfSummary["Vsd"]["base_case_energy_consumption"] == 0:
            error_msg = "Base case energy consumption is zero. Please check the input data."
            raise CustomException(error_msg)

        self.format_dataframes()
        self.__rename_columns()
        self.logger.info("Energy calculation completed")

    def __summarize(self, dfenergy, site):
        """
        PRIVATE METHOD USED IN create_energy_calculation()

        Creates summary dataframe for VSDCalculation and ImpellerCalculation dataframe
        """
        columns = [
            "pump_tag",
            "rated_flowrate",
            "selected_speed_variation",
            "base_case_energy_consumption",
            "proposed_case_energy_consumption",
            "annual_energy_saving",
            "base_case_emission",
            "proposed_case_emission",
            "ghg_reduction",
            "ghg_reduction_percent",
        ]
        dfSummary = pd.DataFrame(columns=columns, data=np.nan, index=[0])
        dfSummary["pump_tag"] = self.process_data["tag"]["value"]
        dfSummary["rated_flowrate"] = self.process_data["rated_flow"]["value"]

        dfSummary["selected_speed_variation"] = (
            "{:.0%}".format(dfenergy["selected_speed_variation"].max())
            + " - "
            + "{:.0%}".format(dfenergy["selected_speed_variation"].min())
        )
        dfSummary["base_case_energy_consumption"] = dfenergy["base_case_energy_consumption"].sum()
        dfSummary["proposed_case_energy_consumption"] = dfenergy["proposed_case_energy_consumption"].sum()
        dfSummary["annual_energy_saving"] = dfenergy["annual_energy_saving"].sum()
        dfSummary["base_case_emission"] = dfenergy["base_case_emission"].sum()
        dfSummary["proposed_case_emission"] = dfenergy["proposed_case_emission"].sum()
        dfSummary["emission_factor"] = self.dfemission_factor[site]["emission_factor"]
        dfSummary["ghg_reduction"] = dfenergy["ghg_reduction"].sum()
        dfSummary["ghg_reduction_percent"] = dfSummary["ghg_reduction"] / dfSummary["base_case_emission"]
        dfSummary = dfSummary.transpose()

        return dfSummary

    def __rename_columns(self):
        """
        PRIVATE METHOD USED IN create_energy_calculation()

        Renames the columns of all the dataframes from snake_case to Proper Case.
        """
        dfs = [j for j in vars(self).values() if isinstance(j, pd.DataFrame)]
        for df in dfs:
            df.rename(columns=lambda x: x.replace("_", " ").title(), inplace=True)
        self.dfSummary.index = self.dfSummary.index.str.replace("_", " ").str.title()

    def _add_multiheader(self):
        l1 = self.dfcalculation.columns.to_list()
        d1 = {
            **self.mandatory_columns,
            **self.optional_columns,
            **self.computed_columns,
            **self.energy_columns,
            **self.emission_columns,
        }
        multi_header = [(i, d1.get(i.replace(" ", "_").lower(), "")) for i in l1]

        self.VSDCalculation.columns = pd.MultiIndex.from_tuples(multi_header)
        self.ImpellerCalculation.columns = pd.MultiIndex.from_tuples(multi_header)

        self.dfSummary["Unit"] = [d1.get(i.replace(" ", "_").lower(), "") for i in self.dfSummary.index]

    def _remove_multiheader(self):
        self.VSDCalculation.columns = self.VSDCalculation.columns.droplevel(1)
        self.ImpellerCalculation.columns = self.ImpellerCalculation.columns.droplevel(1)

    def get_economic_calculation(self, capex, opex, annual_energy_savings, annual_emission_reduction):
        discount_rate = self.config["discount_rate"]["value"]
        project_life = self.config["project_life"]["value"]
        inflation_rate = self.config["inflation_rate"]["value"]
        electricity_price = self.config["electricity_price"]["value"]

        dfcashflow = ec.create_cashflow_df(capex=capex, project_life=project_life)

        dfcashflow["fuel_cost"] = annual_energy_savings * electricity_price
        dfcashflow["opex"] = ec.inflation_adjusted_opex(opex, inflation_rate, years=dfcashflow.index)
        dfcashflow.loc[1:, "cashflow"] = dfcashflow["fuel_cost"] - dfcashflow["opex"]

        NPV = npf.npv(rate=discount_rate, values=dfcashflow["cashflow"])
        IRR = npf.irr(dfcashflow["cashflow"])
        annualized_spending = ec.annualized_spending(NPV, discount_rate, project_life)
        pay_back = ec.calculate_payback_period(dfcashflow["cashflow"])
        ghg_reduction_cost = ec.GHG_reduction_cost(annualized_spending, annual_emission_reduction)

        economic_calculation = {
            "Capex": round(capex, 0),
            "NPV": round(NPV, 0),
            "IRR": "{:.0%}".format(IRR),
            "Payback Period": pay_back,
            "Annualized Spendings": round(annualized_spending, 0),
            "Annual GHG Reduction": round(annual_emission_reduction, 0),
            "GHG Reduction Cost": round(ghg_reduction_cost, 0),
        }
        return economic_calculation

    def __get_economics(self):
        self.VSDEconomics = self.get_economic_calculation(
            capex=self.config["vsd_capex"]["value"] / self.process_data["spare"]["value"],
            opex=self.config["vsd_opex"]["value"] * self.config["vsd_capex"]["value"],
            annual_energy_savings=self.dfSummary["Vsd"]["Annual Energy Saving"],
            annual_emission_reduction=self.dfSummary["Vsd"]["Ghg Reduction"],
        )

        self.VFDEconomics = self.get_economic_calculation(
            capex=self.config["vfd_capex"]["value"] / self.process_data["spare"]["value"],
            opex=self.config["vfd_opex"]["value"] * self.config["vfd_capex"]["value"],
            annual_energy_savings=self.dfSummary["Vsd"]["Annual Energy Saving"],
            annual_emission_reduction=self.dfSummary["Vsd"]["Ghg Reduction"],
        )

        self.ImpellerEconomics = self.get_economic_calculation(
            capex=self.config["impeller_capex"]["value"] / self.process_data["spare"]["value"],
            opex=self.config["impeller_opex"]["value"] * self.config["impeller_capex"]["value"],
            annual_energy_savings=self.dfSummary["Impeller"]["Annual Energy Saving"],
            annual_emission_reduction=self.dfSummary["Impeller"]["Ghg Reduction"],
        )

    def get_economics_summary(self):
        try:
            self.__get_economics()

            dfs = []
            for option, col in zip(
                [self.VSDEconomics, self.VFDEconomics, self.ImpellerEconomics], ["VSD", "VFD", "Impeller"]
            ):
                df = pd.DataFrame(option.values(), index=option.keys(), columns=[col])
                dfs.append(df)

            self.dfEconomics = pd.concat(dfs, axis=1)

        except Exception as e:
            self.logger.error("Error while creating economics summary.")
            print(traceback.format_exc())

    def _get_output_path(self, output_folder, site, tag):
        """
        PRIVATE METHOD used in  write_to_excel()

        Creates output path for excel file.
        """
        output_folder = Path(output_folder).resolve()
        output_folder_path = os.path.join(output_folder, site)
        os.makedirs(output_folder_path, exist_ok=True)
        output_path = os.path.join(output_folder_path, tag + ".xlsx")
        return output_path

    def format_dataframes(self):
        """
        Formats the dataframes for excel file.
        """
        percent_columns = [
            "flowrate_percent",
            "old_pump_efficiency",
            "old_motor_efficiency",
            "new_motor_efficiency",
            "new_pump_efficiency",
            "ghg_reduction_percent",
            "required_speed_variation",
            "selected_speed_variation",
            "working_percent"
        ]
        for df in [self.VSDCalculation, self.ImpellerCalculation]:
            for col in percent_columns:
                df[col] = df[col].apply(lambda x: uf.format_number(x, type="percent"))

            for col in df.columns:
                if df[col].dtype == "float64":
                    df[col] = df[col].apply(lambda x: uf.format_number(x, type="whole"))

    def format_summary(self):
        excluded_columns = ["Ghg Reduction Percent", "Emission Factor"]
        self.dfSummary = self.dfSummary.apply(
            lambda row: row.apply(lambda val: uf.format_number(val, type="percent"))
            if row.name == "Ghg Reduction Percent"
            else row
            if row.name == "Emission Factor"
            else row.apply(uf.format_number),
            axis=1,
        )

    def write_to_excel(self, output_folder, site, tag):
        """
        Creates excel file based on the output folder, site and tag.
        Writes three dataframes to excel file.
        1. dfsummary
        2. VSDCalculation
        3. ImpellerCalculation

        """
        try:
            path = self._get_output_path(output_folder, site, tag)

            self.format_summary()
            self._add_multiheader()

            with xw.App(visible=False) as app:
                if not os.path.isfile(path):
                    wb = xw.Book()
                else:
                    wb = xw.Book(path)
                ws = wb.sheets[0]
                ws.clear_contents()

                for cell, df, bool in zip(
                    ["A1", "A14", "A32", "G1"],
                    [self.dfSummary, self.VSDCalculation, self.ImpellerCalculation, self.dfEconomics],
                    [True, False, False, True],
                ):
                    ws.range(cell).options(index=bool).value = df
                    current_area = ws.range(cell).expand().address
                    #make boder
                    ws.range(current_area).api.Borders.LineStyle = 1

                ws.api.PageSetup.Orientation = xw.constants.PageOrientation.xlLandscape
                ws.api.PageSetup.PaperSize = xw.constants.PaperSize.xlPaperA3
                ws.api.PageSetup.PrintArea = "$A$1:$AG$50"
                ws.api.PageSetup.Zoom = 55
                ws.range("14:14").api.Font.Bold = True
                ws.range("14:14").api.Orientation = 90
                ws.range("32:32").api.Font.Bold = True
                ws.range("32:32").api.Orientation = 90
                ws.range("A:A").api.EntireColumn.AutoFit()

                pdf_path = path.replace(".xlsx", ".pdf")
                wb.api.ExportAsFixedFormat(0, pdf_path)
                wb.save(path)

                self._remove_multiheader()

                self.logger.info(f"Excel file created at {path}")
        except Exception as e:
            raise CustomException(e, "Error in writing to excel.")
