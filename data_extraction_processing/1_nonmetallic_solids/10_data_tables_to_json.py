"""
Step 10 — Data Tables to JSON
==============================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Parses data-table Markdown files into structured JSON using a state
    machine that tracks DATA TABLE headers, bracket column headers
    [h1; h2], and CURVE blocks. Produces per-file and merged JSON.

Input:
    - processed_data/md_files/*_data.md — filtered data Markdown files

Output:
    - processed_data/data_tables_json/*.json — per-file JSON
    - processed_data/data_tables_json/merged.json — all data tables merged

Dependencies:
    - os, re, json, collections

Note:
    Column headers inside brackets use semicolons as separators; falls
    back to commas if only one part is found (OCR artifact workaround).
"""
import os
import re
import json
from collections import defaultdict

def extract_curves_from_md(md_path):
    """Parse data-table Markdown into structured dicts with table titles, headers, and curve data.

    Args:
        md_path: Path to the filtered data Markdown file.

    Returns:
        List of dicts, each with table_title, column_headers, and curves data.
    """
    tables = []

    with open(md_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    current_table = None
    current_curve = None
    current_headers = []

    def save_current_table():
        """Append the current table dict to the tables list if it has a title."""
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

        # 2. Column headers inside [ ... ] -- semicolon-separated, with comma fallback
        if clean_line.startswith("[") and clean_line.endswith("]") and current_table:
            headers = clean_line.strip("[]").split(";")
            # OCR sometimes misses semicolons; fall back to comma splitting
            if len(headers) == 1:
                headers = clean_line.strip("[]").split(",")
            # Reformat any remaining commas inside headers as parenthetical qualifiers
            current_headers = [h.strip().replace(",", " (") + ")" for h in headers]
            current_table["column_headers"] = current_headers
            continue

        # 3. Detect curves
        match = re.match(r"CURVE\s+(\d+)\*?", clean_line, re.IGNORECASE)
        if match and current_table:
            current_curve = match.group(1)
            continue

        # 4. Data row: must be pipe-delimited, not a separator (no colons), and inside a curve
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
    """Convert all data-table Markdown files in a folder to JSON and produce a merged file.

    Args:
        input_folder: Directory containing *_data.md files.
        output_folder: Directory where per-file and merged JSON files are written.
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
