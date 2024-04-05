class ValveCharacter:
    LINEAR = "Linear"
    EQUAL_PERCENTAGE = "Equal Percentage"
    QUICK_OPENING = "Quick Opening"


class PumpDesignDataVariables:
    EQUIPMENT_TAG = "Equipment Tag"
    EQUIPMENT_TYPE = "Equipment Type"
    DESCRIPTION = "Description"
    RATED_FLOWRATE = "Rated Flowrate"
    RATED_HEAD = "Rated Head"
    DENSITY = "Density"
    BEP_FLOWRATE = "BEP Flowrate"
    BEP_EFFICIENCY = "BEP Efficiency"
    MOTOR_EFFICIENCY = "Motor Efficiency"
    DISCHARGE_VALVE_SIZE = "Discharge Valve Size"
    DISCHARGE_VALVE_CHARACTER = "Discharge Valve Character"
    PUMP_SPEED = "Pump Speed"
    CALCULATION_METHOD = "Calculation Method"
    SPARING_FACTOR = "Sparing Factor"
    HEADER_ROW = "Header Row"


class PumpOperationVariables:
    SUCTION_PRESSURE = "Suction Pressure"
    DISCHARGE_PRESSURE = "Discharge Pressure"
    DISCHARGE_FLOWRATE = "Discharge Flowrate"
    CV_OPENING = "CV Opening"
    DOWNSTREAM_PRESSURE = "Downstream Pressure"
    RECIRCULATION_FLOW = "Recirculation Flow"


class EmissionVariables:
    BASE_CASE_EMISSION = "Base Case Emission"
    PROPOSED_CASE_EMISSION = "Proposed Case Emission"
    GHG_REDUCTION = "GHG Reduction"
    GHG_REDUCTION_PERCENT = "GHG Reduction Percent"
    EMISSION_FACTOR = "Emission Factor"
    ANNUAL_GHG_REDUCTION = "Annual GHG Reduction"


class ComputedVariables:
    FLOWRATE_PERCENT = "Flowrate Percent"
    DIFFERENTIAL_PRESSURE = "Differential Pressure"
    ACTUAL_CV = "Actual CV"
    CALCULATED_CV_DROP = "Calculated CV Drop"
    MEASURED_CV_DROP = "Measured CV Drop"
    CV_PRESSURE_DROP = "CV Pressure Drop"
    INHERENT_PIPING_LOSS = "Inherent Piping Loss"
    REQUIRED_DIFFERENTIAL_PRESSURE = "Required Differential Pressure"
    REQUIRED_SPEED_VARIATION = "Required Speed Variation"
    BASE_HYDRAULIC_POWER = "Base Hydraulic Power"
    OLD_PUMP_EFFICIENCY = "Old Pump Efficiency"
    OLD_MOTOR_EFFICIENCY = "Old Motor Efficiency"
    BASE_MOTOR_POWER = "Base Motor Power"
    WORKING_HOURS = "Working Hours"
    WORKING_PERCENT = "Working Percent"
    NEW_PUMP_EFFICIENCY = "New Pump Efficiency"
    NEW_MOTOR_EFFICIENCY = "New Motor Efficiency"
    SELECTED_MEASURE = "Selected Measure"
    SELECTED_SPEED_VARIATION = "Selected Speed Variation"
    BASE_CASE_ENERGY_CONSUMPTION = "Base Case Energy Consumption"
    PROPOSED_CASE_ENERGY_CONSUMPTION = "Proposed Case Energy Consumption"
    ANNUAL_ENERGY_SAVING = "Annual Energy Saving"
    CV_OPENING = "CV Opening"
    DOWNSTREAM_PRESSURE = "Downstream Pressure"
    MOTOR_POWER = "Motor Power"
    RECIRCULATION_FLOW = "Recirculation Flow"


class OptionalVariables:
    POWER_FACTOR = "Power Factor"
    RUN_STATUS = "Run Status"
    SPEED = "Speed"
    MOTOR_AMP = "Motor Amp"


class InputSheetNames:
    DESIGN_DATA = "Design Data"
    OPERATIONAL_DATA = "Operational Data"
    PUMP_CURVE = "Pump Curve"
    UNIT = "Unit"


class ConfigurationVariables:
    PIPING_LOSS = "Piping Loss"
    MIN_CV_LOSS = "Min CV Loss"
    MIN_CV_OPENING = "Min CV Opening"
    DISCHARGE_FLOWRATE = "Discharge Flowrate"
    MIN_WORKING_PERCENT = "Min Working Percent"
    MIN_SPEED = "Min Speed"
    BIN_PERCENT = "Bin Percent"
    EMISSION_FACTOR = "Emission Factor"
    PUMP_EFFICIENCY = "Pump Efficiency"
    DISCOUNT_RATE = "Discount Rate"
    PROJECT_LIFE = "Project Life"
    INFLATION_RATE = "Inflation Rate"
    VSD_CAPEX = "VSD Capex"
    VFD_CAPEX = "VFD Capex"
    VSD_OPEX = "VSD Opex"
    VFD_OPEX = "VFD Opex"
    ELECTRICITY_PRICE = "Electricity Price"
    PUMP_COST = "Pump Cost"
    IMPELLER_CAPEX = "Impeller Capex"
    IMPELLER_OPEX = "Impeller Opex"
    MOTOR_COST = "Motor Cost"
    HIGH_EFFICIENCY_ESCALATION_FACTOR = "High Eff Escalation Factor"
    PREMIUM_EFFICIENCY_ESCALATION_FACTOR = "Premium Eff Escalation Factor"
    STD_EFFICIENCY_MOTOR = "Std Eff Motor"
    HIGH_EFFICIENCY_MOTOR = "High Eff Motor"
    PREMIUM_EFFICIENCY_MOTOR = "Premium Eff Motor"


class EconomicsVariables:
    ANNUAL_ENERGY_SAVING = "Annual Energy Saving"
    NPV = "NPV"
    IRR = "IRR"
    PAYBACK_PERIOD = "Payback Period"
    DISCOUNT_RATE = "Discount Rate"
    CASH_FLOW = "Cash Flow"
    CAPEX = "Capex"
    OPEX = "Opex"
    ANNUALIZED_SPENDING = "Annualized Spending"
    GHG_REDUCTION_COST = "GHG Reduction Cost"
    FUEL_COST = "Fuel Cost"
