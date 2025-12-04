# Lane Lexicon to StarDict Converter

This directory contains a Python script to convert Lane Arabic-English Lexicon XML files to StarDict format.

## Requirements

- Python 3.6+
- `pyglossary` (Python package)
- `dictfmt` (from dictd package)
- `dictzip` (from dictd package)
- `tabfile` binary (included in deps.zip)
- GTK2 libraries (for tabfile)

### Installing Dependencies on Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get install dictd dictfmt dictzip libgtk2.0-0

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Extract dependencies
unzip ../../deps.zip -d ../..

# Run the conversion
python3 convert_to_stardict.py \
  --source-dir ../source-lane \
  --output-dir ./output \
  --tabfile ../../deps/tabfile
```

### Command Line Options

- `--source-dir`: Directory containing source XML files (default: ../source-lane)
- `--output-dir`: Directory for output files (default: current directory)
- `--tabfile`: Path to tabfile executable
- `--no-clean`: Do not clean up temporary files

## Output

The script generates three StarDict dictionary files:
- `lane-lexicon.dict.dz` - Compressed dictionary data
- `lane-lexicon.idx` - Index file
- `lane-lexicon.ifo` - Dictionary information file

## Testing

Run the test suite with:

```bash
python3 -m unittest test_convert_to_stardict -v
```

## GitHub Actions

A GitHub Actions workflow is configured to automatically run this conversion when:
- Source XML files in `Lane-Arabic-English-Lexicon/source-lane/` are modified
- The conversion script itself is modified
- The workflow file is modified
- Manually triggered via workflow_dispatch

The workflow will:
1. Run the conversion script
2. Create a zip file from the output
3. Upload it as a build artifact
4. Update `dist/stardict/StarDict-Lane-Lexicon.zip` in the repository

## Conversion Process

The script performs the following steps:

1. **Merge XML Files**: Combines all XML files from the source directory
2. **First Cleanup**: Removes XML tags and performs text transformations
3. **Convert to dictd**: Uses dictfmt to create dictd format files
4. **Convert to CSV**: Uses pyglossary to convert dictd format to tab-separated format
5. **Second Cleanup**: Applies additional text transformations
6. **Add Colors**: Adds HTML formatting for better display
7. **Convert to StarDict**: Uses tabfile to create final StarDict files

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Original bash script: Copyright 2015 Abu Djuwairiyyah Karim Mohammad Karimou
Python conversion: 2024
