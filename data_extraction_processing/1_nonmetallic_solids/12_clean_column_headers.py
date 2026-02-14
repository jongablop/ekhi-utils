"""
Step 12 — Clean Column Headers
===============================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Strips parenthetical content (e.g., unit annotations from OCR) from
    column header strings in the joined data JSON.

Input:
    - processed_data/all_data.json — joined metadata + data

Output:
    - processed_data/all_data_headers_cleaned.json — same data with cleaned headers

Dependencies:
    - json, re
"""
import json
import re

def clean_header(header):
    """Remove parenthetical content (e.g., unit annotations) from a column header string."""
    # Remove parenthetical content like "(unit)" from OCR-extracted headers
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
