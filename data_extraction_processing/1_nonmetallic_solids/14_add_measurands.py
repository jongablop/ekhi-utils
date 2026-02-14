"""
Step 14 — Add Measurands
=========================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Tags each curve entry with its measurand by matching column header
    names against the table's property field (e.g., if the property
    contains "Emittance" and a header is "Emittance", that is the measurand).

Input:
    - processed_data/all_data_headers_cleaned_corrected.json

Output:
    - processed_data/all_data_headers_cleaned_corrected_with_measurand.json

Dependencies:
    - json, re
"""
import json
import re

def clean_header(header):
    """Remove parenthetical content from a column header string."""
    # Remove parenthetical content from headers
    return re.sub(r"\s*\(.*?\)", "", header).strip()

# Load JSON data with corrected headers
with open("processed_data/all_data_headers_cleaned_corrected.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

    for table_entry in all_data:
        data = table_entry.get("table_data")
        prop = table_entry.get("property").lower()
        measurand = ''
        for elem in data:
            d = elem.get("data")     

            # Find the column header whose name appears in the property string
            for header in d["column_headers"]:
                if header.lower() in prop:
                    measurand = header
                    break

            elem["measurand"] = measurand

# Save back to JSON
#with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "w", encoding="utf-8") as f:
with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "w", encoding="utf-8") as f:

    json.dump(all_data, f, indent=2, ensure_ascii=True)