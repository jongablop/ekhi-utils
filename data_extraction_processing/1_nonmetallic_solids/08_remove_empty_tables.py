"""
Step 08 — Remove Empty Tables and Merge Continued Sections
==========================================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Removes specification tables that contain no data rows (only headers
    and separators) and merges "(continued)" table sections into their
    parent table.

Input:
    - processed_data/md_files/*_specs.md — filtered specification Markdown files

Output:
    - processed_data/md_files/*_specs-clean.md — cleaned files without empties

Dependencies:
    - os, re
"""
import os
import re

def remove_or_merge_spec_tables(file_path, output_path):
    """Remove empty specification tables and merge continued table sections.

    Args:
        file_path: Path to the input specification Markdown file.
        output_path: Path where the cleaned output Markdown will be written.
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

            # Merge with previous if continued
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
    """Process all specification Markdown files in a folder, removing empty tables.

    Args:
        folder_path: Path to the folder containing *specs*.md files to clean.
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