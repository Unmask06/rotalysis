import streamlit as st

# Page configuration for wider page
st.set_page_config(layout="wide")
logo_path = "static/BTME logo.png"
st.sidebar.image(logo_path, width=200)

# Title and Introduction
st.title("Welcome to Rotalysis")

st.markdown(
    """
This app provides a comprehensive tool for calculating energy and emission savings along 
with the economics of converting fixed-speed driven pumps and compressors into variable speed drives.
Tailored for the oil and gas industry, this tool utilizes operational and process data to offer insights 
into potential savings and efficiency improvements.
"""
)

# Objective
st.header("Objective")

st.write(
    """
The primary objective of this application is to calculate energy and emission savings along with the economics calculation for the conversion of fixed speed driven pumps and compressors into Variable Speed Drive (VSD) based on the operational data and process data received from the company. This aids in making informed decisions about energy efficiency improvements and emissions reduction strategies.
"""
)

# Required Input Data
st.header("Required Input Data")

st.markdown(
    """
To utilize this tool effectively, you'll need to provide:
- **Input data** in the form of Excel files with the following sheets:
    - **Design data** of the pumps and compressors [Mandatory].
    - **Operational data** from the Distributed Control System (DCS) [Mandatory].
    - **Pump Curve data** for the pumps [Optional].
    - **Unit** followed in the Operational data [Mandatory].
- A **configuration file** in terms of Excel file.
- A **task list** for the pumps and compressors with the Tag and other required information.
"""
)

# Expected Output
st.header("Expected Output")

st.markdown(
    """
Upon providing the necessary data and performing the calculations, the tool will generate the output excel file with the following details:
- Energy and Emission saving calculation for VSD installation / Impeller trimming for various bins of flow rate percentage.
- A summary of the Energy and emission savings and Economics calculation for VSD installation and Impeller trimming.
"""
)

# Navigating the App
st.header("Getting Started")

st.markdown(
    """
To get started:
1. Navigate to the 'Calculation' page from the sidebar and provide the path.
2. Process the task to calculate energy and emission savings.
3. Results will be saved in the output folder provided.

We hope this tool empowers you to make data-driven decisions towards energy efficiency and emissions reduction in your operations.
"""
)

# Placeholder for further development or instructions
# This could include links to other pages of the app or external documentation
