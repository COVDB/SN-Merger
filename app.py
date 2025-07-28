import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Serial Number Merger", layout="centered")
st.title("Serial Number Merger")

st.write("""
Upload eerst de drie Excel-bestanden en selecteer daarna de juiste kolommen voor de merges.
""")

#
# Sidebar: uploads + filterlijst
#
st.sidebar.header("1. Upload bestanden")
amlog_file   = st.sidebar.file_uploader("AM LOG EQUIPMENT LIST",    type=["xls","xlsx"])
zsd_file     = st.sidebar.file_uploader("ZSD_PO_PER_SO (EXPORT)",    type=["xls","xlsx"])
status_file  = st.sidebar.file_uploader("ZSTATUS export",            type=["xls","xlsx"])

st.sidebar.header("2. Material filter")
# default lijst
DEFAULT_MATS = [
    "000000000001001917","000000000001001808","000000000001001749",
    "000000000001001776","000000000001001911","000000000001001755",
    "000000000001001760","000000000001001809","000000000001001747",
    "000000000001001711","000000000001001757","000000000001001708",
    "000000000001001770","000000000001001710","000000000001001771",
    "000000000001001758","000000000001007905","000000000001001753",
    "000000000001001752","000000000001008374","000000000001001805",
    "000000000001001709","000000000001008561","000000000001008560",
    "000000000001001765","000000000001001775","000000000001009105",
    "000000000001001777","000000000001001742","000000000001001813",
    "000000000001009719"
]
extra_mats = st.sidebar.text_area(
    "Extra material numbers (één per regel)",
    value=""
)
extra_list = [m.strip() for m in extra_mats.splitlines() if m.strip()]
all_mats   = list(dict.fromkeys(DEFAULT_MATS + extra_list))
selected_mats = st.sidebar.multiselect(
    "Selecteer material numbers",
    options=all_mats,
    default=DEFAULT_MATS
)

#
# Pas pas toe zodra alle drie bestanden geüpload zijn
#
if amlog_file and zsd_file and status_file:
    # 1) Lees AM LOG
    df_amlog = pd.read_excel(amlog_file, dtype=str)
    df_amlog.columns = df_amlog.columns.str.strip()
    # Afleiden construction year/month uit Delivery Date
    if "Delivery Date" in df_amlog.columns:
        dates = pd.to_datetime(df_amlog["Delivery Date"], errors="coerce")
        df_amlog["Year of construction"]  = dates.dt.year.fillna(0).astype(int).astype(str)
        df_amlog["Month of construction"] = dates.dt.month.fillna(0).astype(int).astype(str).str.zfill(2)
    st.success("AM LOG ingelezen en bouwjaar/-maand afgeleid")

    # 2) Lees EXPORT (ZSD_PO_PER_SO)
    df_zsd = pd.read_excel(zsd_file, dtype=str)
    df_zsd.columns = df_zsd.columns.str.strip()
    st.success("ZSD_PO_PER_SO ingelezen")

    # 3) Lees ZSTATUS
    df_stat = pd.read_excel(status_file, dtype=str)
    df_stat.columns = df_stat.columns.str.strip()
    st.success("ZSTATUS ingelezen")

    #
    # Stap 4: kolomselecties
    #
    st.header("Key-kolommen selecteren")
    amlog_ref       = st.selectbox("AM LOG: Customer Reference",    df_amlog.columns, index=df_amlog.columns.get_loc("Customer Reference") if "Customer Reference" in df_amlog.columns else 0)
    amlog_matcol    = st.selectbox("AM LOG: Material Number",       df_amlog.columns, index=df_amlog.columns.get_loc("Material Number")    if "Material Number"    in df_amlog.columns else 0)
    amlog_eq        = st.selectbox("AM LOG: Equipment Number",      df_amlog.columns, index=df_amlog.columns.get_loc("Equipment Number")   if "Equipment Number"   in df_amlog.columns else 0)
    amlog_sn        = st.selectbox("AM LOG: Serial number",         df_amlog.columns, index=df_amlog.columns.get_loc("Serial number")      if "Serial number"      in df_amlog.columns else 0)

    zsd_doc         = st.selectbox("EXPORT: Document (Purch.Doc)",   df_zsd.columns,   index=df_zsd.columns.get_loc("Document")             if "Document"            in df_zsd.columns else 0)
    zsd_mat         = st.selectbox("EXPORT: Material",               df_zsd.columns,   index=df_zsd.columns.get_loc("Material")             if "Material"            in df_zsd.columns else 0)
    zsd_proj        = st.selectbox("EXPORT: Project Reference",     df_zsd.columns,   index=df_zsd.columns.get_loc("Project Reference")    if "Project Reference"   in df_zsd.columns else 0)

    stat_projref    = st.selectbox("ZSTATUS: ProjRef",               df_stat.columns,  index=df_stat.columns.get_loc("ProjRef")             if "ProjRef"             in df_stat.columns else 0)
    stat_soldto     = st.selectbox("ZSTATUS: Sold-to pt",            df_stat.columns,  index=df_stat.columns.get_loc("Sold-to pt")          if "Sold-to pt"          in df_stat.columns else 0)
    stat_shipto     = st.selectbox("ZSTATUS: Ship-to",               df_stat.columns,  index=df_stat.columns.get_loc("Ship-to")             if "Ship-to"             in df_stat.columns else 0)
    stat_created    = st.selectbox("ZSTATUS: Created on",            df_stat.columns,  index=df_stat.columns.get_loc("Created on")          if "Created on"          in df_stat.columns else 0)

    #
    # Verwerk en merge
    #
    if st.button("Verwerken"):
        # a) clean join-sleutels
        for df, col in [
            (df_amlog, amlog_ref),
            (df_zsd,   zsd_doc),
            (df_stat,  stat_projref)
        ]:
            df[col] = df[col].astype(str).str.replace(r'\.0$','',regex=True).str.strip()

        # b) filter AMLOG
        df_amlog_f = df_amlog[df_amlog[amlog_matcol].isin(selected_mats)].copy()
        st.write(f"Na filter AM LOG: {len(df_amlog)} → {len(df_amlog_f)} rijen")

        # c) merge1 AMLOG ↔ ZSD
        df1 = df_amlog_f.merge(
            df_zsd[[zsd_doc, zsd_mat, zsd_proj]],
            left_on=amlog_ref, right_on=zsd_doc,
            how="left",
            suffixes=("","_exp")
        )
        st.write(f"Na merge met EXPORT: {len(df1)} rijen")

        # d) merge2 ↔ ZSTATUS
        df2 = df1.merge(
            df_stat[[stat_projref, stat_soldto, stat_shipto, stat_created]],
            left_on=zsd_proj, right_on=stat_projref,
            how="left",
            suffixes=("","_zst")
        )
        st.write(f"Na merge met ZSTATUS: {len(df2)} rijen")

        # e) selecteer output-kolommen
        out_cols = [
            "Delivery Date", amlog_ref, amlog_eq, amlog_sn,
            "Year of construction", "Month of construction",
            zsd_mat, zsd_doc, zsd_proj,
            stat_soldto, stat_shipto, stat_created
        ]
        df_out = df2[out_cols].copy()

        # f) Toon & download
        st.dataframe(df_out.head(100))
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_out.to_excel(writer, index=False, sheet_name="SAP_Upload")
        st.download_button(
            "Download merged Excel",
            data=buf.getvalue(),
            file_name="merged_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Zet alle drie de bestanden in sidebar om te starten.")
