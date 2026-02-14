"""
Step 17 — Count CSV Rows
==========================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Diagnostic utility that counts the total number of rows (including and
    excluding the header) in a CSV file and prints the result to the console.

Input:
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv

Output:
    - Console output (row counts)

Dependencies:
    - csv
"""
import csv

filename = "processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv"

with open(filename, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    row_count = sum(1 for row in reader)  # counts all rows including header

print(f"Total rows including header: {row_count}")
print(f"Total data rows excluding header: {row_count - 1}")
