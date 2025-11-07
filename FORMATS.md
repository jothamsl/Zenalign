# Supported Data Formats

Senalign supports a wide variety of data formats for maximum flexibility. The system automatically detects the format and loads the data appropriately.

## 📊 Supported Formats

### Delimited Text Files
- **CSV** (`.csv`) - Comma-separated values
  - Auto-detects encoding (UTF-8, Latin-1)
  - Handles different separators (`,` `;`)
- **TSV** (`.tsv`) - Tab-separated values
- **TXT** (`.txt`) - Plain text with auto-detected delimiter
  - Supports: tab, semicolon, pipe, comma

### JSON Files
- **JSON** (`.json`) - Standard JSON format
  - Auto-detects orientation (records, columns, etc.)
- **JSON Lines** (`.jsonl`) - Newline-delimited JSON
  - Each line is a separate JSON object

### Excel Files
- **XLSX** (`.xlsx`) - Excel 2007+ format
- **XLS** (`.xls`) - Excel 97-2003 format
- **XLSB** (`.xlsb`) - Excel binary format (faster for large files)

### High-Performance Formats
- **Parquet** (`.parquet`) - Columnar storage format
  - Excellent for large datasets
  - Preserves data types
- **Feather** (`.feather`) - Fast binary format
  - Optimized for speed
  - Good for temporary storage

### Python Formats
- **Pickle** (`.pkl`, `.pickle`) - Serialized Python objects
  - Preserves all pandas dtypes
  - ⚠️ Only use trusted sources

### Scientific/Statistical Formats
- **HDF5** (`.hdf`, `.h5`) - Hierarchical Data Format
  - Good for large datasets
  - Supports compression
- **Stata** (`.dta`) - Stata statistical software
- **SPSS** (`.sav`) - SPSS statistical software

### Markup Formats
- **XML** (`.xml`) - Extensible Markup Language
- **HTML** (`.html`) - HTML tables
  - Extracts first table from page

---

## 📝 Format Details

### CSV/TSV/TXT
**Best for:** General purpose, human-readable data

**Features:**
- Auto-encoding detection (UTF-8, Latin-1)
- Auto-delimiter detection for `.txt` files
- Handles European CSV (semicolon-separated)

**Example:**
```csv
name,age,email
Alice,25,alice@example.com
Bob,30,bob@test.org
```

### JSON/JSONL
**Best for:** Nested data, API responses

**Standard JSON:**
```json
[
  {"name": "Alice", "age": 25},
  {"name": "Bob", "age": 30}
]
```

**JSON Lines:**
```jsonl
{"name": "Alice", "age": 25}
{"name": "Bob", "age": 30}
```

### Parquet
**Best for:** Large datasets, data warehouses

**Features:**
- Columnar storage (efficient compression)
- Preserves schema and types
- Fast read/write
- Industry standard for big data

**When to use:**
- Datasets > 10MB
- Need to preserve exact dtypes
- Working with Spark, Dask, or cloud storage

### Feather
**Best for:** Fast inter-process communication

**Features:**
- Extremely fast read/write
- Binary format
- Good for temporary files

**When to use:**
- Speed is critical
- Exchanging data between Python/R/Julia

### HDF5
**Best for:** Large scientific datasets

**Features:**
- Compression support
- Hierarchical structure
- Partial reads (doesn't load entire file)

**When to use:**
- Very large datasets (> 1GB)
- Need compression
- Scientific computing

### Stata/SPSS
**Best for:** Statistical software exports

**Features:**
- Preserves variable labels
- Maintains value labels
- Handles missing value codes

**When to use:**
- Exporting from Stata/SPSS
- Working with survey data
- Need to preserve metadata

---

## 🚀 Usage Examples

### Via Frontend
1. Click "Choose File"
2. Select any supported format
3. System auto-detects and loads

### Via API
```bash
# Works with any format
curl -X POST http://localhost:8000/datasets/upload \
  -F "file=@data.parquet"

curl -X POST http://localhost:8000/datasets/upload \
  -F "file=@data.feather"

curl -X POST http://localhost:8000/datasets/upload \
  -F "file=@data.dta"
```

---

## ⚠️ Important Notes

### Security
- **Pickle files**: Only upload from trusted sources (can execute code)
- **HTML/XML**: May require external validation

### Performance
- **Small files (< 10MB)**: CSV, JSON work fine
- **Medium files (10-100MB)**: Use Parquet or Feather
- **Large files (> 100MB)**: Parquet recommended

### Encoding
- CSV/TXT files automatically try UTF-8, then Latin-1
- For other encodings, convert before upload

### Multi-Sheet Excel
- Only first sheet is loaded
- To analyze other sheets, export individually

---

## 🔍 Format Detection

The system uses file extension to determine format:

```python
# Automatic detection
.csv  → pandas.read_csv()
.parquet → pandas.read_parquet()
.xlsx → pandas.read_excel()
.jsonl → pandas.read_json(lines=True)
```

For `.txt` files, delimiter is auto-detected:
1. Reads first line
2. Checks for: tab, semicolon, pipe, comma
3. Uses detected delimiter

---

## 📊 Format Comparison

| Format | Speed | Size | Human Readable | Schema Preservation |
|--------|-------|------|----------------|-------------------|
| CSV | ⭐⭐⭐ | ❌ Large | ✅ Yes | ❌ No |
| JSON | ⭐⭐ | ❌ Large | ✅ Yes | ⭐ Partial |
| Parquet | ⭐⭐⭐⭐⭐ | ✅ Small | ❌ No | ✅ Yes |
| Feather | ⭐⭐⭐⭐⭐ | ⭐ Medium | ❌ No | ✅ Yes |
| Excel | ⭐⭐ | ⭐ Medium | ⭐ Partial | ⭐ Partial |
| HDF5 | ⭐⭐⭐⭐ | ✅ Small | ❌ No | ✅ Yes |
| Pickle | ⭐⭐⭐⭐ | ⭐ Medium | ❌ No | ✅ Yes |

---

## 🛠️ Troubleshooting

### "Unsupported file format"
- Check file extension is in supported list
- Ensure file isn't corrupted

### "Failed to load CSV file: UnicodeDecodeError"
- File encoding issue
- Convert to UTF-8 before upload

### "Failed to load Excel file"
- File may be password-protected
- Try saving as XLSX (not XLS)

### "No tables found in HTML file"
- HTML file doesn't contain `<table>` tags
- Export data as CSV instead

---

## 💡 Best Practices

1. **For sharing data**: Use CSV (most compatible)
2. **For performance**: Use Parquet (fastest)
3. **For preservation**: Use Parquet or HDF5 (keeps types)
4. **For readability**: Use CSV or JSON (human-readable)
5. **For APIs**: Use JSON or JSON Lines

---

## 🔄 Format Conversion

If your data is in an unsupported format, convert it:

**Python:**
```python
import pandas as pd

# Any format → CSV
df = pd.read_excel('data.xlsx')
df.to_csv('data.csv', index=False)

# Any format → Parquet
df = pd.read_csv('data.csv')
df.to_parquet('data.parquet')
```

**Command Line:**
```bash
# Excel → CSV
libreoffice --convert-to csv data.xlsx

# JSON → CSV (with jq)
jq -r '(.[0] | keys_unsorted), (.[] | [.[]]) | @csv' data.json > data.csv
```

---

## 📦 Required Packages

Format support requires these Python packages (already in `requirements.txt`):

- `pyarrow` - Parquet support
- `tables` - HDF5 support  
- `pyreadstat` - SPSS support
- `lxml` - XML support
- `html5lib` - HTML parsing
- `pyxlsb` - Excel binary format
- `openpyxl` - Excel XLSX support

---

**Need a format not listed?** Open an issue and we'll consider adding it!
