# ekhi-utils

This repository holds some examples of how to work with the JSON files downloaded from EKHI. Those examples can be found in the `notebooks` folder.

## The JSON Schema

The JSON schema in `schemas/ekhi-dataset.json` defines the JSON structure for EKHI dataset files. 

### Structure

- **publication_info** — bibliographic metadata
- **datasets** — list of materials and associated reported data

Each object in `datasets[*].reported_data[*]` conforms to the
[FER schema](https://github.com/jongablop/fer/blob/main/fer-schema.json).

### Validation

To validate an EKHI JSON file:

```bash
pip install jsonschema
python -m jsonschema -i examples/tungsten.json ekhi-schema.json