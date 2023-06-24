
## OBJECTIVE
Calculating energy and emission saving calculation along with the economics calculation for the conversion of fixed speed driven pumps and compressors into Variable speed drive based on the operational data and process data received from the company.

## INPUT
- Operational data from the DCS
- Process data of the pumps and compressors
- Configuration file for the pumps and compressors
- Task list for the pumps and compressors with the Tag and other required information

## OUTPUT
- Energy and Emision saving calculation for VSD intallation / Impeller trimming for various bins of flowrate percentage
- Summary of the Energy and emission savings and  Economics calculation for VSD intallation and Impeller trimming.

## CALCULATION METHODOLOGY
### Pump Calculation

1. Put the operational data and process data as received from company into the standard template. 
2. General dataframe cleaning to remove all columns or rows for which all entries are non numeric i.e. empty/corrupt columns and rows.
3. Find the equipment type for dfprocess_data

4. Clean for Pump dataframe for columns:
    
5. Retain column if within list of relevant columns required for calculation (mandatory + optional columns)

6. Raise error if any column within list of mandatory column is missing
7. Set the proces_data and config dictionary to the PumpFunction usign set methods.
8. Remove abnormal rows based on calculation method specified in pump file (cv_opening or downstream_pressure).
9. Calculate computed_columns using the PumpFunction class
10. Based on the flowrate percentage, other columns are grouped and mean is calculated.
11. Bin less than 27.5% of flowrate is removed from the dataframe
12. **Selected Speed variation** 
- If selected option is "Impeller" then selected speed variation is the max of required speed variation.
- if selected option is "VSD" then selected speed variation same as the required speed variation.
13. Pump efficiency is calculated based on the equation 1- (1-%Q)^2