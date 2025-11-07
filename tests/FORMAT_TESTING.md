# Format Testing Guide

## Testing Different Formats

To test various data formats with Senalign:

### Create Test Files (Python)

```python
import pandas as pd

# Load sample data
df = pd.read_csv('tests/sample_data.csv')

# TSV (Tab-separated)
df.to_csv('tests/sample_data.tsv', sep='\t', index=False)

# JSON
df.to_json('tests/sample_data.json', orient='records', indent=2)

# JSON Lines
df.to_json('tests/sample_data.jsonl', orient='records', lines=True)

# Parquet (requires pyarrow)
df.to_parquet('tests/sample_data.parquet', index=False)

# Feather (requires pyarrow)
df.to_feather('tests/sample_data.feather')

# Pickle
df.to_pickle('tests/sample_data.pkl')

# Excel (requires openpyxl)
df.to_excel('tests/sample_data.xlsx', index=False)

# HDF5 (requires tables)
df.to_hdf('tests/sample_data.h5', key='data', mode='w')
```

### Test via API

```bash
# CSV (already works)
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.csv"

# TSV
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.tsv"

# JSON
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.json"

# JSON Lines
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.jsonl"

# Parquet
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.parquet"

# Feather
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.feather"

# Excel
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.xlsx"

# Pickle
curl -X POST http://localhost:8000/datasets/upload -F "file=@tests/sample_data.pkl"
```

### Test via Frontend

1. Start the application: `./start_fullstack.sh`
2. Open http://localhost:3000
3. Click "Choose File"
4. Try uploading files with different extensions
5. Verify they all load correctly

### Expected Behavior

For all formats:
- ✅ File uploads successfully
- ✅ System detects format automatically
- ✅ Data is loaded into pandas DataFrame
- ✅ Profiling works correctly
- ✅ Analysis completes normally

### Format-Specific Notes

**CSV/TSV/TXT:**
- Auto-detects encoding (UTF-8, Latin-1)
- Auto-detects delimiter for .txt files

**JSON:**
- Tries standard format first
- Falls back to JSON Lines if needed

**Excel:**
- Only first sheet is read
- XLSB is faster for large files

**Parquet/Feather:**
- Requires pyarrow package
- Much faster than CSV for large files

**HDF5:**
- Requires tables package
- Reads first key/table found

**Pickle:**
- ⚠️ Security warning: only use trusted sources
- Can execute arbitrary code

---

## Error Testing

### Unsupported Format
```bash
curl -X POST http://localhost:8000/datasets/upload -F "file=@test.pdf"
```
**Expected**: 400 error with list of supported formats

### Corrupted File
```bash
echo "invalid data" > test.csv
curl -X POST http://localhost:8000/datasets/upload -F "file=@test.csv"
```
**Expected**: 500 error with parsing details

### Empty File
```bash
touch empty.csv
curl -X POST http://localhost:8000/datasets/upload -F "file=@empty.csv"
```
**Expected**: Error about empty dataset

---

## Performance Comparison

Test with 100,000 rows:

| Format | Upload Time | Load Time | File Size |
|--------|------------|-----------|-----------|
| CSV | ~2s | ~1s | 5.2 MB |
| TSV | ~2s | ~1s | 5.2 MB |
| JSON | ~3s | ~2s | 12 MB |
| Parquet | ~0.5s | ~0.2s | 1.8 MB |
| Feather | ~0.3s | ~0.1s | 3.5 MB |
| Excel | ~4s | ~3s | 4.5 MB |

**Recommendation**: Use Parquet for datasets > 10MB

---

## Converting Between Formats

```python
import pandas as pd

# CSV → Parquet
df = pd.read_csv('large_data.csv')
df.to_parquet('large_data.parquet')

# Excel → CSV
df = pd.read_excel('data.xlsx')
df.to_csv('data.csv', index=False)

# JSON → Parquet
df = pd.read_json('data.json')
df.to_parquet('data.parquet')
```

---

## Troubleshooting

### "No module named 'pyarrow'"
```bash
pip install pyarrow
```

### "No module named 'tables'"
```bash
pip install tables
```

### "No module named 'pyreadstat'"
```bash
pip install pyreadstat
```

### CSV encoding issues
```python
# Try different encoding
df = pd.read_csv('file.csv', encoding='latin-1')
df.to_csv('file_utf8.csv', encoding='utf-8', index=False)
```
