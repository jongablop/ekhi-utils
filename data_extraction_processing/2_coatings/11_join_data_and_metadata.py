"""
Step 11 — Join Data and Metadata
==================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Joins specification-table metadata with curve data by matching
    (table number, curve number) pairs, producing a single enriched
    JSON and a report of any curves that could not be matched.

Input:
    - processed_data/specification_tables_json/all_specification_tables.json
      — spec metadata from Step 09
    - processed_data/data_tables_json/merged.json
      — curve data from Step 10

Output:
    - processed_data/all_data.json — enriched JSON with metadata + data
    - missing_curves.txt — list of unmatched (table, curve) pairs

Dependencies:
    - os, json, re
"""
import os
import json
import re

def extract_table_number(title):
    """Extract the integer table number from a DATA TABLE title string.

    Args:
        title: A string like 'DATA TABLE NO. 42'.

    Returns:
        The table number as an int, or None if no match is found.
    """
    match = re.search(r"DATA\s+TABLE\s+NO\.?\s*(\d+)\.?", title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def find_curve_data(table_num, curve_num, data_file):
    """Look up curve data for a given table and curve number in the merged data JSON.

    Args:
        table_num: The specification/data table number to match.
        curve_num: The curve number within the table.
        data_file: Path to the merged data tables JSON file.

    Returns:
        Dict with 'column_headers' and 'curve' data if found, or None.
    """
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for curve_json in data:

        curve_table_number = extract_table_number(curve_json.get("table_title"))
        #print(curve_table_number, table_num)
        if int(curve_table_number) != int(table_num):
            continue  # skip if wrong table
        else:
            print(curve_table_number, table_num)

        curves = curve_json.get("curves", {})
        column_headers = curve_json.get("column_headers", [])

        cleaned_curve_num = str(curve_num).strip()
        # Case-insensitive match of curve number keys (handles whitespace)
        matched_curve = None
        for key in curves.keys():
            if key.strip().lower() == cleaned_curve_num.strip().lower():
                matched_curve = key
                break

        if matched_curve:
            return {
                "column_headers": column_headers,
                "curve": curves[matched_curve]
            }
    return None


def enrich_metadata(metadata_file, data_file, output_file, missing_file="missing_curves.txt"):
    """Join specification metadata with curve data and write the enriched result.

    Matches each (table, curve) pair from the spec metadata to its corresponding
    data in the merged data JSON. Unmatched curves are logged to a missing file.

    Args:
        metadata_file: Path to the all_specification_tables JSON.
        data_file: Path to the merged data tables JSON.
        output_file: Path for the enriched output JSON.
        missing_file: Path for the text file listing unmatched curves.
    """
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    if isinstance(metadata, dict):
        metadata = [metadata]

    found_count = 0
    missing_count = 0
    missing_entries = []

    for table_entry in metadata:
        table_num = table_entry.get("table")

        enriched_table_data = []
        for entry in table_entry.get("table_data", []):
            curve_num = entry.get("Curve No.")
            curve_info = find_curve_data(table_num, curve_num, data_file)

            if curve_info:
                entry["data"] = curve_info
                enriched_table_data.append(entry)
                found_count += 1
            else:
                missing_count += 1
                missing_entries.append(f"Table {table_num}, Curve {curve_num}: '{entry.get('Composition (weight percent), Specifications and Remarks', '')}'")

        table_entry["table_data"] = enriched_table_data

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    with open(missing_file, "w", encoding="utf-8") as f:
        for line in missing_entries:
            f.write(line + "\n")

    print(f"[✓] Expanded JSON saved to {output_file}")
    print(f"[!] Curves found: {found_count}")
    print(f"[!] Curves missing: {missing_count}")
    print(f"[!] Missing curve info saved to {missing_file}")


# Example usage:
enrich_metadata(
    metadata_file="./processed_data/specification_tables_json/all_specification_tables.json",
    data_file="./processed_data/data_tables_json/merged.json",
    output_file="./processed_data/all_data.json"
)
