"""
Step 09 — Specification Tables to JSON
=======================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Parses cleaned specification-table Markdown files into structured JSON.
    Splits the table title on "of" to separate property from material name.
    Processes all *-clean.md files and produces a merged JSON.

Input:
    - processed_data/md_files/*-clean.md — cleaned specification Markdown

Output:
    - processed_data/specification_tables_json/*.json — per-file JSON
    - processed_data/specification_tables_json/all_specification_tables.json — merged

Dependencies:
    - os, re, json
"""
import os
import re
import json

def parse_md_table(md_lines):
    """Parse Markdown table lines into a list of dictionaries keyed by header names.

    Args:
        md_lines: List of Markdown table lines (including header and separator rows).

    Returns:
        List of dicts, one per data row, with header names as keys.
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
    """Parse specification tables from a Markdown file and write them as JSON.

    Args:
        input_path: Path to the cleaned specification Markdown file.
        output_path: Path where the output JSON will be written.

    Returns:
        List of dicts, each containing table number, property, material, and table_data.
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

            # Split title on "of" to separate property name from material name
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
    """Convert all cleaned specification Markdown files in a folder to JSON and merge them.

    Args:
        input_folder: Directory containing *-clean.md specification files.
        output_folder: Directory where per-file and merged JSON files are written.
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
