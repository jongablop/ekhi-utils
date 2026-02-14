"""
Step 00 (test) — Unit Test for Multi-Curve Splitter
====================================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Standalone unit test for the multi-curve table splitting logic.
    Uses a hardcoded 6-curve example (DATA TABLE NO. 573) to verify
    that the splitter produces correct per-curve Markdown blocks.

Input:
    - None (hardcoded test data embedded in script)

Output:
    - Console output showing the split result for visual inspection

Dependencies:
    - re
"""
import re

def split_multi_curve_md(title_line, header_line, table_block):
    """
    Splits a multi-curve markdown table into multiple curves,
    showing the title and header only once at the top.
    """
    lines = [l.strip() for l in table_block.strip().split("\n") if l.strip()]
    if len(lines) < 3:
        return table_block  # Not enough content to split

    # First row: curve names
    curve_names = [c.strip() for c in lines[0].split("|") if c.strip()]

    # Data headers (e.g., T, E, T, E, ...)
    column_headers = [h.strip("* ").strip() for h in lines[2].split("|") if h.strip()]

    # Data rows
    data_rows = [ [c.strip() for c in row.split("|") if c.strip() or c == ""] for row in lines[3:] ]

    num_curves = len(curve_names)
    output_lines = [title_line, header_line, ""]

    for curve_index in range(num_curves):
        curve_name = curve_names[curve_index]
        col_start = curve_index * 2
        col_end = col_start + 2
        col_headers = column_headers[col_start:col_end]

        # Build table for this curve
        new_table = [
            f"**{curve_name}**",
            "| " + " | ".join(col_headers) + " |",
            "| " + " | ".join([":---"] * 2) + " |"
        ]

        for row in data_rows:
            if len(row) >= col_end:
                subrow = row[col_start:col_end]
                if any(cell.strip() for cell in subrow):
                    new_table.append("| " + " | ".join(subrow) + " |")

        output_lines.append("\n".join(new_table))
        output_lines.append("")  # Blank line between curves

    return "\n".join(output_lines).strip()


# Example usage
title = "#### **DATA TABLE NO. 573: NORMAL TOTAL EMITTANCE OF ALUMINUM SILICATE GLASS**"
header = "*[Temperature, T, K; Emittance, E]*"
table_md = """
| CURVE 1 | | CURVE 4 | | CURVE 2 | | CURVE 5 | | CURVE 3 | | CURVE 6 | |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T** | **E** | **T** | **E** | **T** | **E** | **T** | **E** | **T** | **E** | **T** | **E** |
| 76.5 | 0.860 | 373 | 0.899 | 391 | 0.883 | 76.5 | 0.857 | 75.9 | 0.853 | 373 | 0.898 |
| 366 | 0.887 | 641 | 0.895 | 637 | 0.887 | 392 | 0.902 | 351 | 0.899 | 647 | 0.898 |
| 534 | 0.896 | 859 | 0.838 | 860 | 0.819 | 531 | 0.901 | 527 | 0.893 | 862 | 0.878 |
| 710 | 0.881 | | | | | 693 | 0.906 | 700 | 0.901 | | |
| 822 | 0.839 | | | | | 923 | 0.872 | 911 | 0.869 | | |
"""

result = split_multi_curve_md(title, header, table_md)
print(result)

