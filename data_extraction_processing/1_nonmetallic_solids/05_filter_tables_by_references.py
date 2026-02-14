"""
Step 05 — Filter Tables by References (Basic)
==============================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Filters a Markdown data file to keep only sections whose reference
    numbers appear in the filtered reference CSV. Counts remaining curves.

Input:
    - raw_data/<chapter>/<chapter>_ceramicos.md — Markdown with all tables
    - processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv

Output:
    - processed_data/<chapter>_ceramicos-filtered.md — filtered Markdown

Dependencies:
    - re
"""
import re

import re

def load_reference_ids(reference_file):
    """
    Load valid reference numbers from a CSV file.
    """
    valid_refs = set()
    with open(reference_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("Reference"):
                parts = line.split(",")
                if parts and parts[0].isdigit():
                    valid_refs.add(int(parts[0]))
    return valid_refs


def filter_data_file(input_file, output_file, valid_refs):
    """
    Filter the input data file and write only sections with valid references.
    Also counts the number of curves in the filtered data.
    """
    keep_section = False
    current_section = []
    filtered_lines = []
    total_curves = 0

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        # Detect start of a new section
        if line.startswith("# ") or line.startswith("### "):
            if current_section:
                if keep_section:
                    filtered_lines.extend(current_section)
                current_section = []
                keep_section = False

        current_section.append(line)

        # Look for Ref. No. values in tables
        ref_matches = re.findall(r"\|\s*\d+\s*\|\s*(\d+)\s*\|", line)
        for ref in ref_matches:
            if int(ref) in valid_refs:
                keep_section = True
                total_curves += 1  # Count each valid curve

    # Add the last section if needed
    if current_section and keep_section:
        filtered_lines.extend(current_section)

    # Write to output file
    with open(output_file, "w", encoding="utf-8") as f:
        # Optionally write the count at the top
        f.write(f"<!-- Total Curves: {total_curves} -->\n")
        f.writelines(filtered_lines)

    print(f"Filtered data written to {output_file}")
    print(f"✅ Total number of curves remaining: {total_curves}")


if __name__ == "__main__":

    oxides_salts = "04_0655_0759_multiple_oxides_and_salts/04_ceramicos_001_049.md"
    monoxide = "05_0760_1352_monoxide_compounds/"
    intermetallic = "06_1351_1432_intermetallic_compounds/06_ceramics.md"
    non_metal_a = "07_a_1433_1501_non_metal_mixtures_sinteresed_press_powders/07_a_ceramicos.md"
    non_metal_b = "07_b_1502_1526_non_metal_mixtures_press_powders/07_b_ceramics.md"
    miscellaneous = "08_1527_1596_miscellaneous_mixtures/08_ceramicos.md"
    glasses = "09_1597_1725_glasses/09_ceramicos.md"
    minerals = "10_1726_1776_minerals_and_rocks/10_ceramicos.md"
    polymers = "11_1777_1819_polymers/11_ceramicos.md"


    main_input_path = './20250531_touloukian_ceramics-main/20250531_touloukian_ceramics-main/'
    reference_csv = "./processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv"  # Path to your references file
    input_data_file = main_input_path + glasses  # Path to your data file
    output_filtered_file = "./processed_data/11_ceramicos-filtered.md"  # Where to save the filtered content

    refs = load_reference_ids(reference_csv)
    filter_data_file(input_data_file, output_filtered_file, refs)

    print(f"Filtered data written to {output_filtered_file}")
