In order to enhance the reproducibility of the data extraction, curation and structuring process carried out to obtain the initial dataset of EKHI, we have uploaded here the scripts used in that process.

This folder contains the differents pipelines to process the PDF files of the following books:

- Y. S. Touloukian and D. P. DeWitt, *Thermal Radiative Properties: Metallic Elements and Alloys*, Thermophysical Properties of Matter — The TPRC Data Series, Volume 7, IFI/Plenum, New York, 1970.

- Y. S. Touloukian and D. P. DeWitt, *Thermal Radiative Properties: Nonmetallic Solids*, Thermophysical Properties of Matter — The TPRC Data Series, Volume 8, IFI/Plenum, New York, 1972.

- Y. S. Touloukian, D. P. DeWitt, and R. S. Hernicz, *Thermal Radiative Properties: Coatings*, Thermophysical Properties of Matter — The TPRC Data Series, Volume 9, IFI/Plenum, New York, 1972.

You will find the references of the PDF files in the article about EKHI.

The Python libraries used in that process can be found in the `requirements.txt` file inside this folder.

The volumes on nonmetallics solids and on coatings were digitized using a combination of LLMs, due to the poor quality of the scanned PDF files that were used as source documents. Thus, the pipelines corresponding to those volumes only contain the scripts used to curate and structure the data (folders `./1_nonmetallic_solids` and `./2_coatings`). We hope that they will server as a reference for future works.

By contrast, the volumen on metallic elements and alloys was completelly processed using Python, so the folder `./0_metallic_elements_and_alloys` contains the full pipeline that extracts the data from the PDF file, correct some digitizing errors, and generates the structured JSON files that are part of the dataset.