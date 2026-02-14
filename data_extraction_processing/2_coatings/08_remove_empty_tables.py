"""
Step 08 — Remove Empty Specification Tables
=============================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Removes specification tables that contain no data rows (only headers
    and separators) and merges "(continued)" sections back into their
    parent table to produce a clean, consolidated spec file.

Input:
    - processed_data/md_files/*_filtered_specs.md — filtered spec files

Output:
    - processed_data/md_files/*_filtered_specs-clean.md — cleaned specs

Dependencies:
    - os, re
"""
import os
import re

def remove_or_merge_spec_tables(file_path, output_path):
    """Remove empty specification tables and merge '(continued)' sections into their parent.

    Args:
        file_path: Path to the input filtered specs markdown file.
        output_path: Path for the cleaned output markdown file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []
    current_table = []
    inside_table = False
    last_table_index = None

    # Updated regex to handle headings, period or colon, and extra spaces
    spec_table_pattern = re.compile(
        r"^\s*(?:#{1,6}\s*)?SPECIFICATION TABLE NO\.\s*(\d+)(?:[.:])?\s*(.*)",
        re.IGNORECASE
    )

    for line in lines:
        match = spec_table_pattern.match(line)
        if match:
            title_suffix = match.group(2).strip()

            # Merge "(continued)" tables into their parent by appending rows
            if "(continued)" in title_suffix.lower() and last_table_index is not None:
                for l in [] if not current_table else current_table:
                    pass  # no-op, just to avoid unused var warning
                inside_table = True
                current_table = output_lines[last_table_index]
                continue

            # End previous table (check if data exists)
            if current_table:
                if not table_has_data(current_table):
                    output_lines.pop(last_table_index)
                current_table = []

            # Start new table
            current_table = [line]
            output_lines.append(current_table)
            last_table_index = len(output_lines) - 1
            inside_table = True
            continue

        if inside_table:
            if "|" in line:
                # If this is a continued table, skip duplicate headers/separators
                if is_header_or_separator(line) and last_table_index is not None:
                    if any(is_header_or_separator(l) for l in output_lines[last_table_index]):
                        continue
                current_table.append(line)
            else:
                inside_table = False

        if not inside_table:
            output_lines.append([line])  # non-table content

    # Handle last table
    if current_table and not table_has_data(current_table):
        output_lines.pop(last_table_index)

    # Flatten & write cleaned file
    with open(output_path, "w", encoding="utf-8") as f:
        for block in output_lines:
            f.writelines(block)

def is_header_or_separator(line):
    """Detects if a line is a table header or separator row."""
    return (
        line.strip().lower().startswith("| curve no.") or
        re.match(r"^\s*\|(\s*:?[-]+:?)+\s*\|", line.strip())
    )

def table_has_data(table_lines):
    """Check if a table contains data rows (beyond headers and separators)."""
    for l in table_lines:
        if "|" in l and not is_header_or_separator(l):
            return True
    return False

def process_folder(folder_path):
    """Process all spec markdown files in a folder, removing empty tables from each.

    Args:
        folder_path: Directory containing filtered spec markdown files.
    """
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".md") and "specs" in filename.lower():
            file_path = os.path.join(folder_path, filename)
            clean_name = f"{os.path.splitext(filename)[0]}-clean.md"
            output_path = os.path.join(folder_path, clean_name)
            print(f"Processing: {file_path} → {output_path}")
            remove_or_merge_spec_tables(file_path, output_path)

# Example usage:
# process_folder("path/to/your/folder")

process_folder('./processed_data/md_files')