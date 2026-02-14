"""
Step 10 — Data Tables to JSON
===============================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Parses filtered data-table markdown files into structured JSON.
    Uses bracket-delimited headers ([col1; col2; ...]), CURVE markers,
    and a state machine to extract numerical curve data per table.

Input:
    - processed_data/md_files/*_filtered_data.md — filtered data markdown

Output:
    - processed_data/data_tables_json/<name>.json — per-file JSON
    - processed_data/data_tables_json/merged.json — merged JSON of all
      data tables

Dependencies:
    - os, re, json, collections
"""
import os
import re
import json
from collections import defaultdict

def extract_curves_from_md(md_path):
    """Parse a filtered data-table markdown file into structured table/curve dicts.

    Uses bracket-delimited headers, CURVE markers, and a state machine to
    extract numerical curve data per table.

    Args:
        md_path: Path to the filtered data markdown file.

    Returns:
        List of table dicts, each containing table_title, column_headers,
        and a nested curves dict mapping curve numbers to column data lists.
    """
    tables = []

    with open(md_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    current_table = None
    current_curve = None
    current_headers = []

    def save_current_table():
        """Append the current table to the results list if it has a title."""
        if current_table and current_table["table_title"]:
            tables.append(current_table.copy())

    for line in lines:
        clean_line = line.lstrip("#").strip()  # remove markdown heading markers

        # 1. Detect start of a new DATA TABLE
        if re.match(r"DATA\s+TABLE\s+NO\.?\s*\d+", clean_line, re.IGNORECASE):
            save_current_table()
            current_table = {
                "table_title": clean_line,
                "column_headers": [],
                "curves": defaultdict(lambda: defaultdict(list))
            }
            current_curve = None
            current_headers = []
            continue

        # 2. Column headers inside [ ... ] — semicolon-delimited, comma fallback
        if clean_line.startswith("[") and clean_line.endswith("]") and current_table:
            headers = clean_line.strip("[]").split(";")
            # OCR sometimes misses semicolons; fall back to comma splitting
            if len(headers) == 1:
                headers = clean_line.strip("[]").split(",")
            # Reformat remaining commas inside each header as parenthetical units
            current_headers = [h.strip().replace(",", " (") + ")" for h in headers]
            current_table["column_headers"] = current_headers
            continue

        # 3. Detect curves
        match = re.match(r"CURVE\s+(\d+)\*?", clean_line, re.IGNORECASE)
        if match and current_table:
            current_curve = match.group(1)
            continue

        # 4. Data row: pipe-delimited, no colons (skip separator rows)
        if "|" in clean_line and re.match(r"^\|.*\|$", clean_line) and ":" not in clean_line and current_curve:
            parts = [p.strip() for p in clean_line.strip("|").split("|")]

            # If we don't have headers but this row looks like a markdown header row
            if not current_headers and all(parts):
                current_headers = parts
                current_table["column_headers"] = current_headers
                continue

            try:
                for j, val in enumerate(parts):
                    if val:
                        key = current_headers[j] if j < len(current_headers) else f"col{j+1}"
                        current_table["curves"][current_curve][key].append(float(val))
            except ValueError:
                continue


    save_current_table()
    return tables


def process_md_files(input_folder, output_folder):
    """Convert all filtered data markdown files in a folder to JSON and merge them.

    Args:
        input_folder: Directory containing *_filtered_data.md files.
        output_folder: Directory where per-file and merged JSON will be written.
    """
    os.makedirs(output_folder, exist_ok=True)
    all_tables = []

    md_files = [f for f in os.listdir(input_folder)
                if f.lower().endswith('.md') and 'data' in f.lower()]

    for md_file in md_files:
        md_path = os.path.join(input_folder, md_file)
        print(f"Processing: {md_file}")

        tables = extract_curves_from_md(md_path)

        base_name = os.path.splitext(md_file)[0]
        json_filename = f"{base_name}.json"
        output_path = os.path.join(output_folder, json_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(tables, f, indent=4)

        print(f"  Saved: {json_filename}")
        all_tables.extend(tables)

    merged_path = os.path.join(output_folder, "merged.json")
    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(all_tables, f, indent=4)
    print(f"Merged JSON saved to {merged_path}")


# Example usage
input_folder = "./processed_data/md_files"
output_folder = "./processed_data/data_tables_json"

process_md_files(input_folder, output_folder)
