"""
Step 06 — Filter Tables by Valid References (Two-Phase)
========================================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Two-phase filter: first keeps specification-table rows whose
    reference numbers appear in the filtered CSV, then keeps data-table
    curve blocks only for (spec table, curve) pairs that survived the
    first phase.

Input:
    - raw_data/<section>/t_coatings_*.md — corrected markdown tables
    - processed_data/Touloukian-coatings_bibliografia-updated-filtered.csv
      — valid reference list from Step 03

Output:
    - processed_data/md_files/<name>_filtered_specs.md — filtered specs
    - processed_data/md_files/<name>_filtered_data.md  — filtered data

Dependencies:
    - re, os
"""
import re
import os


def load_reference_ids(reference_file):
    """
    Load valid reference numbers from a CSV file.
    """
    valid_refs = set()
    with open(reference_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("Reference"):
                parts = line.strip().split(",")
                if parts and parts[0].isdigit():
                    valid_refs.add(int(parts[0]))
    print(f"✅ Loaded {len(valid_refs)} valid reference IDs.")
    return valid_refs


def clean_line(line):
    """
    Remove stray asterisks and filter out annotation lines like '* Not shown on plot'.
    """
    if re.match(r"^\s*\*.*not shown on plot.*$", line, re.IGNORECASE):
        return None
    if re.match(r"^\s*\*.*no plot given.*$", line, re.IGNORECASE):
        return None
    return line.replace("*", "").strip()


def filter_specifications(input_file, spec_output_file, valid_refs):
    """
    Filter SPECIFICATION TABLES: keep headers and rows with valid references.
    Return set of (Spec Table No., Curve No.) pairs for DATA TABLE filtering.
    """
    filtered_specs = []
    valid_curve_pairs = set()
    total_curves = 0

    current_block = []
    current_spec_no = None
    inside_spec_table = False

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        cleaned_line = clean_line(line)
        if cleaned_line is None:
            continue

        # Detect start of a SPECIFICATION TABLE
        spec_match = re.match(
            r"(?:\#{1,6}\s*)?(?:\*\*)?\s*(?:Page\s*\d+:)?\s*SPECIFICATION TABLE NO\.\s*(\d+)",
            cleaned_line,
            re.IGNORECASE
        )
        if spec_match:
            # Write the previous table if it had a header and valid rows
            if current_block and len(current_block) > 1:
                filtered_specs.extend(current_block)
            # Start a new table block
            current_block = [cleaned_line]
            current_spec_no = int(spec_match.group(1))
            inside_spec_table = True
            continue

        # Detect start of a DATA TABLE (end of current SPEC TABLE)
        data_match = re.match(
            r"(?:\#{1,6}\s*)?(?:\*\*)?\s*(?:Page\s*\d+:)?\s*DATA TABLE NO\.\s*(\d+)",
            cleaned_line,
            re.IGNORECASE
        )
        if data_match:
            if current_block and len(current_block) > 1:
                filtered_specs.extend(current_block)
            current_block = []
            inside_spec_table = False
            current_spec_no = None
            continue

        if inside_spec_table and current_spec_no is not None:
            if "|" in cleaned_line:
                # Detect header row: a pipe-delimited row that is NOT a separator line
                if not any(re.match(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$", cleaned_line) for _ in [1]):
                    if len(current_block) == 1:  # First line is table title
                        current_block.append(cleaned_line)  # Save header row
                    else:
                        # Extract curve number (col 1) and ref number (col 2) from data row
                        row_match = re.match(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|", cleaned_line)
                        if row_match:
                            curve_no = int(row_match.group(1))
                            ref_no = int(row_match.group(2))
                            if ref_no in valid_refs:
                                current_block.append(cleaned_line)
                                valid_curve_pairs.add((current_spec_no, curve_no))
                                total_curves += 1
                    continue

                # ✅ Detect separator row (| :--- | ... |) and always keep it
                if re.match(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$", cleaned_line):
                    current_block.append(cleaned_line)
                    continue

                # Non-table line inside SPEC TABLE (keep as-is)
                current_block.append(cleaned_line)



    # Add last SPECIFICATION TABLE if needed
    if current_block and len(current_block) > 1:
        filtered_specs.extend(current_block)

    # Write filtered SPECIFICATION TABLES
    with open(spec_output_file, "w", encoding="utf-8") as f:
        f.write(f"<!-- Total Curves in SPECIFICATION TABLES: {total_curves} -->\n\n")
        f.writelines(line + "\n" for line in filtered_specs)

    print(f"✅ Total curves in spec tables: {total_curves}")
    return valid_curve_pairs


def filter_data_tables(input_file, data_output_file, valid_curve_pairs):
    """
    Filter DATA TABLES for only valid (Spec Table No., Curve No.) pairs.
    Keeps only CURVE blocks from DATA TABLES that match valid pairs.
    """
    current_data_no = None
    current_data_block = []
    current_curve_block = []
    filtered_data = []
    total_data_curves = 0
    keep_data_table = False
    keep_curve = False

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        cleaned_line = clean_line(line)
        if cleaned_line is None:
            continue

        # Detect start of SPECIFICATION TABLE or another block
        if re.match(r"(?:\#{1,6}\s*)?(?:\*\*)?\s*SPECIFICATION TABLE NO\.", cleaned_line, re.IGNORECASE):
            if keep_curve and current_curve_block:
                current_data_block.extend(current_curve_block)
                current_curve_block = []
            if keep_data_table and current_data_block:
                filtered_data.extend(current_data_block)
                current_data_block = []
            current_data_no = None
            keep_data_table = False
            keep_curve = False
            continue

        # 📄 Detect start of a DATA TABLE
        data_match = re.match(
            r"(?:\#{1,6}\s*)?(?:\*\*)?\s*(?:Page\s*\d+:)?\s*DATA TABLE NO\.\s*(\d+)",
            cleaned_line,
            re.IGNORECASE
        )
        if data_match:
            # Flush previous curve and data blocks (same as before)
            if keep_curve and current_curve_block:
                current_data_block.extend(current_curve_block)
                current_curve_block = []
            if keep_data_table and current_data_block:
                filtered_data.extend(current_data_block)
                current_data_block = []

            current_data_no = int(data_match.group(1))
            current_data_block = [cleaned_line]
            keep_data_table = False
            keep_curve = False
            # Set a flag to keep next lines with '[' after this header if needed
            continue

        # 📄 Keep lines containing '[' immediately after DATA TABLE header
        # or simply keep any line containing '[' inside a DATA TABLE block
        if current_data_no is not None and "[" in cleaned_line:
            current_data_block.append(cleaned_line)
            continue


        # Detect start of a CURVE block
        curve_match = re.match(r"(?:\#{1,6}\s*)?CURVE\s+(\d+)", cleaned_line, re.IGNORECASE)
        if curve_match:
            if keep_curve and current_curve_block:
                current_data_block.extend(current_curve_block)
            current_curve_no = int(curve_match.group(1))
            if (current_data_no, current_curve_no) in valid_curve_pairs:
                keep_curve = True
                keep_data_table = True
                total_data_curves += 1
                current_curve_block = [cleaned_line]
            else:
                keep_curve = False
                current_curve_block = []
            continue

        if keep_curve:
            current_curve_block.append(cleaned_line)

    if keep_curve and current_curve_block:
        current_data_block.extend(current_curve_block)
    if keep_data_table and current_data_block:
        filtered_data.extend(current_data_block)

    with open(data_output_file, "w", encoding="utf-8") as f:
        f.write(f"<!-- Total Curves in DATA TABLES: {total_data_curves} -->\n\n")
        f.writelines(line + "\n" for line in filtered_data)

    print(f"✅ Total curves in data tables: {total_data_curves}")


def process_file(input_file, reference_file, output_dir):
    """
    Process a single Markdown file: filter SPECIFICATION and DATA tables.
    """
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    spec_output_file = os.path.join(output_dir, f"{base_name}_filtered_specs.md")
    data_output_file = os.path.join(output_dir, f"{base_name}_filtered_data.md")

    valid_refs = load_reference_ids(reference_file)
    valid_curve_pairs = filter_specifications(input_file, spec_output_file, valid_refs)
    filter_data_tables(input_file, data_output_file, valid_curve_pairs)

if __name__ == "__main__":

    pigmented = "1_Pigmented_Coatings/"
    contact = "2_Contact_Coatings/"
    conversion = "3_Conversion_Coatings/"

    metallic_pigmented = pigmented + "A_Metallic_Pigmented_Coatings/t_coatings_1_A.md"
    nonmetallic_pigmented = pigmented + "B_Nonmetallic_Pigmented_Coatings/t_coatings_1_B-corrected.md"
    enamels_pigmented = pigmented + "C_Enamels_Fused_Vitreous_Porcelain/t_coatings_1_C.md"
    trade_names_pigmented = pigmented + "D_Trade_Names/t_coatings_1_D.md"
    miscellaneous_pigmented = pigmented + "E_Miscellaneous/t_coatings_1_E.md"

    metallic_contact = contact + "A_Metallic_Contact_Coatings/t_coatings_2_a.md"
    nonmetallic_contact = contact + "B_Nonmetallic_Contact_Coatings/t_coatings_2_b.md"
    mirrors_contact = contact + "C_Second_Surface_Mirrors/t_coatings_2_c.md"
    antireflection_contact = contact + "D_Antireflection_Coatings/t_coatings_2_D.md"
    resin_contact = contact + "E_Resin_Coatings/t_coatings_2_E.md"
    black_contact = contact + "F_Metallic_Black_Coatings/t_coatings_2_F.md"

    anodized_conversion = conversion + "A_Anodized_Coatings/t_coatings_3_A.md"
    oxidized_conversion = conversion + "B_Oxidized_Coatings/t_coatings_3_B.md"
    miscellaneous_conversion = conversion + "C_Miscellaneous/t_coatings_3_C.md"


    main_input_path = './raw_data/'
    input_data_file = main_input_path + nonmetallic_pigmented  # Path to your data file
    
    reference_file = "./processed_data/Touloukian-coatings_bibliografia-updated-filtered.csv"
    input_file = input_data_file

    # Extract the base directory and filename (without extension)
    base_dir = os.path.dirname(input_file)  # "10_1726_1776_minerals_and_rocks"
    base_name = os.path.splitext(os.path.basename(input_file))[0]  # "10_ceramicos"
    output_dir = os.path.dirname(".\\processed_data\\md_files\\")

    # Build output filenames
    spec_output_file = os.path.join(output_dir, f"{base_name}_filtered_specs.md")
    data_output_file = os.path.join(output_dir, f"{base_name}_filtered_data.md")

    print(f"Specification Output: {spec_output_file}")
    print(f"Data Output:          {data_output_file}")

    process_file(input_file, reference_file, output_dir)
