"""
Step 09 — Specification Tables to JSON
========================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Parses cleaned specification-table markdown files into structured
    JSON. Splits each table title on the word "of" to separate the
    measured property from the material name, and collects all row data.

Input:
    - processed_data/md_files/*-clean.md — cleaned spec markdown files

Output:
    - processed_data/specification_tables_json/<name>.json — per-file JSON
    - processed_data/specification_tables_json/all_specification_tables.json
      — merged JSON of all specification tables

Dependencies:
    - os, re, json
"""
import os
import re
import json

def parse_md_table(md_lines):
    """Parse pipe-delimited markdown table lines into a list of row dictionaries.

    Args:
        md_lines: List of strings representing lines of a markdown table.

    Returns:
        List of dicts mapping column headers to cell values for each data row.
    """
    headers = []
    rows = []
    for line in md_lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        parts = [cell.strip() for cell in line.strip('|').split('|')]

        # Header
        if not headers:
            headers = parts
            continue

        # Skip alignment line
        if all(re.match(r'^:?-+:?$', cell) for cell in parts):
            continue

        # Data row
        if len(parts) == len(headers):
            rows.append(dict(zip(headers, parts)))
        else:
            padded = parts + [''] * (len(headers) - len(parts))
            rows.append(dict(zip(headers, padded)))

    return rows

def md_to_json(input_path, output_path):
    """Convert a cleaned specification-table markdown file to structured JSON.

    Splits each table title on 'of' to separate the measured property from the
    material name, and collects all row data into a list of table objects.

    Args:
        input_path: Path to the cleaned spec markdown file.
        output_path: Path for the output JSON file.

    Returns:
        List of table dicts with keys: table, property, material, table_data.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = []
    i = 0
    spec_pattern = re.compile(
        r'^\s*#{0,6}\s*SPECIFICATION TABLE NO\.\s*(\d+)\s*[.:]?\s*(.+)$',
        re.IGNORECASE
    )

    while i < len(lines):
        line = lines[i].strip()
        match = spec_pattern.match(line)
        if match:
            table_number = match.group(1)
            title = match.group(2).strip()

            # Split title on "of" to separate property from material name
            if " of " in title.lower():
                parts = re.split(r'\bof\b', title, flags=re.IGNORECASE)
                prop = parts[0].strip()
                material = parts[1].strip()
            else:
                prop = title
                material = ""

            # Skip to first table line
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('|'):
                i += 1

            # Collect table lines
            table_lines = []
            while i < len(lines) and (
                lines[i].strip().startswith('|') or
                re.match(r'^\s*[:|\- ]+\s*$', lines[i])
            ):
                table_lines.append(lines[i])
                i += 1

            if table_lines:
                table_data = parse_md_table(table_lines)
                result.append({
                    "table": table_number,
                    "property": prop,
                    "material": material,
                    "table_data": table_data
                })
        else:
            i += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"Saved JSON to {output_path}")
    return result

def process_folder(input_folder, output_folder):
    """Convert all cleaned spec markdown files in a folder to JSON and merge them.

    Args:
        input_folder: Directory containing *-clean.md spec files.
        output_folder: Directory where per-file and merged JSON will be written.
    """
    os.makedirs(output_folder, exist_ok=True)
    all_tables = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith("-clean.md"):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_folder, output_filename)

            result = md_to_json(input_path, output_path)
            all_tables.extend(result)

    # Save merged file
    merged_path = os.path.join(output_folder, "all_specification_tables.json")
    with open(merged_path, 'w', encoding='utf-8') as f:
        json.dump(all_tables, f, indent=2)
    print(f"Saved merged JSON to {merged_path}")

# Example usage:
# process_folder("clean_md_folder", "json_output_folder")

# Example usage:
process_folder("processed_data/md_files", "processed_data/specification_tables_json")
