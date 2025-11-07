# 🚀 Senalign Quick Start Guide

## One-Command Start (Recommended)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_key_here

# Install dependencies (first time only)
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Start everything
./start_fullstack.sh
```

Then open: **http://localhost:3000**

---

## What You'll See

### 1. Upload Screen
- Big blue button to choose file
- **Accepts 15+ formats**: CSV, TSV, JSON, Excel, Parquet, Feather, HDF5, Stata, SPSS, XML, HTML
- Shows file size and row/column count

### 2. Problem Description Screen
- **Large text area** to describe your ML problem in natural language
- Examples: "I want to predict customer churn...", "I need to classify images...", etc.
- Optional target column input
- Optional protected columns (comma-separated)
- GPT-5 will understand your problem and tailor recommendations

### 3. Results Screen
- 🎯 **Quality Score**: Big colored circle (0-100)
- 🤖 **GPT-5 Analysis**: 
  - Problem understanding (how AI interpreted your description)
  - Recommended ML approach
  - Feature engineering suggestions
  - Recommendations tailored to your specific problem
- 📊 **Column Details**: Each column with stats and PII detection
- 📄 **Raw JSON**: Complete API response

---

## Quick Test Flow

1. **Upload**: Click file → Select `tests/sample_data.csv` → Upload
2. **Describe**: Write "I want to predict customer scores based on demographics and income"
3. **Analyze**: Click "Analyze with GPT-5" → Wait 10-30 seconds
4. **Review**: See quality score, GPT-5's understanding, tailored recommendations

---

## Common Issues

### ⚠️ "OPENAI_API_KEY not configured"
```bash
export OPENAI_API_KEY=sk-...
# Then restart servers
```

### ❌ "Network Error"
Make sure backend is running:
```bash
curl http://localhost:8000/health
```

### 🐌 Analysis takes forever
- Check internet connection
- Verify API key is valid
- Check backend terminal for errors

---

## File Locations

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Uploaded datasets**: `./data/`
- **Test data**: `./tests/sample_data.csv`

---

## Example curl Commands

```bash
# Upload
curl -X POST http://localhost:8000/datasets/upload -F file=@tests/sample_data.csv

# Analyze (replace ds_XXX with actual dataset_id)
curl -X POST http://localhost:8000/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id":"ds_XXX",
    "problem_description":"I want to predict customer churn based on demographics and usage patterns"
  }'

# Get result (replace job_XXX with actual job_id)
curl http://localhost:8000/analysis/result/job_XXX
```

---

## Next Steps

After testing Feature 1:
1. Verify all functionality works
2. Reply with "approve feature 1"
3. Move on to Feature 2 (Exa integration)

---

## Need Help?

- Check `frontend/TESTING.md` for detailed test scenarios
- Check `README.md` for complete documentation
- Check backend logs for error messages
- Use http://localhost:8000/docs for API documentation
