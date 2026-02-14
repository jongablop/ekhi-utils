"""
Step 16 — Join Data and Metadata
==================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Joins the specification/metadata JSON (material composition, remarks) with
    the extracted curve data by matching on (table_number, curve_number). Curves
    that cannot be matched are logged to a missing-curves text file for manual
    review.

Input:
    - processed_data/specification_tables_metals-filtered-clean.json — spec metadata
    - processed_data/normalized_curves_json/ — folder of curve JSONs

Output:
    - processed_data/all_data.json — enriched JSON with metadata + curve data
    - missing_curves.txt — list of unmatched table/curve pairs

Dependencies:
    - os, json
"""
import os
import json

def find_curve_data(table_num, curve_num, curve_data_folder):
    """Look up curve data for a given table and curve number from JSON files on disk.

    Args:
        table_num: The specification table number.
        curve_num: The curve number within that table.
        curve_data_folder: Directory containing normalised curve JSON files.

    Returns:
        A dict with 'column_headers' and 'curve' keys if found, or None if not matched.
    """
    # Zero-pad table number to 3 digits to match filename convention (e.g. "table_037_")
    table_num_padded = str(table_num).zfill(3)
    pattern = f"table_{table_num_padded}_"

    for fname in os.listdir(curve_data_folder):
        if fname.startswith(pattern) and fname.endswith(".json"):
            json_path = os.path.join(curve_data_folder, fname)
            with open(json_path, "r", encoding="utf-8") as f:
                curve_json = json.load(f)
            
            curves = curve_json.get("curves", {})
            column_headers = curve_json.get("column_headers", [])

            # Prefix-match curve number to handle suffixed keys like "15_page_2"
            cleaned_curve_num = str(curve_num).strip()
            matched_curve = None
            for key in curves.keys():
                if key.startswith(cleaned_curve_num):
                    matched_curve = key
                    break

            if matched_curve:
                return {
                    "column_headers": column_headers,
                    "curve": curves[matched_curve]
                }
    return None


def enrich_metadata(metadata_file, curve_data_folder, output_file, missing_file="missing_curves.txt"):
    """Join specification metadata with extracted curve data and write the enriched JSON.

    Args:
        metadata_file: Path to the specification tables JSON.
        curve_data_folder: Directory containing normalised curve JSON files.
        output_file: Path for the output enriched JSON.
        missing_file: Path for the text file listing unmatched table/curve pairs.
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
            curve_info = find_curve_data(table_num, curve_num, curve_data_folder)

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
    #metadata_file="./processed_data/specification_tables_metals-filtered-clean.json",
    #metadata_file="./processed_data_missing_entries/specification_tables_metals-filtered-clean.json",
    metadata_file="./processed_data_missing_entries_71-128/specification_tables_metals-filtered-clean.json",
    curve_data_folder="./processed_data/normalized_curves_json",
    output_file="./processed_data_missing_entries_71-128/all_data.json"
    #output_file="./processed_data_missing_entries/all_data.json"
    #output_file="./processed_data/all_data.json"
)
