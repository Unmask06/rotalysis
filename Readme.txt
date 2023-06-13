Put the operational data and process data as received from company into the standard template. 
General dataframe cleaning to remove all columns or rows for which all entries are non numeric i.e. empty/corrupt columns and rows.
Find the equipment type for dfprocess_data
If Pump then , process the data using PumpFunction Class
Clean for Pump dataframe for columns:
    Retain column if within list of relevant columns required for calculation (mandatory + optional columns)
    Raise error if any column within list of mandatory column is missing
Set the proces_data and config dictionary to the PumpFunction usign set methods.
Remove abnormal rows based on calculation method specified in pump file (cv_opening or downstream_pressure)
calculate computed_columns using the PumpFunction class
Based on the flowrate percentage, other columns are grouped and mean is calculated
Bin less than 27.5% of flowrate is removed from the dataframe
Selected Speed variation
    If selected option is "Impeller" then selected speed variation is the max of required speed variation.
    if selected option is "VSD" then selected speed variation same as the required speed variation.
Pump efficiency is calculated based on the equation 1- (1-%Q)^2




