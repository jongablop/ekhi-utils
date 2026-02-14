"""
Step 00 — Correct Multi-Curve Tables
=====================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Splits multi-curve Markdown data tables into individual single-curve
    blocks so that downstream parsers can process one curve at a time.

Input:
    - raw_data/09_glasses/09_ceramicos.md — Markdown with multi-curve tables

Output:
    - raw_data/09_glasses/09_ceramicos-corrected.md — Markdown with each
      curve in its own table block

Dependencies:
    - re, pathlib
"""
import re
from pathlib import Path

# Matches Markdown alignment cells like :---, ---:, :---:
ALIGN_CELL_RE = re.compile(r'^\s*:?-+:?\s*$')

def split_md_row(row: str):
    """Split a markdown table row into cells, preserving internal empties."""
    cells = row.rstrip("\n")
    parts = cells.split("|")
    # drop leading/trailing fence empties only
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]

def is_alignment_row(parts):
    """Return True if all cells in parts match the Markdown alignment pattern (e.g., :---)."""
    return parts and all(ALIGN_CELL_RE.match(c or "") for c in parts)

def looks_like_data_table_title(line: str) -> bool:
    """Return True if the line matches a 'DATA TABLE NO.' heading pattern."""
    clean = line.lstrip("#").strip()
    # Match with optional bold markers (**) before DATA TABLE NO.
    return bool(re.match(r"^\*?\*?\s*DATA\s+TABLE\s+NO\.?", clean, re.IGNORECASE))

def looks_like_bracket_header(line: str) -> bool:
    """Detect column-header lines like *[Temperature, T, K; Emittance, E]*."""
    s = line.strip()
    return (s.startswith("*[") and s.endswith("]*")) or (s.startswith("[") and s.endswith("]"))

def is_table_row(line: str) -> bool:
    """Return True if the line starts with a pipe character, indicating a Markdown table row."""
    return line.lstrip().startswith("|")

def parse_multicurve_table_block(table_lines):
    """
    Parse a multi-curve table block (the contiguous '|' lines).
    Returns (col_names, ordered_curve_labels, curves_data)
      - col_names: ['T','E'] (or whatever is in the header row)
      - ordered_curve_labels: e.g., ['CURVE 1','CURVE 4','CURVE 2',...]
      - curves_data: dict label -> list of (v1, v2) strings
    """
    if not table_lines:
        return None

    # Row 0: curve labels row (e.g. CURVE 1 | | CURVE 4 | | ...)
    label_cells = split_md_row(table_lines[0])
    curve_labels = [c for c in label_cells if re.search(r'\bCURVE\s+\d+', c, re.IGNORECASE)]
    if not curve_labels:
        return None  # not multi-curve

    # Find alignment row index
    idx = 1
    while idx < len(table_lines) and not is_alignment_row(split_md_row(table_lines[idx])):
        idx += 1
    if idx >= len(table_lines):
        return None  # malformed table
    idx += 1  # move past alignment row

    # Header row (per-curve headers like **T** | **E** | **T** | **E** | ...)
    if idx >= len(table_lines):
        return None
    header_parts = split_md_row(table_lines[idx])
    # Strip bold markers (**) and use the first pair as canonical column names
    header_parts_clean = [re.sub(r'^\*+|\*+$', '', h).strip() for h in header_parts]
    if len(header_parts_clean) < 2:
        col_names = ["col1", "col2"]
    else:
        col_names = [header_parts_clean[0] or "col1", header_parts_clean[1] or "col2"]
    idx += 1

    # Data rows
    curves_data = {lab: [] for lab in curve_labels}
    n_curves = len(curve_labels)
    expected_cols = n_curves * 2  # Each curve has two columns (e.g., T and E)

    while idx < len(table_lines) and is_table_row(table_lines[idx]):
        parts = split_md_row(table_lines[idx])

        # pad/truncate to expected columns
        if len(parts) < expected_cols:
            parts = parts + [""] * (expected_cols - len(parts))
        elif len(parts) > expected_cols:
            parts = parts[:expected_cols]

        for k, label in enumerate(curve_labels):
            a = parts[2*k].strip()
            b = parts[2*k + 1].strip()
            if a or b:  # keep rows that have at least one value
                curves_data[label].append((a, b))
        idx += 1

    return col_names, curve_labels, curves_data

def transform_file(input_path, output_path):
    """Read a Markdown file, split multi-curve tables into single-curve blocks, and write the result.

    Args:
        input_path: Path to the input Markdown file containing multi-curve tables.
        output_path: Path where the corrected Markdown with single-curve tables is written.
    """
    lines = Path(input_path).read_text(encoding="utf-8").splitlines()
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # Copy anything that isn't a DATA TABLE title
        if not looks_like_data_table_title(line):
            out.append(line)
            i += 1
            continue

        # This is a DATA TABLE title. Copy it through.
        title_line = line
        out.append(title_line)
        i += 1

        # Optional bracket header line right after
        bracket_line = None
        if i < n and looks_like_bracket_header(lines[i]):
            bracket_line = lines[i]
            out.append(bracket_line)
            i += 1

        # If the next non-empty line is a table row that contains CURVE labels → multi-curve
        # Otherwise, just continue copying as-is.
        j = i
        # skip blank lines but preserve them later if not transforming
        skipped_blank = []
        while j < n and not lines[j].strip():
            skipped_blank.append(lines[j])
            j += 1

        if j < n and is_table_row(lines[j]) and "CURVE" in lines[j].upper():
            # Collect the contiguous table block starting at j
            tbl_start = j
            tbl_lines = []
            while j < n and is_table_row(lines[j]):
                tbl_lines.append(lines[j])
                j += 1

            parsed = parse_multicurve_table_block(tbl_lines)
            if not parsed:
                # Not a proper multi-curve block; dump originals
                out.extend(skipped_blank)
                out.extend(tbl_lines)
                i = j
                continue

            col_names, curve_labels, curves_data = parsed

            # Emit per-curve breakdown (title & bracket already written once)
            for label in curve_labels:
                out.append(f"")
                out.append(f"**{label}**")
                out.append(f"| {col_names[0]} | {col_names[1]} |")
                out.append("| :--- | :--- |")
                for a, b in curves_data[label]:
                    if a or b:
                        out.append(f"| {a} | {b} |")

            # Advance past the table block; do NOT re-emit original table or skipped blanks
            i = j
        else:
            # Not a multi-curve table; restore any skipped blanks and continue
            out.extend(skipped_blank)
            # (do not consume further; loop will append whatever is next)
            # nothing special to do
            continue

    Path(output_path).write_text("\n".join(out) + "\n", encoding="utf-8")


# Example usage:
# transform_file("big_input.md", "big_output.md")


# Example usage:
main_input_path = './20250531_touloukian_ceramics-main/20250531_touloukian_ceramics-main/'
glasses = "09_1597_1725_glasses/09_ceramicos.md"
input_data_file = main_input_path + glasses  # Path to your data file
output_data_file = main_input_path + "09_1597_1725_glasses/09_ceramicos-corrected.md"

transform_file(input_data_file, output_data_file)
