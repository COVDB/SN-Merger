import pandas as pd
import streamlit as st

# List of equipment numbers to filter on
EQUIPMENT_NUMBERS = [
    "000000000001001917",
    "000000000001001808",
    "000000000001001749",
    "000000000001001776",
    "000000000001001911",
    "000000000001001755",
    "000000000001001760",
    "000000000001001809",
    "000000000001001747",
    "000000000001001711",
    "000000000001001757",
    "000000000001001708",
    "000000000001001770",
    "000000000001001710",
    "000000000001001771",
    "000000000001001758",
    "000000000001007905",
    "000000000001001753",
    "000000000001001752",
    "000000000001008374",
    "000000000001001805",
    "000000000001001709",
    "000000000001008561",
    "000000000001008560",
    "000000000001001765",
    "000000000001001775",
    "000000000001009105",
    "000000000001001777",
    "000000000001001742",
    "000000000001001813",
    "000000000001009719",
]

# Expected column names in the "AM LOG" sheet
AM_LOG_COLUMNS = {
    "Delivery Date": "Delivery Date",
    "Customer Reference": "Customer Reference",
    "Serial number": "Serial number",
    "Year of construction": "Year of construction",
    "Month of construction": "Month of construction",
    "Equipment number": "Equipment number",
}

st.title("Excel Merger")

st.write(
    "Upload the three Excel sheets: 'AM LOG', 'ZSD_PO_PER_SO' and 'ZSTATUS'."
)

am_log_file = st.file_uploader("Upload AM LOG", type=["xls", "xlsx"])
zsd_file = st.file_uploader("Upload ZSD_PO_PER_SO", type=["xls", "xlsx"])
status_file = st.file_uploader("Upload ZSTATUS", type=["xls", "xlsx"])

if am_log_file is not None:

    # Read all data as strings so equipment numbers keep their leading zeros
    am_log_df = pd.read_excel(am_log_file, dtype=str)
    # Strip whitespace from column names to avoid mismatches
    am_log_df.columns = am_log_df.columns.str.strip()

    am_log_df = pd.read_excel(am_log_file)


    missing_cols = [
        col for col in AM_LOG_COLUMNS.values() if col not in am_log_df.columns
    ]
    if missing_cols:
        st.error(f"Missing columns in AM LOG: {', '.join(missing_cols)}")
    else:

        equipment_col = am_log_df[AM_LOG_COLUMNS["Equipment number"]].str.strip()
        filtered = am_log_df[equipment_col.isin(EQUIPMENT_NUMBERS)]


        filtered = am_log_df[
            am_log_df[AM_LOG_COLUMNS["Equipment number"]]
            .astype(str)
            .isin(EQUIPMENT_NUMBERS)
        ]

        output_columns = [
            AM_LOG_COLUMNS["Delivery Date"],
            AM_LOG_COLUMNS["Customer Reference"],
            AM_LOG_COLUMNS["Serial number"],
            AM_LOG_COLUMNS["Year of construction"],
            AM_LOG_COLUMNS["Month of construction"],
        ]
        st.write("Filtered AM LOG")
        st.dataframe(filtered[output_columns])
else:
    st.info("Waiting for AM LOG file upload")
