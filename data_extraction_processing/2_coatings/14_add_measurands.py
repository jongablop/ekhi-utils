"""
Step 14 — Add Measurands
==========================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Tags each curve entry with its measurand by matching column headers
    against the table-level property name. If a header appears as a
    substring of the property, it is identified as the measurand.

Input:
    - processed_data/all_data_headers_cleaned_corrected.json — corrected
      JSON from Step 13

Output:
    - processed_data/all_data_headers_cleaned_corrected_with_measurand.json
      — JSON with a "measurand" field added to each curve entry

Dependencies:
    - json, re
"""
import json
import re

def clean_header(header):
    """Remove parenthetical content from a column header string.

    Args:
        header: A column header string potentially containing parenthetical text.

    Returns:
        The header with parenthetical substrings removed and whitespace trimmed.
    """
    # Remove parenthetical content and surrounding whitespace
    return re.sub(r"\s*\(.*?\)", "", header).strip()

with open("processed_data/all_data_headers_cleaned_corrected.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

    for table_entry in all_data:
        data = table_entry.get("table_data")
        prop = table_entry.get("property").lower()
        measurand = ''
        for elem in data:
            d = elem.get("data")     

            # Identify the measurand: first header that is a substring of the property name
            for header in d["column_headers"]:

                if header.lower() in prop:
                    measurand = header
                    break

            elem["measurand"] = measurand

# Save back to JSON
#with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "w", encoding="utf-8") as f:
with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "w", encoding="utf-8") as f:

    json.dump(all_data, f, indent=2, ensure_ascii=True)