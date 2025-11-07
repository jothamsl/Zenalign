# Senalign Dataset Quality Validator

A FastAPI backend + React frontend for dataset quality validation with LLM-powered analysis using OpenAI GPT-5.

## Features (Incremental Implementation)

### ✅ Feature 1: File Upload + Profiling + PII Detection + GPT-5 Analysis
- **Upload 15+ data formats**: CSV, TSV, JSON, Excel, Parquet, Feather, HDF5, Stata, SPSS, XML, HTML, and more ([see all formats](FORMATS.md))
- **Natural language problem description** (no dropdowns!)
- Automatic data profiling (types, missing data, statistics)
- PII detection (emails, phones, SSNs, etc.)
- **GPT-5-powered contextual analysis** tailored to your specific ML problem
- React frontend for easy testing

**Key Innovation**: Users describe their ML problem in plain English, and GPT-5 understands the context to provide tailored recommendations, suggest appropriate ML approaches, and identify relevant features.

### 🔜 Feature 2: Exa Integration (Not Yet Implemented)
### 🔜 Feature 3: External Augmentation (Not Yet Implemented)
### 🔜 Feature 4: PDF Export (Not Yet Implemented)
### 🔜 Feature 5: Task Queue (Not Yet Implemented)

---

## Requirements

### Required Environment Variables

```bash
# REQUIRED for Feature 1
export OPENAI_API_KEY=your_openai_key_here

# Required for app (can use default for dev)
export SECRET_KEY=your_secret_key_here
```

### Optional Environment Variables (for future features)

```bash
export EXA_API_KEY=your_exa_key_here              # Feature 2
export KAGGLE_USERNAME=your_username              # Feature 3
export KAGGLE_KEY=your_kaggle_key                 # Feature 3
```

---

## Quick Start (Full Stack)

### Option 1: Start Backend + Frontend Together

```bash
# Set environment variable
export OPENAI_API_KEY=your_openai_key_here

# Install Python dependencies
pip install -r requirements.txt

# Run both servers
./start_fullstack.sh
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Option 2: Start Backend Only

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_openai_key_here
export SECRET_KEY=dev-secret-key

# Run the server
python -m uvicorn app.main:app --reload --port 8000
```

### Option 3: Backend + Frontend Separately

**Terminal 1 (Backend):**
```bash
export OPENAI_API_KEY=your_openai_key_here
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install
npm run dev
```

---

## Using the React Frontend

The easiest way to test Feature 1 is with the included React frontend:

1. Start both servers using `./start_fullstack.sh`
2. Open http://localhost:3000 in your browser
3. Upload a dataset (try `tests/sample_data.csv`)
4. **Describe your ML problem** in natural language (e.g., "I want to predict customer churn...")
5. Click "Analyze with GPT-5" and view results

The UI shows:
- ✅ Dataset upload and validation
- ✅ **Natural language problem description input**
- ✅ Real-time analysis status
- ✅ Quality score with visual indicator
- ✅ **GPT-5's understanding of your problem**
- ✅ **Recommended ML approaches** tailored to your use case
- ✅ **Feature engineering suggestions** specific to your problem
- ✅ PII detection highlights
- ✅ AI-powered recommendations
- ✅ Column-by-column statistics
- ✅ Raw JSON output

---

## Feature 1: Usage Guide

### Supported Data Formats

Senalign supports **15+ data formats**:
- **Delimited**: CSV, TSV, TXT
- **JSON**: JSON, JSON Lines
- **Excel**: XLSX, XLS, XLSB
- **High-Performance**: Parquet, Feather
- **Scientific**: HDF5, Stata (.dta), SPSS (.sav)
- **Markup**: XML, HTML

See [FORMATS.md](FORMATS.md) for detailed format documentation.

---

### 1. Upload a Dataset

```bash
curl -X POST "http://localhost:8000/datasets/upload" \
  -F "file=@tests/sample_data.csv" \
  -H "accept: application/json"
```

**Response:**
```json
{
  "dataset_id": "ds_a1b2c3d4e5f6",
  "filename": "sample_data.csv",
  "rows": 10,
  "columns": 6,
  "size_bytes": 512,
  "uploaded_at": "2025-11-07T14:30:00.123456"
}
```

### 2. Start Analysis

```bash
curl -X POST "http://localhost:8000/analysis/start" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "ds_a1b2c3d4e5f6",
    "problem_description": "I want to predict customer churn based on usage patterns and demographics. I need to identify which customers are likely to leave in the next 30 days.",
    "target_column": "score",
    "protected_columns": ["email"]
  }'
```

**Response:**
```json
{
  "job_id": "job_x7y8z9a0b1c2",
  "status": "processing",
  "message": "Analysis started. Poll /analysis/result/{job_id} for results."
}
```

### 3. Get Analysis Result

```bash
curl -X GET "http://localhost:8000/analysis/result/job_x7y8z9a0b1c2"
```

**Response (when completed):**
```json
{
  "job_id": "job_x7y8z9a0b1c2",
  "dataset_id": "ds_a1b2c3d4e5f6",
  "status": "completed",
  "created_at": "2025-11-07T14:30:05.123456",
  "completed_at": "2025-11-07T14:30:10.654321",
  "profile": {
    "dataset_id": "ds_a1b2c3d4e5f6",
    "total_rows": 10,
    "total_columns": 6,
    "quality_score": 82.5,
    "columns": [
      {
        "name": "age",
        "dtype": "int64",
        "missing_count": 0,
        "missing_percent": 0.0,
        "unique_count": 10,
        "numeric_stats": {
          "mean": 29.6,
          "std": 3.2,
          "min": 25,
          "max": 35
        },
        "pii_detected": false,
        "pii_types": []
      },
      {
        "name": "email",
        "dtype": "object",
        "missing_count": 2,
        "missing_percent": 20.0,
        "unique_count": 8,
        "pii_detected": true,
        "pii_types": ["email"]
      }
    ],
    "pii_summary": {
      "pii_detected": true,
      "pii_columns": ["email"],
      "pii_column_count": 1
    }
  },
  "llm_recommendations": {
    "problem_understanding": "The user wants to build a predictive classification model...",
    "recommended_approach": "Binary classification using ensemble methods...",
    "overall_quality": "good",
    "quality_issues": [
      "Missing data in email column (20%)",
      "PII detected in email column - requires careful handling"
    ],
    "missing_data_assessment": "Low to moderate missing data...",
    "pii_concerns": "Email addresses present, ensure GDPR compliance...",
    "bias_risks": ["Geographic concentration in US cities"],
    "feature_engineering_suggestions": [
      "Create age groups for better generalization",
      "Engineer interaction features between income and location"
    ],
    "recommendations": [
      "Handle missing emails appropriately",
      "Consider anonymization for email column",
      "Check for class imbalance in target"
    ],
    "suitability_assessment": "Dataset appears suitable for classification with some preprocessing needed...",
    "suggested_preprocessing": [
      "Impute or drop missing email values",
      "Normalize numeric features",
      "One-hot encode city column"
    ],
    "potential_challenges": [
      "Limited sample size may affect model generalization",
      "PII handling requires additional privacy measures"
    ],
    "success_metrics": [
      "F1-score for balanced precision-recall",
      "AUC-ROC for model discrimination",
      "Confusion matrix for error analysis"
    ]
  }
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pii_detector.py -v
pytest tests/test_profiler.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

**Expected Test Output:**
```
tests/test_pii_detector.py::test_detect_email_in_values PASSED
tests/test_pii_detector.py::test_detect_phone_in_values PASSED
tests/test_pii_detector.py::test_detect_ssn_in_values PASSED
tests/test_pii_detector.py::test_detect_in_column_name PASSED
tests/test_pii_detector.py::test_detect_combined PASSED
tests/test_pii_detector.py::test_no_pii PASSED
tests/test_profiler.py::test_profile_numeric_column PASSED
tests/test_profiler.py::test_profile_categorical_column PASSED
tests/test_profiler.py::test_profile_pii_column PASSED
tests/test_profiler.py::test_calculate_quality_score PASSED
tests/test_profiler.py::test_profile_dataset PASSED
tests/test_profiler.py::test_empty_dataframe PASSED
```

---

## API Documentation

Once running, visit:
- **Interactive docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Project Structure

```
app/                      # Backend (FastAPI)
  main.py                 # FastAPI app entry point
  config.py               # Configuration and env validation
  routers/
    datasets.py           # Dataset upload endpoints
    analysis.py           # Analysis endpoints
  services/
    ingestion.py          # File ingestion logic
    profiler.py           # Dataset profiling
    llm_client.py         # OpenAI integration
  models/
    schemas.py            # Pydantic models
  utils/
    fileutils.py          # File handling utilities
    pii_detector.py       # PII detection logic

frontend/                 # Frontend (React + Vite)
  src/
    App.jsx               # Main React component
    App.css               # Styles
    main.jsx              # React entry point
  index.html              # HTML template
  vite.config.js          # Vite configuration
  package.json            # Node dependencies

tests/
  test_profiler.py        # Profiler tests
  test_pii_detector.py    # PII detector tests
  sample_data.csv         # Test fixture

data/                     # Uploaded datasets stored here
start.sh                  # Backend quick start
start_fullstack.sh        # Full stack quick start
```

---

## LLM Analysis Schema

GPT-5 analyzes your dataset in the context of your problem and returns a structured JSON report:

```json
{
  "problem_understanding": "AI's interpretation of your ML problem",
  "recommended_approach": "Specific ML approach(es) recommended",
  "overall_quality": "excellent|good|fair|poor",
  "quality_issues": ["array of specific issues"],
  "missing_data_assessment": "detailed assessment",
  "pii_concerns": "PII risks and compliance considerations",
  "bias_risks": ["potential bias sources for your use case"],
  "feature_engineering_suggestions": ["specific ideas for your problem"],
  "recommendations": ["prioritized, actionable recommendations"],
  "suitability_assessment": "how well dataset fits your problem",
  "suggested_preprocessing": ["preprocessing steps for your use case"],
  "potential_challenges": ["challenges specific to your problem"],
  "success_metrics": ["suggested evaluation metrics"]
}
```

---

## Error Handling

### Missing OPENAI_API_KEY

If you attempt to run analysis without the key:

```json
{
  "detail": "ERROR: Missing required environment variable: OPENAI_API_KEY\nACTION: export OPENAI_API_KEY=your_key_here and re-run. No fallback will be used."
}
```

### Dataset Not Found

```json
{
  "detail": "Dataset ds_xyz123 not found"
}
```

### OpenAI API Failure

```json
{
  "status": "failed",
  "error": "ERROR: OpenAI API call failed: <error details>\nACTION: Verify OPENAI_API_KEY is valid and you have API access."
}
```

---

## Design Principles

1. **No Fallback Data**: If external services (OpenAI) are unavailable, the system fails explicitly with clear error messages.

2. **Privacy First**: 
   - PII is detected and flagged
   - Only sanitized aggregates are sent to OpenAI (no raw PII)
   - Sensitive values are redacted in LLM prompts

3. **Async Operations**: 
   - Uses `asyncio.to_thread` for pandas operations
   - Background task processing for analysis

4. **Simple and Modifiable**:
   - Small, focused modules
   - Clear separation of concerns
   - Easy to extend with new features

---

## Next Steps

After validating Feature 1, the following features can be implemented:

- **Feature 2**: Exa integration for external evidence gathering
- **Feature 3**: Kaggle/Google Datasets integration for augmentation
- **Feature 4**: PDF report generation
- **Feature 5**: Celery task queue for production scaling

---

## License

MIT
