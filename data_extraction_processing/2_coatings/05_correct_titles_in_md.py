"""
Step 05 — Correct Table Titles in Markdown
===========================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Merges consecutive bold-text lines that should be a single table
    header. Detects lines starting with **DATA TABLE NO.** or
    **SPECIFICATION TABLE NO.** and joins them with the following bold
    line when the title was incorrectly split across two lines.

Input:
    - raw_data/<section>/t_coatings_*.md — raw OCR'd markdown files

Output:
    - raw_data/<section>/t_coatings_*-corrected.md — corrected markdown

Dependencies:
    - os, re
"""
import os
import re

def merge_bold_titles(md_path, output_path=None):
    """Merge consecutive bold-text lines that form a single table title.

    Detects lines starting with **DATA TABLE NO.** or **SPECIFICATION TABLE NO.**
    and joins them with the following bold line when the title was split across
    two lines by OCR.

    Args:
        md_path: Path to the input markdown file.
        output_path: Path for the corrected output file. Defaults to overwriting md_path.
    """
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    merged_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        # Detect bold table headers split across two consecutive lines
        if re.match(r"^\*\*DATA TABLE NO\.\s*\d+", line.strip(), re.IGNORECASE) or re.match(r"^\*\*SPECIFICATION TABLE NO\.\s*\d+", line.strip(), re.IGNORECASE):
            # Look ahead to see if next line is also bold
            if i + 1 < len(lines) and re.match(r"^\*\*.*\*\*$", lines[i+1].strip()):
                # Concatenate the two bold fragments into one line
                merged_line = line.rstrip("**") + " " + lines[i+1].strip("*") + "**"
                merged_lines.append(merged_line)
                i += 2
                continue

        merged_lines.append(line)
        i += 1

    if not output_path:
        output_path = md_path

    with open(output_path, "w", encoding="utf-8") as f:
        for l in merged_lines:
            f.write(l + "\n")

# Example usage
merge_bold_titles(
    "raw_data/1_Pigmented_Coatings/B_Nonmetallic_Pigmented_Coatings/t_coatings_1_B.md",
    "raw_data/1_Pigmented_Coatings/B_Nonmetallic_Pigmented_Coatings/t_coatings_1_B-corrected.md",
)
