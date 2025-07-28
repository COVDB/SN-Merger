import pandas as pd
import streamlit as st

# List of material numbers to filter on
MATERIAL_NUMBERS = [
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
    "Material Number": "Material Number",
}

st.title("Excel Merger")

st.write(
    "Upload the three Excel sheets: 'AM LOG', 'ZSD_PO_PER_SO' and 'ZSTATUS'."
)

st.sidebar.header("Uploads")
am_log_file = st.sidebar.file_uploader("Upload AM LOG", type=["xls", "xlsx"])
zsd_file = st.sidebar.file_uploader("Upload ZSD_PO_PER_SO", type=["xls", "xlsx"])
status_file = st.sidebar.file_uploader("Upload ZSTATUS", type=["xls", "xlsx"])

st.sidebar.header("Filtering")
# Allow users to add additional material numbers via text area
extra_numbers_text = st.sidebar.text_area(
    "Additional material numbers (one per line)",
    value="",
)
extra_numbers = [n.strip() for n in extra_numbers_text.splitlines() if n.strip()]

# Combine default and additional numbers then let the user select which to use
all_numbers = MATERIAL_NUMBERS + extra_numbers
selected_numbers = st.sidebar.multiselect(
    "Material numbers for filtering",
    options=all_numbers,
    default=MATERIAL_NUMBERS,
)

if am_log_file is not None:
    # Read all data as strings so material numbers keep their leading zeros
    am_log_df = pd.read_excel(am_log_file, dtype=str)
    # Strip whitespace from column names to avoid mismatches
    am_log_df.columns = am_log_df.columns.str.strip()

    # Extract year and month from Delivery Date into construction columns
    if AM_LOG_COLUMNS["Delivery Date"] in am_log_df.columns:
        delivery_dates = pd.to_datetime(
            am_log_df[AM_LOG_COLUMNS["Delivery Date"].strip()], errors="coerce"
        )
        am_log_df[AM_LOG_COLUMNS["Year of construction"]] = (
            delivery_dates.dt.year.astype("Int64").astype(str)
        )
        am_log_df[AM_LOG_COLUMNS["Month of construction"]] = (
            delivery_dates.dt.month.astype("Int64").astype(str).str.zfill(2)
        )

    missing_cols = [
        col for col in AM_LOG_COLUMNS.values() if col not in am_log_df.columns
    ]
    if missing_cols:
        st.error(f"Missing columns in AM LOG: {', '.join(missing_cols)}")
    else:
        material_col = (
            am_log_df[AM_LOG_COLUMNS["Material Number"]].astype(str).str.strip()
        )
        filtered = am_log_df[material_col.isin(selected_numbers)]

        removed_count = len(am_log_df) - len(filtered)


        # Default to the filtered rows. Join with ZSD_PO_PER_SO if provided.
        merged = filtered.copy()

        if zsd_file is not None:
            zsd_df = pd.read_excel(zsd_file, dtype=str)
            zsd_df.columns = zsd_df.columns.str.strip()
            if {"Document", "Material"}.issubset(zsd_df.columns):
                zsd_df = zsd_df[["Document", "Material"]]
                zsd_df["Document"] = zsd_df["Document"].astype(str).str.strip()
                merged = filtered.merge(
                    zsd_df,
                    left_on=AM_LOG_COLUMNS["Customer Reference"],
                    right_on="Document",
                    how="left",
                )
            else:
                st.warning("ZSD_PO_PER_SO missing 'Document' or 'Material' columns")


                merged = filtered.copy()


        output_columns = [
            AM_LOG_COLUMNS["Delivery Date"],
            AM_LOG_COLUMNS["Customer Reference"],
            AM_LOG_COLUMNS["Serial number"],
            AM_LOG_COLUMNS["Year of construction"],
            AM_LOG_COLUMNS["Month of construction"],
        ]

        if zsd_file is not None and {"Document", "Material"}.issubset(merged.columns):



            output_columns.extend(["Document", "Material"])

        st.write(
            f"Filtered AM LOG - removed {removed_count} of {len(am_log_df)} rows"
        )
        st.dataframe(merged[output_columns])





        st.write(
            f"Filtered AM LOG - removed {removed_count} of {len(am_log_df)} rows"
        )
        st.dataframe(filtered[output_columns])



else:
    st.info("Waiting for AM LOG file upload")
