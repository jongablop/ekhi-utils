"""
Step 15 — Merge and Normalise JSON Curves
===========================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Normalises curve names (e.g. "CURVE 15*" becomes "15") and merges
    duplicate curves that share the same number. Data lists for each column
    are concatenated. This deduplication step is necessary because multi-page
    tables can produce repeated curve entries.

Input:
    - processed_data/merged_json/table_NNN_*.json — merged table JSONs

Output:
    - processed_data/normalized_curves_json/table_NNN_*.json — deduplicated JSONs

Dependencies:
    - os, json, re, collections
"""
import os
import json
import re
from collections import defaultdict

def normalize_curve_name(name):
    """
    Extracts curve number from names like 'CURVE 15*', 'CURVE 15 (continued)', '15*', etc.
    Returns a string like '15'
    """
    match = re.search(r'\bCURVE\s*(\d+)', name.upper())
    if not match:
        match = re.search(r'\b(\d+)', name)
    return match.group(1) if match else name.strip()

def merge_curves(curves):
    """Merge duplicate curves that share the same normalised curve number.

    Args:
        curves: Dict mapping original curve names to dicts of column data lists.

    Returns:
        A dict mapping normalised curve numbers to merged column data.
    """
    merged = defaultdict(lambda: defaultdict(list))

    for original_name, curve_data in curves.items():
        norm_name = normalize_curve_name(original_name)

        for column, values in curve_data.items():
            if isinstance(values, list):
                merged[norm_name][column].extend(values)

    return dict(merged)

def process_json_folder(input_folder, output_folder):
    """Normalise curve names and merge duplicates for all JSON files in a folder.

    Args:
        input_folder: Directory containing merged table JSON files.
        output_folder: Directory where normalised JSON files will be written.
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".json"):
            continue

        input_path = os.path.join(input_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        original_curve_count = len(data.get("curves", {}))
        data["curves"] = merge_curves(data.get("curves", {}))
        final_curve_count = len(data["curves"])

        output_path = os.path.join(output_folder, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"[✓] {filename}: {original_curve_count} → {final_curve_count} curves after merge")

# Example usage
process_json_folder(
    input_folder="./processed_data/merged_json",
    output_folder="./processed_data/normalized_curves_json"
)
