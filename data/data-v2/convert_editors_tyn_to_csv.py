"""Convert editors data from JSON to CSV format."""
import json
import os

import pandas as pd

# Load the JSON file
with open("editors_tyn.json", encoding="utf-8") as file:
    data = json.load(file)

print(f"Loaded {len(data)} records from JSON")

# Flatten the JSON structure for CSV export
flat_data = []
for entry in data:
    flat_data.append(
        {
            "title": entry.get("title", ""),
            "url": entry.get("url", ""),
            "language": entry.get("language", ""),
            "validityFrom": entry.get("validityFrom", ""),
            "validityTo": entry.get("validityTo", ""),
            "content": entry.get("content", ""),  # Full content, not truncated
            "meta_navigation": entry.get("meta", {}).get("navigation", ""),
            "meta_title": entry.get("meta", {}).get("title", ""),
            "meta_description": entry.get("meta", {}).get("description", ""),
            "meta_visibility": entry.get("meta", {}).get("visibility", ""),
        }
    )

# Convert to DataFrame
df = pd.DataFrame(flat_data)

print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}")

# Save to CSV
csv_path = "editors_tyn.csv"
df.to_csv(csv_path, index=False, encoding="utf-8")
print(f"Saved CSV to {csv_path}")

# Save to Excel (XLSX)
excel_path = "editors_tyn.xlsx"
df.to_excel(excel_path, index=False, engine="openpyxl")
print(f"Saved Excel file to {excel_path}")

# Create Excel-friendly version with truncated content
df_excel_friendly = df.copy()
# Truncate content to 500 chars for better Excel viewing
df_excel_friendly["content"] = df_excel_friendly["content"].apply(
    lambda x: (x[:500] + "...") if isinstance(x, str) and len(x) > 500 else x
)
excel_friendly_path = "editors_tyn_excel_friendly.xlsx"
df_excel_friendly.to_excel(excel_friendly_path, index=False, engine="openpyxl")
print(f"Saved Excel-friendly file to {excel_friendly_path}")

# Verify the files were written correctly
csv_size = os.path.getsize(csv_path)
excel_size = os.path.getsize(excel_path)
excel_friendly_size = os.path.getsize(excel_friendly_path)
print(f"CSV file size: {csv_size} bytes")
print(f"Excel file size: {excel_size} bytes")
print(f"Excel-friendly file size: {excel_friendly_size} bytes")

# Show first few rows for verification
print("\nFirst 2 rows:")
for i in range(min(2, len(df))):
    print(f"Row {i + 1}:")
    for col in df.columns:
        value = str(df.iloc[i][col])
        if len(value) > 100:
            value = value[:97] + "..."
        print(f"  {col}: {value}")
    print()
