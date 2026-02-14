"""
Step 00 — Markdown to CSV
=========================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Converts a Markdown reference table into a CSV file, parsing
    pipe-delimited rows and stripping HTML tags.

Input:
    - raw_data/touloukian-metals-alloys-references.md — Markdown table of references

Output:
    - processed_data/touloukian-metals-alloys-references.csv — CSV version of the table

Dependencies:
    - os, csv, re (standard library)
"""

import os
import csv
import re

def ensure_dir(path):
    """Create the directory at path if it does not already exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def parse_markdown_table(md_lines):
    """Parse pipe-delimited Markdown table lines into a list of row lists.

    Args:
        md_lines: Raw lines from a Markdown file containing a pipe-delimited table.

    Returns:
        A list of lists, where each inner list contains the cell values for one row.
    """
    # Filter out separator lines and empty lines
    table_lines = [
        line.strip() for line in md_lines 
        # Skip Markdown separator rows (e.g., |---|---|)
        if line.strip() and not re.match(r'^\s*\|?[-| ]+\|?\s*$', line)
    ]

    parsed_rows = []
    for line in table_lines:
        line = line.replace('<br>', '').strip()
        # Split on pipe and trim leading/trailing empty cells from outer pipes
        cols = [col.strip() for col in line.split('|')]
        if cols and cols[0] == '':
            cols = cols[1:]
        if cols and cols[-1] == '':
            cols = cols[:-1]
        parsed_rows.append(cols)

    return parsed_rows

def convert_md_to_csv(input_file, output_file):
    """Read a Markdown table file and write its contents as CSV.

    Args:
        input_file: Path to the input Markdown file.
        output_file: Path to the output CSV file.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rows = parse_markdown_table(lines)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def main(origin_folder, final_folder, filename):
    """Convert a Markdown reference table to CSV, creating directories as needed.

    Args:
        origin_folder: Directory containing the source Markdown file.
        final_folder: Directory where the output CSV will be written.
        filename: Name of the Markdown file to convert.
    """
    ensure_dir(origin_folder)
    ensure_dir(final_folder)

    md_path = os.path.join(origin_folder, filename)
    csv_filename = os.path.splitext(filename)[0] + '.csv'
    csv_path = os.path.join(final_folder, csv_filename)

    convert_md_to_csv(md_path, csv_path)
    print(f"✅ Converted '{md_path}' to '{csv_path}'")

if __name__ == '__main__':
    # Customize your folders and file name
    origin = 'raw_data'
    final = 'processed_data'
    file_name = 'touloukian-metals-alloys-references.md'

    main(origin, final, file_name)
