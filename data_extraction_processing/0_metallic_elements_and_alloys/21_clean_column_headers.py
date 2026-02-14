"""
Step 18 — Clean Column Headers
================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Strips parenthetical content from column header strings (e.g. removes
    units or qualifiers in parentheses) using the regex r"\\s*\\(.*?\\)" so
    that downstream steps receive uniform property names.

Input:
    - processed_data/all_data.json — enriched JSON from Step 16

Output:
    - processed_data/all_data_headers_cleaned.json — JSON with cleaned headers

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
with open("processed_data_missing_entries_71-128/all_data.json", "r", encoding="utf-8") as f:
#with open("processed_data/all_data.json", "r", encoding="utf-8") as f:    
    all_data = json.load(f)

    for table_entry in all_data:
        data = table_entry.get("table_data")
        
        for elem in data:
            d = elem.get("data")     

            cleaned_headers = [clean_header(h) if isinstance(h, str) else h for h in d["column_headers"]]
            d["column_headers"] = cleaned_headers


# Save back to JSON
#with open("processed_data/all_data_headers_cleaned.json", "w", encoding="utf-8") as f:
with open("processed_data_missing_entries_71-128/all_data_headers_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=True)
