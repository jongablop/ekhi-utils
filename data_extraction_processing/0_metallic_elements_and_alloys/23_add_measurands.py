"""
Step 20 — Add Measurands
========================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Tags each data entry with its measurand by matching column headers
    against the property name using case-insensitive substring matching.

Input:
    - processed_data_missing_entries_71-128/all_data_headers_cleaned_corrected.json — corrected JSON with table data

Output:
    - processed_data_missing_entries_71-128/all_data_headers_cleaned_corrected_with_measurand.json — JSON with added measurand field

Dependencies:
    - json, re
"""
import json
import re

def clean_header(header):
    """Remove parenthetical content from a column header string.

    Args:
        header: A column header string potentially containing parenthesised units.

    Returns:
        The header with all parenthetical substrings removed and whitespace stripped.
    """
    # Remove anything inside parentheses, including the parentheses themselves
    # Also strip whitespace around the remaining text
    return re.sub(r"\s*\(.*?\)", "", header).strip()

# Load your JSON data (assuming loaded into `data` variable)
#with open("processed_data/all_data_headers_cleaned_corrected.json", "r", encoding="utf-8") as f:
with open("processed_data_missing_entries_71-128/all_data_headers_cleaned_corrected.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

    for table_entry in all_data:
        data = table_entry.get("table_data")
        prop = table_entry.get("property").lower()
        measurand = ''
        for elem in data:
            d = elem.get("data")

            # Case-insensitive check: if a column header is a substring of the property name, it is the measurand
            for header in d["column_headers"]:

                if header.lower() in prop:
                    measurand = header
                    break

            elem["measurand"] = measurand

# Save back to JSON
#with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "w", encoding="utf-8") as f:
with open("processed_data_missing_entries_71-128/all_data_headers_cleaned_corrected_with_measurand.json", "w", encoding="utf-8") as f:

    json.dump(all_data, f, indent=2, ensure_ascii=True)