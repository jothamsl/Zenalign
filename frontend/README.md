# Frontend for Senalign Dataset Quality Validator

A simple React frontend to test Feature 1 of the Senalign API.

## Features

- ✅ File upload (CSV, JSON, Excel)
- ✅ Analysis configuration
- ✅ Real-time polling for results
- ✅ Quality score visualization
- ✅ PII detection display
- ✅ LLM recommendations display
- ✅ Column-by-column analysis
- ✅ Health check integration

## Installation

```bash
cd frontend
npm install
```

## Running

**Prerequisites:** The backend must be running on `http://localhost:8000`

```bash
# Start backend first (from root directory)
cd ..
python -m uvicorn app.main:app --reload --port 8000

# In another terminal, start frontend
cd frontend
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## Usage

1. **Upload Dataset**: Select a CSV/JSON/Excel file and click upload
2. **Configure Analysis**: Choose problem type, target column, and protected columns
3. **Start Analysis**: Click "Start Analysis" and wait for results
4. **View Results**: See quality score, AI recommendations, and column details

## Development

- Built with React 18 + Vite
- Uses Axios for API calls
- Proxies API requests to backend on port 8000
- Hot module replacement enabled

## Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.

## Troubleshooting

**"Network Error" or API not responding:**
- Make sure backend is running on http://localhost:8000
- Check that OPENAI_API_KEY is set in backend

**"OPENAI_API_KEY not configured" warning:**
- Set the environment variable in your backend terminal
- Restart the backend server

**Analysis stuck on "Analyzing...":**
- Check backend logs for errors
- Verify OpenAI API key is valid
- Check your internet connection
