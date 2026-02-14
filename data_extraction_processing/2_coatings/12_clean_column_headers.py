"""
Step 12 — Clean Column Headers
================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Strips parenthetical content (e.g. units, annotations) from every
    column header in the enriched data JSON so that downstream steps
    receive clean, uniform header names.

Input:
    - processed_data/all_data.json — enriched JSON from Step 11

Output:
    - processed_data/all_data_headers_cleaned.json — JSON with cleaned
      column headers

Dependencies:
    - json, re
"""
import json
import re

def clean_header(header):
    """Remove parenthetical content (e.g. units, annotations) from a column header.

    Args:
        header: A column header string potentially containing parenthetical text.

    Returns:
        The header string with all parenthetical substrings removed and whitespace trimmed.
    """
    # Remove parenthetical content and surrounding whitespace
    return re.sub(r"\s*\(.*?\)", "", header).strip()

# Load your JSON data (assuming loaded into `data` variable)
with open("processed_data/all_data.json", "r", encoding="utf-8") as f:
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
with open("processed_data/all_data_headers_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=True)
