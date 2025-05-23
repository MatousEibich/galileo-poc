# Data Conversion Scripts

This folder contains scripts to convert JSON data files into more accessible CSV and Excel formats.

## Available Scripts

### 1. `convert_editors_tyn_to_csv.py`
Converts website content data from `editors_tyn.json` to CSV and Excel formats.

### 2. `convert_messages_tyn_to_csv.py`
Converts news and notices data from `messages_tyn.json` to CSV and Excel formats.

### 3. `convert_official_boards_tyn_to_csv.py`
Converts official noticeboard data from `official_boards_tyn.json` to CSV and Excel formats.

## Usage

Run any script from the data-v2 directory with Python:

```bash
python convert_editors_tyn_to_csv.py
```

## Output Files

Each script produces three output files:

1. **Full CSV** (e.g., `editors_tyn.csv`)
   - Complete dataset with all content intact
   - Best for data processing and analysis

2. **Full Excel** (e.g., `editors_tyn.xlsx`)
   - Complete dataset in Excel format
   - Preserves all data including lengthy content fields

3. **Excel-friendly** (e.g., `editors_tyn_excel_friendly.xlsx`)
   - Content fields truncated to 500 characters for better viewing
   - Optimized for browsing and visual inspection in Excel

## Requirements

- Python 3.x
- pandas
- openpyxl

To install requirements:

```bash
python -m pip install pandas openpyxl
``` 