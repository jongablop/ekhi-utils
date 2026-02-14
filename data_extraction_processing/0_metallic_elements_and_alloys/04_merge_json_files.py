"""
Step 14 — Merge JSON Files by Table
=====================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Merges per-page JSON files (from Step 13) into a single JSON file per
    data table. Validates that column headers are not purely integer placeholders,
    and handles duplicate curve IDs by appending the source filename as a suffix.

Input:
    - processed_data/extracted_json/*_page_*.json — per-page JSONs

Output:
    - processed_data/merged_json/table_NNN_*.json — one merged JSON per table

Dependencies:
    - os, json, re, collections
"""
import os
import json
import re
from collections import defaultdict

def is_header_valid(headers):
    """Check whether column headers are real names rather than OCR-fallback integer placeholders.

    Args:
        headers: List of column header values.

    Returns:
        True if at least one header is not a plain integer, False otherwise.
    """
    # Headers that are all integers are OCR-fallback placeholders, not real names
    return not all(isinstance(h, int) for h in headers)

def extract_table_info_from_filename(filename):
    """
    Extract table number and title from filename like:
    'Table_37_NORMAL SPECTRAL REFLECTANCE OF CHROMTIJM_page_1.json'
    """
    match = re.match(r"Table[_\- ](\d+)[_\- ]+(.*?)(?:_page_\d+)?\.json$", filename, re.IGNORECASE)
    if match:
        number = int(match.group(1))
        title = match.group(2).replace('_', ' ').strip()
        return number, title
    return None, None

def merge_json_files_by_table(input_folder, output_folder, max_table_number=436):
    """Merge per-page JSON files into one JSON file per data table.

    Args:
        input_folder: Directory containing per-page JSON files.
        output_folder: Directory where merged per-table JSON files will be written.
        max_table_number: Maximum table number to include (higher numbers are skipped).
    """
    os.makedirs(output_folder, exist_ok=True)
    grouped = defaultdict(list)

    # Step 1: Read and group files by table number
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith('.json'):
            continue

        table_number, title_from_filename = extract_table_info_from_filename(filename)
        if table_number is None or table_number > max_table_number:
            print(f"[!] Skipped: {filename}")
            continue

        path = os.path.join(input_folder, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        grouped[table_number].append((filename, data, title_from_filename))

    # Step 2: Merge and write output
    for table_number in sorted(grouped.keys()):
        entries = grouped[table_number]

        merged = {
            "table_title": entries[0][2],  # from filename
            "column_headers": [],
            "curves": {}
        }

        for fname, data, title in entries:
            if is_header_valid(data.get("column_headers", [])):
                merged["column_headers"] = data["column_headers"]

            merged["table_title"] = title

            for curve_id, curve_data in data.get("curves", {}).items():
                # Disambiguate duplicate curve IDs by appending source filename
                unique_curve_id = curve_id
                if unique_curve_id in merged["curves"]:
                    unique_curve_id = f"{curve_id}_{os.path.splitext(fname)[0]}"
                merged["curves"][unique_curve_id] = curve_data

        safe_title = re.sub(r'[^\w\d_-]+', '_', merged["table_title"].lower())
        output_filename = f"table_{table_number:03d}_{safe_title}.json"
        output_path = os.path.join(output_folder, output_filename)

        with open(output_path, 'w', encoding='utf-8') as out_file:
            json.dump(merged, out_file, indent=4)
            print(f"[✓] Merged Table {table_number} → {output_filename}")

# Example usage:
merge_json_files_by_table(
    input_folder="./processed_data/extracted_json",
    output_folder="./processed_data/merged_json"
)
