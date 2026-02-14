"""
Step 10 — Rotate Touloukian PDF
================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Rotates every page of the raw Touloukian PDF 90 degrees clockwise so that
    the landscape-scanned pages are upright for downstream OCR processing.

Input:
    - raw_data/touloukian-metals.pdf — original scanned PDF

Output:
    - processed_data/touloukian-metals-rotated-2.pdf — rotated PDF

Dependencies:
    - PyPDF2
"""
from PyPDF2 import PdfReader, PdfWriter

def rotate_pdf_page(input_path, output_path, page_number=0, degrees=90):
    """Rotate every page of a PDF by the given number of degrees clockwise.

    Args:
        input_path: Path to the source PDF file.
        output_path: Path for the rotated output PDF.
        page_number: Unused legacy parameter (all pages are rotated).
        degrees: Clockwise rotation angle in degrees (default 90).
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        #if i == page_number:
        #    page.rotate(degrees)  # clockwise
        page.rotate(degrees)
        writer.add_page(page)

    with open(output_path, 'wb') as f:
        writer.write(f)

    print(f"Saved rotated PDF to {output_path}")

rotate_pdf_page('./raw_data/touloukian-metals.pdf', './processed_data/touloukian-metals-rotated-2.pdf')