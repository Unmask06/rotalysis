import streamlit as st

# Set page config to widen the layout
st.set_page_config(page_title="Rotalysis", layout="wide")
logo_path = "static/BTME logo.png"
st.sidebar.image(logo_path, width=200)

# Displaying the logo in the sidebar if you have one
# logo_path = 'path/to/your/logo.png'
# st.sidebar.image(logo_path, use_column_width=True)

st.title("Rotalysis")
st.markdown("**Rotating Equipment Analysis**")

# Introduction
st.title("Introduction")
st.markdown(
    """
Rotalysis, which stands for "Rotating Equipment Analysis", is an engineering calculation tool developed using Python, 
for assisting energy optimization studies for rotating equipment. The software can be potentially used in conceptual and basic 
engineering level study projects. Rotalysis evaluates common energy-saving measures such as rotor modifications and variable 
speed application based on historical process operations and anticipated operating profiles. It streamlines desktop analysis 
using data science techniques, affinity laws, and economic viability calculations, making the process more manageable while 
saving precious engineering manhours.
"""
)

# Core Functionality
st.header("Core Functionality")
st.markdown(
    """
Rotalysis converts input data related to equipment design (e.g., performance curves) and system side details (obtained as 
flows and pressure and throttling losses) to determine the use profile and recommend changes for diameter and speed. 
The key insights for making the recommendations are obtained by observing the throttling and recycling losses in the system. 
The recommendations are made to minimize these while handling the potential variability in flow demand. The potential recommendations 
are evaluated for energy savings, emission reductions, and economic viability calculations with Capex provided as an input. 
A block diagram showing the typical inputs and typical output is illustrated below.
"""
)

# Placeholder for the Block Diagram Image
# Make sure to replace 'path/to/your/block_diagram.png' with the actual path to your block diagram image file
# block_diagram_path = 'path/to/your/block_diagram.png'
# st.image(block_diagram_path, caption='Figure 1: Input and Output Block Diagram')

# Levels of Analysis
st.header("Levels of Analysis")
st.markdown(
    """
Depending on the nature of the project, required accuracy levels, and data availability, the analysis can be performed at 
different levels of rigor. These levels and their corresponding input data requirements are defined as follows:
"""
)
st.markdown(
    """
- **Level 1:** Inputs required are snapshot operating data from the field and the current best efficiency point. 
Output recommends diameter reduction/speed variation using thumb rules/correlations.
- **Level 2:** Inputs required are time series operational data from DCS and the current best efficiency point. 
Output recommends diameter reduction/speed variation using thumb rules/correlations. The recommendation, however, 
can now be made with a greater degree of confidence since the proposed measures would positively cover reasonable 
flow variations determined after data cleaning.
- **Level 3:** Inputs required are time series operational data from DCS and performance curves. Energy saving calculations 
are now more accurate as the base case and proposed case efficiencies are determined from the equipment performance curves 
instead of high-level correlations. The recommendations for diameter and speed changes are also made based on any constraints 
emerging from the curves (min allowable diameter, min allowable speed).
- **Level 4:** Inputs required are similar to Level 3, with Future profiles additionally included. Outputs are similar to Level 3 
but verified to handle future operations.
"""
)

# Project References
st.header("Project References")
st.markdown(
    """
Rotalysis was developed to meet the project requirements of a decarbonization/energy optimization study for a reputed Oil and Gas Company in UAE. 
It was effectively used to study over 50 pumps to assess the energy savings and economic viability of rotor changes and adoption of variable 
speed drive on existing fixed speed equipment. Once all the necessary inputs are ready, Rotalysis can produce the results almost instantaneously.
"""
)

# System Requirements and Deployment
st.header("System Requirements and Deployment")
st.markdown(
    """
- Can be used as a Windows desktop application with GUI or basic command line interface (CLI).
- Ready for web deployment using Streamlit.
- Single Page Application (SPA) development in progress.
"""
)

# You can add more sections or functionalities as per your application needs
