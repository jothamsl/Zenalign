# Frontend Testing Guide

## Feature 1 - Complete Testing Workflow

### Prerequisites
```bash
# 1. Set environment variable
export OPENAI_API_KEY=your_openai_key_here

# 2. Start full stack
./start_fullstack.sh
```

### Test Scenarios

#### Scenario 1: Happy Path - Complete Analysis
1. **Open Frontend**: Navigate to http://localhost:3000
2. **Check Health**: Look for green "✓ Healthy" badge in header
3. **Upload Dataset**:
   - Click "Choose File"
   - Select `tests/sample_data.csv`
   - Click "Upload Dataset"
   - ✅ Should see success message with dataset_id
   - ✅ Should see dataset info (10 rows, 6 columns)
4. **Describe Problem**:
   - In the text area, write: "I want to predict customer scores based on their age, income, and location. This is for a marketing campaign targeting high-value customers."
   - Target Column: `score`
   - Protected Columns: `email`
   - Click "Analyze with GPT-4o"
5. **Wait for Results**:
   - ✅ Should see "GPT-4o is analyzing your dataset..."
   - ✅ After ~10-30 seconds, results appear
6. **Verify Results Display**:
   - ✅ Quality score circle (0-100)
   - ✅ **Problem Understanding**: GPT-4o's interpretation of your description
   - ✅ **Recommended Approach**: Specific ML methods suggested
   - ✅ **Feature Engineering Suggestions**: Ideas tailored to your problem
   - ✅ **Suitability Assessment**: How well the data fits your use case
   - ✅ Dataset overview stats
   - ✅ AI Analysis section with recommendations
   - ✅ Column details with PII highlighting
   - ✅ Raw JSON at bottom

#### Scenario 2: Missing API Key
1. Stop servers
2. Unset OPENAI_API_KEY: `unset OPENAI_API_KEY`
3. Start backend: `python -m uvicorn app.main:app --port 8000`
4. Start frontend: `cd frontend && npm run dev`
5. **Expected**:
   - ⚠️ Yellow warning banner: "OPENAI_API_KEY not configured"
   - Upload works fine
   - Analysis start fails with explicit error message
   - ❌ No fallback data shown

#### Scenario 3: Invalid File Type
1. Try uploading a `.txt` or `.pdf` file
2. **Expected**:
   - ❌ Error message: "Unsupported file format"

#### Scenario 4: Large File
1. Try uploading a file > 100MB
2. **Expected**:
   - ❌ Error message: "File too large. Max size: 100MB"

#### Scenario 5: Dataset Not Found
1. Upload a dataset
2. Note the dataset_id
3. Stop backend
4. Delete the file from `data/` directory
5. Start backend again
6. Try to analyze the deleted dataset
7. **Expected**:
   - ❌ Error message about dataset not found

#### Scenario 6: PII Detection
1. Upload `tests/sample_data.csv` (contains emails)
2. Run analysis
3. **Verify**:
   - ✅ "PII Detected: Yes" in overview
   - ✅ "PII Columns: 1" shown
   - ✅ Email column has red border and "🔒 PII: email" badge
   - ✅ In raw JSON, email top_categories show "[REDACTED]"

#### Scenario 7: Different Problem Descriptions
Test various natural language descriptions:
- "I want to predict house prices based on location and features"
- "I need to detect anomalies in network traffic for security monitoring"
- "I want to cluster customers into segments for personalized marketing"
- "I need to forecast sales for the next quarter based on historical data"
- "I want to classify images of products into categories"

**Expected**: GPT-4o adapts recommendations to each specific problem, suggesting appropriate ML approaches and preprocessing

#### Scenario 8: Multiple Datasets
1. Upload first dataset → Analyze → View results
2. Click "Start Over"
3. Upload second dataset → Analyze → View results
4. **Expected**: Each analysis is independent

#### Scenario 9: Polling Behavior
1. Start analysis
2. Open browser DevTools → Network tab
3. **Observe**:
   - ✅ Polls `/analysis/result/{job_id}` every 2 seconds
   - ✅ Stops polling when status = "completed"
   - ✅ Shows spinner during polling

### Visual Checks

#### Quality Score Color Coding
- 80-100: Green gradient (Excellent)
- 60-79: Blue gradient (Good)
- 40-59: Orange gradient (Fair)
- 0-39: Red gradient (Poor)

#### PII Highlighting
- Columns with PII: Red left border, pink background
- PII badge: Red with lock icon

#### Responsive Layout
- Test on different screen sizes
- Cards should stack properly on mobile

### Browser Console Checks

Open DevTools Console and verify:
- ✅ No JavaScript errors
- ✅ No 404 errors
- ✅ API calls return 200 or expected error codes

### Performance Checks

1. **Upload Speed**: Should be nearly instant for small files
2. **Analysis Time**: 5-15 seconds depending on dataset size
3. **UI Responsiveness**: No lag when clicking buttons
4. **Polling Efficiency**: 2-second intervals, stops when done

### Edge Cases

#### Empty Dataset
Create a CSV with only headers, no data rows
- **Expected**: Quality score = 0, minimal stats

#### Single Column
Create a CSV with only 1 column
- **Expected**: Analysis completes, limited recommendations

#### All Missing Data
Create a CSV with many null values
- **Expected**: Low quality score, warnings about missing data

#### Unicode/Special Characters
Upload dataset with unicode characters (emoji, accents)
- **Expected**: Handles gracefully

---

## Manual API Testing (Without Frontend)

If frontend has issues, test backend directly:

```bash
# Upload
curl -X POST "http://localhost:8000/datasets/upload" \
  -F "file=@tests/sample_data.csv"

# Start analysis (use dataset_id from above)
curl -X POST "http://localhost:8000/analysis/start" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "ds_XXX",
    "problem_type": "classification",
    "target_column": "score"
  }'

# Get result (use job_id from above)
curl "http://localhost:8000/analysis/result/job_XXX"
```

---

## Troubleshooting

### Frontend doesn't load
- Check if running on http://localhost:3000
- Check console for errors
- Verify Vite is running: `npm run dev` should show "Local: http://localhost:3000"

### "Network Error" on upload
- Verify backend is running on port 8000
- Check CORS settings in backend
- Try `curl http://localhost:8000/health` to verify backend

### Analysis never completes
- Check backend logs for errors
- Verify OPENAI_API_KEY is valid
- Check internet connectivity
- Look at Network tab for failed API calls

### PII not detected
- Verify test data actually contains PII patterns
- Check `app/utils/pii_detector.py` regex patterns
- Try data with explicit patterns: "test@email.com", "123-45-6789"

### Styling issues
- Clear browser cache
- Hard refresh (Cmd+Shift+R or Ctrl+Shift+R)
- Check if CSS file loaded in Network tab

---

## Success Criteria

✅ **Feature 1 is working correctly if:**
1. Can upload CSV/JSON/Excel files
2. Upload returns dataset_id and stats
3. Can describe ML problem in natural language (textarea)
4. Analysis uses GPT-4o (not GPT-4o-mini)
5. Polling shows real-time status
6. Results display:
   - Quality score
   - Problem understanding from GPT-4o
   - Recommended ML approach
   - Feature engineering suggestions
   - Suitability assessment
   - Tailored recommendations
   - Column details with PII detection
7. PII is correctly detected and highlighted
8. Missing OPENAI_API_KEY produces clear error (no fallback)
9. All 12 backend tests pass
10. UI is responsive and bug-free
11. Raw JSON is accessible for debugging
12. GPT-4o recommendations are contextual to the user's problem description
