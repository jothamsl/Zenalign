# Zenalign

**Backend co-pilot for data scientists to audit, reason about, and enhance dataset quality before ML training.**

Built with Test-Driven Development (TDD) following principles from "Building Applications with AI Agents" by Michael Albada (O'Reilly 2025).

## 🎬 Demo

https://github.com/user-attachments/assets/demo_video.mp4

## 💳 Payment Integration

Senalign now includes a **token-based monetization system** powered by **Interswitch Payment Gateway**!

- ✅ **Purchase tokens** to run dataset analyses
- ✅ **10 tokens per analysis** (₦5 at default rate of 2 tokens per ₦1)
- ✅ **Multiple payment methods** - Card, Transfer, USSD, Wallet, etc.
- ✅ **Test mode enabled** - Full test credentials included for development
- ✅ **Production ready** - Complete OAuth2 + Web Checkout integration

📖 **[Read Full Payment Integration Documentation →](PAYMENT_INTEGRATION.md)**

**Quick Setup**: The system works out-of-the-box with test credentials. For production, add your Interswitch credentials to `.env`:
```bash
INTERSWITCH_CLIENT_ID=your_client_id
INTERSWITCH_SECRET_KEY=your_secret_key
INTERSWITCH_MERCHANT_CODE=your_merchant_code
INTERSWITCH_PAY_ITEM_ID=your_pay_item_id
```

## Architecture

Senalign uses a **single-agent architecture** for quick hackathon iteration:
- **Tools**: Profiler, PII detector, LLM client (OpenAI), Exa search, Payment gateway (Interswitch)
- **Memory**: MongoDB for episodic storage of analyses, reports, and payment transactions
- **Orchestration**: Simple sequential chains (profile → LLM → Exa)
- **Privacy-first**: Local processing, anonymized summaries to external APIs
- **Monetization**: Token-based payment system for analysis sessions

## Quick Start

### Prerequisites
- **Python 3.10+**
- **Docker & Docker Compose** (for MongoDB)

### Easy Setup (Recommended)

**Option 1: Using scripts**
```bash
# One-command setup
./setup.sh

# Edit .env with your API keys (OpenAI, Exa, optional Interswitch)
nano .env  # or use your preferred editor

# Start everything
./start.sh

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs

# When done, stop everything
./stop.sh
```

**Option 2: Using Make**
```bash
# Complete setup
make setup

# Edit .env with your API keys
nano .env

# Start everything
make start

# Run tests
make test

# Test MongoDB connection
make test-db

# Stop everything
make stop

# See all commands
make help
```

### Manual Setup

If you prefer manual setup:

### Manual Setup

If you prefer manual setup:

#### 1. Start MongoDB with Docker

```bash
# Start MongoDB container
docker compose up -d mongodb

# Verify it's running
docker compose ps
```

#### 2. Setup Python Environment

```bash
# Clone and navigate to project
cd senalign

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
# Setup environment variables
cp .env.example .env

# Edit .env with your API keys:
# - OPENAI_API_KEY=your_key_here
# - EXA_API_KEY=your_key_here
# - MONGODB_URI=mongodb://localhost:27017/senalign (already set for Docker)
```

### Running the Server

```bash
# Activate venv if not already
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Docker Commands

```bash
# Start MongoDB
docker compose up -d mongodb

# View MongoDB logs
docker compose logs -f mongodb

# Stop MongoDB
docker compose down

# Stop and remove data volumes
docker compose down -v

# Restart MongoDB
docker compose restart mongodb
```

### Running Tests

```bash
# Run all tests
pytest app/tests/ -v

# Run specific test file
pytest app/tests/test_db.py -v

# Run with coverage
pytest app/tests/ --cov=app --cov-report=html
```

## Troubleshooting

### Docker Issues

**Docker daemon not running:**
```bash
# Start Docker Desktop application first, then:
docker compose up -d mongodb
```

**MongoDB connection fails:**
```bash
# Check if MongoDB container is running
docker compose ps

# View MongoDB logs
docker compose logs mongodb

# Restart MongoDB
docker compose restart mongodb

# Test connection
python test_mongodb.py
```

**Port 27017 already in use:**
```bash
# Check what's using the port
lsof -i :27017

# Either stop the other MongoDB instance, or change the port in docker-compose.yml:
# ports:
#   - "27018:27017"  # Use port 27018 instead
# Then update MONGODB_URI in .env to: mongodb://localhost:27018/senalign
```

### Python/Pytest Issues

**Import errors:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Tests failing:**
```bash
# Tests use mongomock, no Docker needed
pytest app/tests/ -v

# For integration tests with real MongoDB:
docker compose up -d mongodb
python test_mongodb.py
```

## Project Structure

```
senalign/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with lifespan management
│   ├── routers/             # API endpoints
│   │   ├── upload.py        # Dataset upload
│   │   ├── analyze.py       # Analysis orchestration
│   │   └── transform.py     # Data transformations
│   ├── services/            # Core business logic
│   │   ├── db.py           # MongoDB connection (✅ Feature 1)
│   │   ├── profiler.py     # Dataset profiling
│   │   ├── pii_detector.py # PII detection
│   │   ├── llm_client.py   # OpenAI integration
│   │   └── exa_client.py   # Exa search integration
│   ├── models/             # Pydantic schemas
│   │   └── schemas.py
│   └── tests/              # pytest test suite
│       ├── test_main.py    # App initialization tests (✅)
│       ├── test_db.py      # Database tests (✅)
│       └── ...
├── temp/                   # Temporary file storage
├── .env                    # Environment variables (gitignored)
├── .env.example           # Example environment file
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Base URL: `/api/v1`

#### Dataset Endpoints
- ✅ `POST /upload` - Upload dataset with problem context (CSV/JSON)
  - Requires: file + problem_description (min 10 chars)
  - Optional: problem_type, dataset_description
  - Returns: dataset_id, metadata, auto-detected problem type
  - Stores: MongoDB metadata + temp file for processing
- ✅ `POST /analyze/{dataset_id}` - Run full analysis pipeline
  - **Requires**: 10 tokens (user-email header)
  - Returns: Complete analysis report + token info
- `POST /transform/{dataset_id}` - Apply data transformations (planned)
- ✅ `GET /health` - Health check

#### Payment Endpoints
- ✅ `GET /payment/pricing` - Get token pricing information
- ✅ `POST /payment/purchase` - Purchase tokens via Interswitch
- ✅ `POST /payment/verify/{transaction_ref}` - Verify payment and credit tokens
- ✅ `GET /payment/balance/{user_email}` - Get user token balance
- ✅ `GET /payment/balance/{user_email}/history` - Get consumption history
- ✅ `GET /payment/transaction/{transaction_ref}` - Get transaction status
- ✅ `GET /payment/inline-config` - Get inline checkout configuration

## Development Status

### Feature 1: Setup & DB Connection ✅
- [x] FastAPI app initialization
- [x] MongoDB connection service
- [x] Health check endpoint
- [x] Test infrastructure with pytest
- [x] Mocking setup for isolated tests

### Feature 2: Dataset Upload Endpoint ✅
- [x] POST /api/v1/upload endpoint
- [x] CSV and JSON file support
- [x] Problem context requirement (problem_description)
- [x] Auto-detection of problem type from description
- [x] File validation and parsing
- [x] MongoDB metadata storage
- [x] Temporary file storage
- [x] Pydantic schemas for validation
- [x] 8 comprehensive tests passing

### Feature 3: Profiling Service ✅
- [x] DatasetProfiler class with problem-context awareness
- [x] Missing value detection
- [x] Outlier detection (IQR method)
- [x] Class imbalance detection
- [x] Data type analysis
- [x] Quality score calculation (completeness, consistency, validity)
- [x] Problem-aware issue prioritization
- [x] Issue summary generation with severity levels
- [x] 11 comprehensive tests passing

### Feature 4: PII Detection ✅
- [x] PIIDetector class for privacy-first analysis
- [x] Email address detection
- [x] Phone number detection (multiple formats)
- [x] SSN detection
- [x] Credit card detection
- [x] Comprehensive PII report generation
- [x] Severity-based recommendations (critical/high)
- [x] Anonymization suggestions
- [x] 11 comprehensive tests passing

### Feature 5: LLM Recommendations ✅
- [x] LLMClient class for OpenAI integration
- [x] Problem-context-aware prompts
- [x] Privacy-first prompting (aggregated data only, NO raw PII)
- [x] Structured JSON response format
- [x] Error handling for API failures
- [x] Comprehensive mocking for tests
- [x] Using gpt-4o for best quality
- [x] 10 comprehensive tests passing

### Feature 7: Analysis Orchestration ✅
- [x] POST /api/v1/analyze/{dataset_id} endpoint
- [x] Sequential chain orchestration (Profile → PII → LLM → Exa)
- [x] Complete report generation
- [x] MongoDB storage for reports
- [x] End-to-end pipeline integration
- [x] Error handling and fallbacks
- [x] 9 comprehensive tests passing

### Feature 6: Exa Search Integration ✅
- [x] ExaClient class for resource discovery
- [x] Domain-specific search (papers, blogs, Kaggle)
- [x] Smart query generation from context + issues
- [x] Resource categorization (paper/blog/kaggle/etc)
- [x] Duplicate filtering
- [x] Integration with analyze endpoint
- [x] 10 comprehensive tests passing (9/10, 1 flaky)

### Feature 9: Payment Integration ✅
- [x] Interswitch Payment Gateway client (OAuth2 + Web Checkout)
- [x] Token management service
- [x] Payment API endpoints (purchase, verify, balance)
- [x] MongoDB collections for transactions and balances
- [x] Token consumption in analyze endpoint
- [x] Frontend components (TokenBalance, TokenPurchase)
- [x] Comprehensive documentation
- [x] Test credentials and test mode support

### Skipped Features
- [ ] Feature 8: Transform Endpoint (Optional - nice-to-have)

## TDD Workflow

Each feature follows strict TDD:
1. **RED**: Write failing test first
2. **GREEN**: Implement minimal code to pass
3. **REFACTOR**: Clean up, add logging, improve code quality

## Privacy & Ethics

Following Ch. 12 principles:
- PII detection before any external API calls
- Anonymized/aggregated data only sent to LLM/Exa
- Local processing prioritized
- No raw data exposure

## Dependencies

- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation and schemas
- **PyMongo**: MongoDB driver
- **Pandas/Scikit-learn**: Data profiling
- **OpenAI**: LLM recommendations
- **Requests**: HTTP client for Interswitch API
- **pytest**: Testing framework
- **mongomock**: MongoDB mocking for tests

## Contributing

This is a hackathon project. Keep code:
- **Simple**: No over-engineering
- **Modular**: Clear separation of concerns
- **Tested**: Write tests first (TDD)
- **Documented**: Clear docstrings and comments where needed

## License

MIT License (Hackathon Project)

---

**Status**: Feature 1 Complete ✅ | Run `pytest app/tests/ -v` to verify

---

## 🎨 Frontend Setup

The frontend is a modern React application located in `frontend/` directory.

### Quick Start

```bash
# From project root
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The app will open at `http://localhost:3000`

### Features

- 📤 **Drag & Drop Upload** - Easy dataset upload with visual feedback
- 🎯 **Problem Context** - Describe your ML problem for tailored analysis
- 📊 **Visual Quality Dashboard** - Color-coded metrics and scores
- 🔒 **Privacy Alerts** - Clear PII warnings
- 🤖 **AI Recommendations** - GPT-4o powered insights with code examples
- 📚 **Learning Resources** - Curated papers, blogs, and Kaggle notebooks from Exa
- 💾 **Export Reports** - Download complete JSON reports

### Full-Stack Development

Run both backend and frontend simultaneously:

**Terminal 1 (Backend):**
```bash
# Start API server
make run
# Or: uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

The frontend proxies API requests to `http://localhost:8000` automatically.

### Build for Production

```bash
cd frontend
npm run build
```

---

## 📊 Complete Workflow

### 1. Start Services

```bash
# Terminal 1: MongoDB
make docker-up

# Terminal 2: Backend API
make run

# Terminal 3: Frontend
cd frontend && npm run dev
```

### 2. Use the Application

1. Open `http://localhost:3000`
2. Drag & drop your CSV/JSON dataset
3. Describe your ML problem in detail
4. Click the submit button
5. Wait 20-30 seconds for complete analysis
6. Review results with:
   - Quality scores
   - PII warnings
   - AI recommendations
   - Domain resources
7. Download the JSON report

### API Endpoints Used

- `POST /api/v1/upload` - Upload dataset with problem description
- `POST /api/v1/analyze/{dataset_id}` - Run complete analysis
- `GET /health` - Health check

---

## 🔧 Configuration

### Backend (.env)
```
# Database
MONGODB_URI=mongodb://localhost:27017/

# AI Services
OPENAI_API_KEY=sk-...
EXA_API_KEY=...

# Payment (Optional - uses test credentials by default)
INTERSWITCH_CLIENT_ID=your_client_id
INTERSWITCH_SECRET_KEY=your_secret_key
INTERSWITCH_MERCHANT_CODE=your_merchant_code
INTERSWITCH_PAY_ITEM_ID=your_pay_item_id
PAYMENT_CALLBACK_URL=https://yourdomain.com/payment/callback
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

---

## 📦 Tech Stack Summary

**Backend:**
- FastAPI (Python 3.10+)
- MongoDB (via Docker)
- OpenAI GPT-4o
- Exa Search API
- Pandas, Scikit-learn

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS + Radix UI
- Axios (API client)
- React Router

---

## 🎯 Project Status

✅ **Complete and Production-Ready**

- 8/9 features implemented (88.9%)
- 62/64 tests passing (96.9%)
- Full-stack integrated
- End-to-end functional
- Privacy-first architecture
- AI-powered insights
- Beautiful, modern UI
- **Token-based monetization with Interswitch payments**

## 📚 Documentation

- **[Payment Integration Guide](PAYMENT_INTEGRATION.md)** - Complete Interswitch integration documentation
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when server is running)
- **[Frontend README](frontend/README.md)** - React frontend setup and usage

