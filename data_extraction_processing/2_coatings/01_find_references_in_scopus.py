"""
Step 01 — Find References in Scopus
====================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Searches Scopus by quoted title extracted from each citation in a
    markdown reference table, retrieves DOI, abstract, and BibTeX, and
    writes an augmented markdown table with the results.

Input:
    - raw_data/Touloukian-coatings_bibliografia-manually-corrected.md
      — hand-corrected bibliography in markdown-table format

Output:
    - raw_data/Touloukian-coatings_bibliografia-updated.md
      — same table with Num Found, DOI, and bibtex columns appended

Dependencies:
    - re, pybliometrics
"""
import re
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval


def parse_markdown_table(md_text):
    """Extract rows from a markdown table."""
    rows = []
    lines = md_text.strip().split("\n")
    for line in lines:
        if "|" in line and not line.startswith("| ---"):
            parts = [cell.strip() for cell in line.strip().split("|")[1:-1]]
            rows.append(parts)
    return rows


def generate_bibtex(result, abstract=""):
    """Generate a BibTeX entry from Scopus result and add abstract."""
    authors = getattr(result, "author_names", "Unknown Author")
    title = getattr(result, "title", "No Title")
    year = getattr(result, "coverDate", "n.d.").split("-")[0]
    journal = getattr(result, "publicationName", "")
    doi = getattr(result, "doi", "")

    bibtex = f"@article{{{doi or 'no-doi'}," \
             f"  author = {{{authors}}}," \
             f"  title = {{{title}}}," \
             f"  journal = {{{journal}}}," \
             f"  year = {{{year}}},"
    if doi:
        bibtex += f"  doi = {{{doi}}},"
    if abstract:
        # Escape braces in abstract text for BibTeX compatibility
        safe_abstract = abstract.replace("{", "\\{").replace("}", "\\}")
        bibtex += f"  abstract = {{{safe_abstract}}},"
    bibtex += "}"
    return bibtex


def search_scopus_by_title(title):
    """Search Scopus for a given title and fetch DOI, abstract, bibtex, and result count."""
    query = f'TITLE("{title}")'
    search = ScopusSearch(query)
    num_found = search.get_results_size()

    if num_found == 0:
        return {"num_found": 0, "doi": None, "abstract": None, "bibtex": None}

    # Take the first result
    result = search.results[0]
    doi = getattr(result, "doi", None)
    eid = getattr(result, "eid", None)

    abstract = ""
    if eid:
        try:
            abs_retrieval = AbstractRetrieval(eid)
            abstract = abstract = (abs_retrieval.abstract or abs_retrieval.description or "").strip()

        except Exception as e:
            print(f"⚠️ Error retrieving abstract for {eid}: {e}")

    # Generate BibTeX including abstract
    bibtex = generate_bibtex(result, abstract)

    return {
        "num_found": num_found,
        "doi": doi,
        "abstract": abstract,
        "bibtex": bibtex
    }


def process_md_file(input_path, output_path):
    """Read a markdown table, augment it with Scopus data, and write a new table."""
    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    rows = parse_markdown_table(md_text)
    header = ["Reference", "TPRC", "Touloukian ref", "Num Found", "DOI", "bibtex"]
    new_rows = [header]
    total_dois_found = 0

    for ref_no, tprc_no, citation in rows[1:]:
        print(f"🔎 Searching for: {citation}")
        # Extract the quoted title from the full citation string
        title_match = re.search(r'"([^"]+)"', citation)
        title = title_match.group(1) if title_match else None

        if not title:
            print("⚠️ No title found in citation. Skipping...")
            new_rows.append([ref_no, tprc_no, citation, "0", "", ""])
            continue

        if title.endswith(','):
            title = title[:-1]


        scopus_data = search_scopus_by_title(title)
        num_found = str(scopus_data.get("num_found", 0))
        doi = scopus_data.get("doi", "") or ""
        bibtex = scopus_data.get("bibtex", "") or ""

        if doi:
            total_dois_found += 1  # Increment count if DOI is present

        if int(num_found) == 0:
            print(f"❌ No Scopus data found for: {title}")
        else:
            print(f"✅ Found {num_found} results for: {title}")

        new_rows.append([ref_no, tprc_no, citation, num_found, doi, bibtex])

    # Write the new markdown table
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(header) + " |\n")
        f.write("|" + "|".join([" --- "]*len(header)) + "|\n")
        for row in new_rows[1:]:
            f.write("| " + " | ".join(row) + " |\n")

    print(f"\n✅ New table written to {output_path}")
    print(f"📊 Total DOIs found: {total_dois_found} out of {len(rows)-1} references.")


if __name__ == "__main__":
    import pybliometrics
    pybliometrics.init()
    input_md = "raw_data/Touloukian-coatings_bibliografia-manually-corrected.md"     # Your input Markdown file
    output_md = "raw_data/Touloukian-coatings_bibliografia-updated.md"  # Output file
    process_md_file(input_md, output_md)
