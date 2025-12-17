# ekhi-utils

This repository holds some examples of how to work with the JSON files downloaded from [EKHI](https://thermomat.ehu.eus/ekhi). Those examples can be found in the `notebooks` folder.

## The JSON Schema

The JSON schema in `schemas/ekhi-dataset.json` defines the JSON structure for EKHI dataset files. 

### Structure

- **publication_info** - bibliographic metadata.
- **id** - identifier of the data record.
- **material** - string of the material name.
- **property** - array of strings with properties and subproperties ordered hierarchically.
- **category** - array of strings with categories and subcategories ordered hierarchically.
- **reported_measurements** - array of the reported Measurements.

Each object in `reported_measurements` conforms to the Measurement structure defined in the
[FER schema](https://github.com/jongablop/fer/blob/main/fer-schema.json).

### Validation

To validate an EKHI JSON file:

```bash
pip install jsonschema
python -m jsonschema -i data/entry_example.json schemas/ekhi-schema.json
