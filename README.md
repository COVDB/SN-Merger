# SN-Merger

This repository contains a small Streamlit application that merges data from
three Excel sheets. Initially only the **AM LOG** sheet is processed. The app
filters rows by a predefined set of equipment numbers and displays selected
columns.

## Running the app

Install the dependencies and start Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

You will be prompted to upload the following Excel files:

1. `AM LOG`
2. `ZSD_PO_PER_SO`
3. `ZSTATUS`

After uploading the **AM LOG** file, the app shows the filtered rows containing
only the columns Delivery Date, Customer Reference, Serial number, Year of
construction and Month of construction. Upload buttons and filtering controls
are available in the sidebar. The year and month of construction are
automatically derived from the Delivery Date. The sidebar also lists the
equipment numbers used for filtering and lets you add or remove them.


If you also upload the **ZSD_PO_PER_SO** sheet, rows are enriched with the
matching *Document* and *Material* columns when `Customer Reference` values from
AM LOG correspond to `Document` values in ZSD_PO_PER_SO.







Equipment numbers are treated as strings so leading zeros are preserved. If your
file stores them as numbers, the app converts that column with `astype(str)` so
matching works even if pandas originally inferred a numeric type.
