# Heroku Deployment Quick Start

## 🚀 Deploy in 3 Steps

### Step 1: Prerequisites
```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# OR visit: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login
```

### Step 2: Run Deployment Script
```bash
# Make executable
chmod +x deploy_heroku.sh

# Deploy (auto-generated app name)
./deploy_heroku.sh

# OR with custom name
./deploy_heroku.sh --app senalign-prod
```

### Step 3: Configure Database
```bash
# Option A: Auto-added by script (MongoDB Atlas)
# Option B: Use external MongoDB Atlas
heroku config:set MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/senalign" -a YOUR_APP
```

**Done!** Your app is live at: `https://YOUR_APP.herokuapp.com` 🎉

---

## 📋 Essential Commands

```bash
# View logs
heroku logs --tail -a YOUR_APP

# Restart app
heroku restart -a YOUR_APP

# Check status
heroku ps -a YOUR_APP

# Open app
heroku open -a YOUR_APP

# View config
heroku config -a YOUR_APP

# Update environment variable
heroku config:set KEY=value -a YOUR_APP
```

---

## ⚙️ Environment Variables

```bash
# Required
heroku config:set OPENAI_API_KEY="sk-..." -a YOUR_APP
heroku config:set EXA_API_KEY="your_key" -a YOUR_APP
heroku config:set MONGODB_URI="mongodb+srv://..." -a YOUR_APP

# Payment (Production)
heroku config:set INTERSWITCH_CLIENT_ID="your_id" -a YOUR_APP
heroku config:set INTERSWITCH_SECRET_KEY="your_secret" -a YOUR_APP
heroku config:set INTERSWITCH_MERCHANT_CODE="your_code" -a YOUR_APP
heroku config:set INTERSWITCH_PAY_ITEM_ID="your_id" -a YOUR_APP
heroku config:set INTERSWITCH_MODE="LIVE" -a YOUR_APP

# Optional
heroku config:set FREE_TOKENS_FOR_NEW_USERS="100" -a YOUR_APP
```

---

## 🧪 Test Your Deployment

```bash
# Health check
curl https://YOUR_APP.herokuapp.com/health

# API docs
open https://YOUR_APP.herokuapp.com/docs

# Test token balance
curl https://YOUR_APP.herokuapp.com/api/v1/payment/balance/test@example.com

# Test pricing
curl https://YOUR_APP.herokuapp.com/api/v1/payment/pricing
```

---

## 🐛 Troubleshooting

### App Crashed?
```bash
heroku logs --tail -a YOUR_APP
heroku ps:scale web=1 -a YOUR_APP
heroku restart -a YOUR_APP
```

### Can't Connect to MongoDB?
```bash
# Check URI
heroku config:get MONGODB_URI -a YOUR_APP

# Verify whitelist: 0.0.0.0/0 in MongoDB Atlas
# Network Access → IP Whitelist → Allow from Anywhere
```

### Import Errors?
```bash
# Check Python version
heroku run python --version -a YOUR_APP

# Should be: Python 3.10.12
# If not, check runtime.txt
```

---

## 🎨 Deploy Frontend

### Option 1: Vercel (Recommended)
```bash
cd frontend
npm i -g vercel
vercel

# Set environment
vercel env add VITE_API_URL
# Enter: https://YOUR_APP.herokuapp.com

# Deploy to production
vercel --prod
```

### Option 2: Netlify
```bash
cd frontend
npm run build
npm i -g netlify-cli
netlify deploy --prod

# Set in Netlify dashboard:
# VITE_API_URL = https://YOUR_APP.herokuapp.com
```

---

## 📊 Files Created for Deployment

✅ `Procfile` - Tells Heroku how to run app
✅ `runtime.txt` - Specifies Python version
✅ `Dockerfile` - For container deployment
✅ `.slugignore` - Excludes unnecessary files
✅ `deploy_heroku.sh` - Automated deployment script

---

## 💰 Cost (Heroku)

| Tier | Dyno | Database | Total/Month |
|------|------|----------|-------------|
| **Dev** | Eco ($5) | MongoDB Free | **$5** |
| **Prod** | Basic ($7) | MongoDB M10 ($57) | **$64** |

**Note**: Eco plan gives 1000 dyno hours shared across all apps

---

## 🔄 Update Deployment

```bash
# Make changes
git add .
git commit -m "Update feature"

# Deploy
git push heroku main

# Check logs
heroku logs --tail -a YOUR_APP
```

---

## ✅ Post-Deployment Checklist

- [ ] App accessible at `https://YOUR_APP.herokuapp.com`
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/docs` shows API documentation
- [ ] MongoDB connected (check logs)
- [ ] Environment variables set (run `heroku config`)
- [ ] Frontend deployed and points to backend
- [ ] Test payment flow with test cards
- [ ] New users get 100 free tokens
- [ ] Can run analysis successfully

---

## 📚 Full Documentation

For detailed deployment guide, see: [HEROKU_DEPLOYMENT.md](HEROKU_DEPLOYMENT.md)

---

## 🆘 Need Help?

```bash
# View deployment script help
./deploy_heroku.sh --help

# View logs
heroku logs --tail -a YOUR_APP

# Open dashboard
heroku dashboard -a YOUR_APP

# Run interactive shell
heroku run bash -a YOUR_APP
```

---

## 🎯 Quick Deploy (TL;DR)

```bash
# 1. Login
heroku login

# 2. Deploy
./deploy_heroku.sh --app senalign

# 3. Set MongoDB (if not auto-added)
heroku config:set MONGODB_URI="..." -a senalign

# 4. Set API Keys
heroku config:set OPENAI_API_KEY="..." -a senalign
heroku config:set EXA_API_KEY="..." -a senalign

# 5. Open & Test
heroku open -a senalign
```

**That's it! 🚀**

---

**Your app is now live on Heroku!** 🎉