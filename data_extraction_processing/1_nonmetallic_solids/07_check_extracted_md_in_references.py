"""
Step 07 — Check Extracted Markdown Against References
=====================================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Validates that every curve in the filtered specification tables has
    a reference number present in the reference CSV. Reports any orphan
    curves whose reference ID is missing.

Input:
    - processed_data/<name>-filtered.md — filtered Markdown
    - processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv

Output:
    - Console output listing invalid curves or confirming all are valid

Dependencies:
    - re
"""
import re

def load_reference_ids(reference_file):
    """Load valid reference numbers from the first column of a CSV file.

    Args:
        reference_file: Path to the reference CSV file.

    Returns:
        Set of integer reference IDs.
    """
    valid_refs = set()
    with open(reference_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("Reference"):
                parts = line.strip().split(",")
                if parts and parts[0].isdigit():
                    valid_refs.add(int(parts[0]))
    return valid_refs

def check_curves_in_refs(md_file, valid_refs):
    """Check that every curve in specification tables has a valid reference number.

    Args:
        md_file: Path to the filtered Markdown file containing specification tables.
        valid_refs: Set of valid reference IDs to check against.
    """
    current_spec_no = None
    inside_spec_table = False
    invalid_curves = []

    with open(md_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Detect start of specification table
            spec_match = re.match(r"SPECIFICATION TABLE NO\.\s*(\d+)", line, re.IGNORECASE)
            if spec_match:
                current_spec_no = int(spec_match.group(1))
                inside_spec_table = True
                continue

            # Detect start of data table or other block ends the spec table
            if re.match(r"DATA TABLE NO\.", line, re.IGNORECASE) or re.match(r"\#{1,6}\s*\*\*?", line):
                inside_spec_table = False
                current_spec_no = None
                continue

            # Process rows inside spec table
            if inside_spec_table and current_spec_no is not None and "|" in line:
                # skip header or separator rows (usually contain text or :---)
                if re.search(r"Curve No\.|:---", line, re.IGNORECASE):
                    continue

                # extract curve no and ref no from table row
                cols = [c.strip() for c in line.strip("|").split("|")]
                if len(cols) >= 2 and cols[0].isdigit() and cols[1].isdigit():
                    curve_no = int(cols[0])
                    ref_no = int(cols[1])
                    if ref_no not in valid_refs:
                        invalid_curves.append((current_spec_no, curve_no, ref_no))

    if invalid_curves:
        print("❌ Curves with Ref. No. NOT found in reference CSV:")
        for spec_no, curve_no, ref_no in invalid_curves:
            print(f" - Spec Table {spec_no}, Curve {curve_no}, Ref. No. {ref_no}")
    else:
        print("✅ All curves in specification tables have valid references.")

if __name__ == "__main__":
    md_file = "./processed_data/09_ceramicos-filtered.md"
    reference_csv = "./processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv"

    valid_refs = load_reference_ids(reference_csv)
    check_curves_in_refs(md_file, valid_refs)
