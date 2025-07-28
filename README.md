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
construction and Month of construction.


Equipment numbers are treated as strings so leading zeros are preserved. If your
file stores them as numbers, the app converts that column with `astype(str)` so
matching works even if pandas originally inferred a numeric type.
=======

