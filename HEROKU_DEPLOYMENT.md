# Heroku Deployment Guide for Senalign

Complete guide to deploy Senalign (backend + payment system) to Heroku.

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ [Heroku Account](https://signup.heroku.com/) (free tier works)
- ✅ [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- ✅ [Git](https://git-scm.com/) installed
- ✅ MongoDB Atlas account (free tier) for database
- ✅ Your API keys ready (OpenAI, Exa, Interswitch)

---

## 🚀 Quick Deploy (Automated)

### Option 1: Using Deploy Script (Recommended)

```bash
# Make script executable (if not already)
chmod +x deploy_heroku.sh

# Deploy with auto-generated app name
./deploy_heroku.sh

# OR deploy with custom app name
./deploy_heroku.sh --app senalign-prod

# Deploy and show logs
./deploy_heroku.sh --logs
```

The script will:
1. ✅ Check prerequisites (Heroku CLI, login status)
2. ✅ Initialize git if needed
3. ✅ Create Heroku app
4. ✅ Add MongoDB Atlas add-on
5. ✅ Set environment variables from .env
6. ✅ Deploy application
7. ✅ Scale web dyno
8. ✅ Open app in browser

---

## 📖 Manual Deploy (Step-by-Step)

If you prefer to deploy manually or the script fails:

### Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Heroku App

```bash
# Create app with auto-generated name
heroku create

# OR create with custom name
heroku create senalign-prod
```

**Save your app name** - you'll need it for the next steps.

### Step 4: Add MongoDB Atlas Add-on

**Option A: Via Heroku Dashboard**
1. Go to https://elements.heroku.com/addons/mongolab
2. Click "Install MongoDB Atlas"
3. Select your app and plan (Free tier available)

**Option B: Via CLI**

```bash
# Try MongoDB Atlas (free tier)
heroku addons:create mongodb-atlas:free -a YOUR_APP_NAME

# OR try mLab (if available)
heroku addons:create mongolab:sandbox -a YOUR_APP_NAME
```

**Option C: Use External MongoDB Atlas**

1. Go to https://cloud.mongodb.com/
2. Create free cluster
3. Get connection string
4. Set as config var:

```bash
heroku config:set MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/senalign" -a YOUR_APP_NAME
```

### Step 5: Set Environment Variables

```bash
# Required API Keys
heroku config:set OPENAI_API_KEY="sk-..." -a YOUR_APP_NAME
heroku config:set EXA_API_KEY="your_exa_key" -a YOUR_APP_NAME

# Interswitch Payment (Production Credentials)
heroku config:set INTERSWITCH_CLIENT_ID="your_client_id" -a YOUR_APP_NAME
heroku config:set INTERSWITCH_SECRET_KEY="your_secret_key" -a YOUR_APP_NAME
heroku config:set INTERSWITCH_MERCHANT_CODE="your_merchant_code" -a YOUR_APP_NAME
heroku config:set INTERSWITCH_PAY_ITEM_ID="your_pay_item_id" -a YOUR_APP_NAME
heroku config:set INTERSWITCH_MODE="LIVE" -a YOUR_APP_NAME

# Optional: Payment Configuration
heroku config:set FREE_TOKENS_FOR_NEW_USERS="100" -a YOUR_APP_NAME
heroku config:set PAYMENT_CALLBACK_URL="https://YOUR_APP_NAME.herokuapp.com/payment/callback" -a YOUR_APP_NAME

# Production Environment
heroku config:set PYTHON_ENV="production" -a YOUR_APP_NAME
```

**Verify configuration:**
```bash
heroku config -a YOUR_APP_NAME
```

### Step 6: Deploy Application

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial deployment to Heroku"

# Add Heroku remote
heroku git:remote -a YOUR_APP_NAME

# Deploy to Heroku
git push heroku main

# If you're on master branch:
git push heroku master

# If you're on a different branch:
git push heroku your-branch:main
```

### Step 7: Scale Dynos

```bash
# Ensure at least 1 web dyno is running
heroku ps:scale web=1 -a YOUR_APP_NAME

# Check status
heroku ps -a YOUR_APP_NAME
```

### Step 8: Check Logs

```bash
# View real-time logs
heroku logs --tail -a YOUR_APP_NAME

# View recent logs
heroku logs -n 200 -a YOUR_APP_NAME
```

### Step 9: Open Your App

```bash
heroku open -a YOUR_APP_NAME
```

Your app should be live at: `https://YOUR_APP_NAME.herokuapp.com`

---

## 🗄️ Database Setup

### MongoDB Atlas Configuration

1. **Create Database User**:
   - Go to Database Access
   - Add Database User
   - Username: `senalign`
   - Password: (generate secure password)
   - Database User Privileges: `readWrite`

2. **Whitelist IP Addresses**:
   - Go to Network Access
   - Add IP Address
   - Allow Access from Anywhere: `0.0.0.0/0` (required for Heroku)

3. **Get Connection String**:
   - Go to Database → Connect
   - Choose "Connect your application"
   - Copy connection string
   - Replace `<password>` with your actual password

4. **Set in Heroku**:
   ```bash
   heroku config:set MONGODB_URI="your_connection_string" -a YOUR_APP_NAME
   ```

---

## 🎨 Frontend Deployment

The backend is now deployed, but you also need to deploy the frontend.

### Option 1: Deploy Frontend to Vercel (Recommended)

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable
vercel env add VITE_API_URL
# Enter: https://YOUR_APP_NAME.herokuapp.com

# Deploy to production
vercel --prod
```

### Option 2: Deploy Frontend to Netlify

```bash
cd frontend

# Build frontend
npm run build

# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy

# Set environment variable in Netlify dashboard:
# VITE_API_URL = https://YOUR_APP_NAME.herokuapp.com

# Deploy to production
netlify deploy --prod
```

### Option 3: Serve Frontend from Heroku (Same App)

Add to your Heroku app to serve both backend and frontend:

```bash
# Build frontend
cd frontend
npm install
npm run build

# Copy build to backend
cp -r dist ../static

# Update main.py to serve static files
# (See "Serving Frontend from Backend" section below)

# Deploy
git add .
git commit -m "Add frontend build"
git push heroku main
```

---

## 🔧 Configuration Files

Your project should have these files for Heroku deployment:

### `Procfile`
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### `runtime.txt`
```
python-3.10.12
```

### `requirements.txt`
Already exists - contains all Python dependencies

### `Dockerfile` (for container deployment)
Already created - can use for Heroku Container Registry

### `.slugignore`
Already created - excludes unnecessary files from deployment

---

## 🧪 Testing Your Deployment

### 1. Test Health Endpoint

```bash
curl https://YOUR_APP_NAME.herokuapp.com/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "senalign"
}
```

### 2. Test API Documentation

Visit: `https://YOUR_APP_NAME.herokuapp.com/docs`

You should see the FastAPI Swagger UI.

### 3. Test Token Balance

```bash
curl https://YOUR_APP_NAME.herokuapp.com/api/v1/payment/balance/test@example.com
```

**Expected Response**:
```json
{
  "user_email": "test@example.com",
  "token_balance": 100,
  "total_purchased": 100,
  "total_consumed": 0,
  ...
}
```

### 4. Test Payment Pricing

```bash
curl https://YOUR_APP_NAME.herokuapp.com/api/v1/payment/pricing
```

---

## 🔄 Updating Your Deployment

### Deploy New Changes

```bash
# Make changes to your code
git add .
git commit -m "Your commit message"

# Push to Heroku
git push heroku main

# Check logs
heroku logs --tail -a YOUR_APP_NAME
```

### Update Environment Variables

```bash
# Update a variable
heroku config:set VARIABLE_NAME="new_value" -a YOUR_APP_NAME

# Remove a variable
heroku config:unset VARIABLE_NAME -a YOUR_APP_NAME

# View all variables
heroku config -a YOUR_APP_NAME
```

### Restart Application

```bash
heroku restart -a YOUR_APP_NAME
```

---

## 🐛 Troubleshooting

### Issue: Application Crashed (H10 Error)

**Check logs**:
```bash
heroku logs --tail -a YOUR_APP_NAME
```

**Common causes**:
- Missing environment variables
- Database connection failed
- Port binding issue (ensure using `$PORT`)

**Fix**:
```bash
# Check if web dyno is running
heroku ps -a YOUR_APP_NAME

# Scale up if needed
heroku ps:scale web=1 -a YOUR_APP_NAME

# Restart
heroku restart -a YOUR_APP_NAME
```

### Issue: MongoDB Connection Failed

**Check connection string**:
```bash
heroku config:get MONGODB_URI -a YOUR_APP_NAME
```

**Verify**:
- Username and password are correct
- IP whitelist includes `0.0.0.0/0`
- Database name is included in URI
- No special characters causing issues (URL encode if needed)

### Issue: "No web processes running"

```bash
# Check Procfile exists
cat Procfile

# Scale web dyno
heroku ps:scale web=1 -a YOUR_APP_NAME

# Check dyno status
heroku ps -a YOUR_APP_NAME
```

### Issue: Import Errors

**Check Python version**:
```bash
heroku run python --version -a YOUR_APP_NAME
```

**Ensure runtime.txt is correct**:
```
python-3.10.12
```

**Check requirements.txt**:
```bash
# Test locally first
pip install -r requirements.txt
```

### Issue: Payment Gateway Not Working

**Verify environment variables**:
```bash
heroku config -a YOUR_APP_NAME | grep INTERSWITCH
```

**Check mode**:
- For production: `INTERSWITCH_MODE=LIVE`
- For testing: `INTERSWITCH_MODE=TEST`

**Test payment endpoint**:
```bash
curl https://YOUR_APP_NAME.herokuapp.com/api/v1/payment/pricing
```

---

## 📊 Monitoring

### View Application Metrics

```bash
# Open Heroku dashboard
heroku dashboard -a YOUR_APP_NAME

# View metrics in CLI
heroku ps -a YOUR_APP_NAME
```

### Set Up Logging Add-on (Optional)

```bash
# Papertrail (free tier available)
heroku addons:create papertrail:choklad -a YOUR_APP_NAME

# View logs
heroku addons:open papertrail -a YOUR_APP_NAME
```

### Monitor Database Usage

```bash
# If using MongoDB Atlas add-on
heroku addons:open mongodb-atlas -a YOUR_APP_NAME
```

---

## 💰 Cost Estimation

### Free Tier (Recommended for Start)

| Resource | Plan | Cost | Limit |
|----------|------|------|-------|
| Web Dyno | Eco | $0 | 1000 hours/month shared |
| MongoDB Atlas | Free | $0 | 512 MB storage |
| **Total** | | **$0/month** | |

**Note**: Heroku's free tier was discontinued. You'll need:
- **Eco Dynos**: $5/month (1000 dyno hours shared across apps)
- OR **Basic Dyno**: $7/month per app

### Production Tier

| Resource | Plan | Cost |
|----------|------|------|
| Web Dyno | Standard-1X | $25/month |
| MongoDB Atlas | M10 | $57/month |
| Papertrail | Choklad | Free |
| **Total** | | **~$82/month** |

---

## 🔒 Security Best Practices

### 1. Secure Environment Variables

```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use Heroku config vars for secrets
heroku config:set SECRET_KEY="..." -a YOUR_APP_NAME
```

### 2. Enable HTTPS (Automatic on Heroku)

All Heroku apps automatically get SSL/TLS.

### 3. Set Up Custom Domain (Optional)

```bash
# Add custom domain
heroku domains:add www.yourdomain.com -a YOUR_APP_NAME

# Configure DNS (at your domain provider)
# Add CNAME record:
# www -> YOUR_APP_NAME.herokuapp.com
```

### 4. Enable Automated Certificate Management

```bash
heroku certs:auto:enable -a YOUR_APP_NAME
```

### 5. Set Security Headers

Add to `app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["YOUR_APP_NAME.herokuapp.com", "www.yourdomain.com"]
)
```

---

## 🚀 Advanced: Using Heroku Container Registry

If you want to use Docker instead of buildpacks:

```bash
# Login to Heroku Container Registry
heroku container:login

# Set stack to container
heroku stack:set container -a YOUR_APP_NAME

# Build and push container
heroku container:push web -a YOUR_APP_NAME

# Release the container
heroku container:release web -a YOUR_APP_NAME

# Check status
heroku ps -a YOUR_APP_NAME
```

---

## 📝 Post-Deployment Checklist

After successful deployment:

- [ ] Test health endpoint
- [ ] Test API documentation page
- [ ] Test token balance endpoint
- [ ] Test payment pricing endpoint
- [ ] Try creating a new user (should get 100 free tokens)
- [ ] Try analyzing a dataset
- [ ] Test payment flow with Interswitch test cards
- [ ] Verify MongoDB connection and data persistence
- [ ] Check application logs for errors
- [ ] Set up custom domain (optional)
- [ ] Configure CORS for frontend domain
- [ ] Set up monitoring/alerting
- [ ] Document your app URL and credentials

---

## 🎯 Quick Reference Commands

```bash
# View logs
heroku logs --tail -a YOUR_APP_NAME

# Restart app
heroku restart -a YOUR_APP_NAME

# Check dyno status
heroku ps -a YOUR_APP_NAME

# Scale dynos
heroku ps:scale web=1 -a YOUR_APP_NAME

# Open app
heroku open -a YOUR_APP_NAME

# Open dashboard
heroku dashboard -a YOUR_APP_NAME

# Run Python shell
heroku run python -a YOUR_APP_NAME

# Run bash
heroku run bash -a YOUR_APP_NAME

# View config
heroku config -a YOUR_APP_NAME

# Set config
heroku config:set KEY=value -a YOUR_APP_NAME

# View add-ons
heroku addons -a YOUR_APP_NAME

# Open MongoDB dashboard
heroku addons:open mongodb-atlas -a YOUR_APP_NAME
```

---

## 📚 Additional Resources

### Official Documentation
- [Heroku Python Deployment](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Heroku Environment Variables](https://devcenter.heroku.com/articles/config-vars)
- [MongoDB Atlas with Heroku](https://www.mongodb.com/cloud/atlas/heroku)

### Senalign Documentation
- [Payment Integration Guide](PAYMENT_INTEGRATION.md)
- [Quick Start Guide](PAYMENT_QUICKSTART.md)
- [API Documentation](http://YOUR_APP_URL/docs)

### Support
- Heroku Support: https://help.heroku.com
- MongoDB Atlas Support: https://docs.atlas.mongodb.com
- Interswitch Docs: https://docs.interswitchgroup.com

---

## ✅ Success!

Your Senalign app should now be live on Heroku! 🎉

**Next Steps**:
1. Deploy frontend to Vercel/Netlify
2. Configure frontend to use your Heroku backend URL
3. Test end-to-end payment flow
4. Share your app with users

**Your URLs**:
- Backend API: `https://YOUR_APP_NAME.herokuapp.com`
- API Docs: `https://YOUR_APP_NAME.herokuapp.com/docs`
- Health Check: `https://YOUR_APP_NAME.herokuapp.com/health`

---

**Happy Deploying! 🚀**