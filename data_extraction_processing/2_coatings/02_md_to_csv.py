"""
Step 02 — Markdown Table to CSV
================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Converts the updated markdown bibliography table into a CSV file
    for easier downstream filtering and programmatic access.

Input:
    - raw_data/Touloukian-coatings_bibliografia-updated.md
      — augmented bibliography markdown table from Step 01

Output:
    - processed_data/Touloukian-coatings_bibliografia-updated.csv
      — same data in CSV format

Dependencies:
    - os, csv, re
"""
import os
import csv
import re

def ensure_dir(path):
    """Create the directory at path if it does not already exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def parse_markdown_table(md_lines):
    """Parse markdown table lines into a list of rows, each row a list of cell strings.

    Args:
        md_lines: Lines of a markdown file containing a pipe-delimited table.

    Returns:
        List of rows where each row is a list of stripped cell values.
    """
    # Filter out separator lines and empty lines
    table_lines = [
        line.strip() for line in md_lines 
        # Skip separator lines (e.g. |---|---|) and blank lines
        if line.strip() and not re.match(r'^\s*\|?[-| ]+\|?\s*$', line)
    ]

    parsed_rows = []
    for line in table_lines:
        # Remove <br> tags and strip spaces
        line = line.replace('<br>', '').strip()
        # Split by '|' and remove first and last if empty
        cols = [col.strip() for col in line.split('|')]
        if cols and cols[0] == '':
            cols = cols[1:]
        if cols and cols[-1] == '':
            cols = cols[:-1]
        parsed_rows.append(cols)

    return parsed_rows

def convert_md_to_csv(input_file, output_file):
    """Read a markdown table file and write its contents as a CSV file.

    Args:
        input_file: Path to the input markdown file.
        output_file: Path to the output CSV file.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rows = parse_markdown_table(lines)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def main(origin_folder, final_folder, filename):
    """Convert a single markdown table file to CSV, creating directories as needed.

    Args:
        origin_folder: Directory containing the source markdown file.
        final_folder: Directory where the output CSV will be written.
        filename: Name of the markdown file to convert.
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
    file_name = 'Touloukian-coatings_bibliografia-updated.md'

    main(origin, final, file_name)
