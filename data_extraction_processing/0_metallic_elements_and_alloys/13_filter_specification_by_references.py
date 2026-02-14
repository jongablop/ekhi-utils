"""
Step 02 — Filter Specification Tables by References
====================================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Filters Markdown specification tables so that only rows whose
    reference number appears in the validated references CSV are kept.

Input:
    - processed_data/specification_tables_metals.md — Markdown specification tables
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv — validated references

Output:
    - processed_data/specification_tables_metals-filtered.md — filtered Markdown
    - processed_data/specification_tables_metals-filtered-summary.txt — per-table row counts

Dependencies:
    - os, csv, re (standard library)
"""

import os
import csv
import re

def load_valid_references(csv_path):
    """Load the set of valid reference numbers from a CSV file.

    Args:
        csv_path: Path to the references CSV with a 'Reference' column.

    Returns:
        A set of reference number strings.
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        references = set(row['Reference'].strip() for row in reader if row['Reference'].strip())
    return references

def split_md_by_tables(md_lines):
    """Split Markdown content into sections delimited by '## SPECIFICATION TABLE' headings.

    Args:
        md_lines: List of lines from the Markdown file.

    Returns:
        A list of (title, block) tuples, where title is the heading line and
        block is the list of lines belonging to that section.
    """
    sections = []
    current_title = None
    current_block = []

    for line in md_lines:
        if line.startswith('## SPECIFICATION TABLE'):
            if current_block:
                sections.append((current_title or "Untitled Section", current_block))
                current_block = []
            current_title = line.strip()
        current_block.append(line)
    
    if current_block:
        sections.append((current_title or "Untitled Section", current_block))

    return sections


def parse_md_table_block(lines):
    """Parse a Markdown section into header, data, and trailing line groups.

    Args:
        lines: List of lines forming one Markdown table section.

    Returns:
        A tuple of (header_lines, data_lines, footer_lines) where header_lines
        includes the header row and separator, data_lines are the table body rows,
        and footer_lines are any lines after the table.
    """
    header_index = None
    for i, line in enumerate(lines):
        if re.match(r'\s*\|.*\|\s*', line) and '|' in line:
            if header_index is None:
                header_index = i
            elif i > header_index + 1:  # data rows
                continue

    if header_index is None:
        return lines, [], []

    header_line = lines[header_index].strip()
    separator_line = lines[header_index + 1].strip()
    data_lines = []
    i = header_index + 2

    while i < len(lines) and '|' in lines[i]:
        data_lines.append(lines[i].strip())
        i += 1

    # Return (header+separator lines, data rows, trailing lines after table)
    return lines[:header_index + 2], data_lines, lines[i:]

def filter_table_data(data_lines, header_line, valid_refs):
    """Filter table data rows to keep only those whose reference number is in valid_refs.

    Args:
        data_lines: List of pipe-delimited data row strings.
        header_line: The header row string (unused; ref column is hard-coded at index 2).
        valid_refs: Set of valid reference number strings.

    Returns:
        A tuple of (filtered_rows, count) where filtered_rows is the list of
        matching row strings and count is the number of matches.
    """
    #headers = [h.strip() for h in header_line.split('|') if h.strip()]
    #try:
#
    #    ref_index = headers.index('Ref. No.')
    #except ValueError:
    #    return data_lines, 0  # No Ref. No. column; skip filtering
    # Hard-coded column index for "Ref. No." (third column, zero-based index 2)
    ref_index = 2
    filtered = []
    for row in data_lines:
        cells = [c.strip() for c in row.split('|') if c.strip() or c == '']
        if len(cells) <= ref_index:
            continue
        ref = cells[ref_index]
        if ref in valid_refs:
            filtered.append(row)
    return filtered, len(filtered)

def filter_md_file_with_summary(md_path, csv_path, output_path, summary_path):
    """Filter a Markdown specification file by valid references and write a summary.

    Args:
        md_path: Path to the input Markdown specification tables file.
        csv_path: Path to the validated references CSV.
        output_path: Path for the filtered Markdown output.
        summary_path: Path for the per-table row count summary file.
    """
    valid_refs = load_valid_references(csv_path)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_lines = f.readlines()

    sections = split_md_by_tables(md_lines)

    output_lines = []
    summary_lines = []
    total_valid = 0

    for title, block in sections:
        output_lines.append(title + '\n')
        summary_entry = f"{title} --> "

        header, data_lines, footer = parse_md_table_block(block)

        if not data_lines:
            output_lines.extend(block[1:])  # no table
            summary_lines.append(summary_entry + "0 valid rows (no table found)")
            continue

        filtered_data, valid_count = filter_table_data(data_lines, header[0], valid_refs)

        output_lines.extend(header)
        output_lines.extend(line + '\n' for line in filtered_data)
        output_lines.extend(footer)

        summary_lines.append(f"{summary_entry}{valid_count} valid row(s)")
        total_valid += valid_count

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))

    print(f"✅ Filtered markdown written to: {output_path}")
    print(f"📄 Summary written to: {summary_path}")
    print(f"Total of valid curves: {total_valid}")

if __name__ == '__main__':
    # md_input = os.path.join('processed_data', 'specification_tables_metals.md')
    md_input = os.path.join('processed_data_missing_entries', 'all_specification_tables.md')
    csv_input = os.path.join('processed_data', 'touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv')
    
    base_name = os.path.splitext(md_input)[0]
    md_output = base_name + '-filtered.md'
    summary_output = base_name + '-filtered-summary.txt'

    filter_md_file_with_summary(md_input, csv_input, md_output, summary_output)
