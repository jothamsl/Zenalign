# 🚀 Deploying Senalign to Heroku

This guide will help you deploy Senalign to Heroku with both backend and frontend.

---

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Make sure git is installed
4. **OpenAI API Key**: Get one from [platform.openai.com](https://platform.openai.com)

---

## Quick Deploy (One-Click)

Click this button to deploy directly to Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Then:
1. Enter your app name
2. Set `OPENAI_API_KEY` config var
3. Click "Deploy app"
4. Wait for build to complete (~5 minutes)
5. Click "View" to open your app

---

## Manual Deployment

### Step 1: Prepare Your Repository

```bash
# Clone or navigate to the project
cd /path/to/Senalign

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Heroku deployment"
```

### Step 2: Create Heroku App

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Or let Heroku generate a name
heroku create
```

### Step 3: Set Environment Variables

```bash
# Set required OpenAI API key
heroku config:set OPENAI_API_KEY=your_openai_key_here

# Set secret key (or let Heroku generate one)
heroku config:set SECRET_KEY=$(openssl rand -hex 32)

# Optional: Set other configs
heroku config:set DATA_DIR=/tmp/data
heroku config:set MAX_UPLOAD_SIZE_MB=100
```

### Step 4: Add Buildpacks

Heroku needs both Node.js (for frontend) and Python (for backend):

```bash
# Add Node.js buildpack first (for frontend build)
heroku buildpacks:add heroku/nodejs

# Add Python buildpack second (for backend)
heroku buildpacks:add heroku/python

# Verify
heroku buildpacks
```

You should see:
```
1. heroku/nodejs
2. heroku/python
```

### Step 5: Deploy

```bash
# Push to Heroku
git push heroku main

# Or if your branch is named differently
git push heroku master
```

### Step 6: Verify Deployment

```bash
# Open your app
heroku open

# Check logs
heroku logs --tail

# Check status
heroku ps
```

---

## What Happens During Deployment

### Build Process

1. **Node.js Build**:
   - Installs npm dependencies
   - Runs `npm run build` in frontend
   - Creates `frontend/dist` folder

2. **Python Build**:
   - Installs Python 3.11
   - Installs dependencies from `requirements.txt`
   - Sets up FastAPI app

3. **Final Setup**:
   - Combines frontend (static) with backend (API)
   - Starts web dyno with Procfile

### Runtime

- **Web Dyno**: Runs `uvicorn app.main:app`
- **Port**: Auto-assigned by Heroku (`$PORT`)
- **Frontend**: Served from `frontend/dist` by FastAPI
- **API**: Available at `/datasets/`, `/analysis/`, etc.

---

## File Structure for Deployment

```
Senalign/
├── Procfile                 # Tells Heroku how to run the app
├── runtime.txt              # Specifies Python version
├── requirements.txt         # Python dependencies
├── package.json             # Node build scripts
├── app.json                # Heroku app configuration
├── app/                    # Backend code
│   └── main.py             # Updated to serve frontend
└── frontend/
    ├── package.json        # Frontend dependencies
    ├── vite.config.js      # Updated for production
    └── dist/               # Built frontend (created during deploy)
```

---

## Environment Variables

Set these in Heroku:

### Required

```bash
OPENAI_API_KEY=sk-...        # Your OpenAI API key
SECRET_KEY=random_string     # Auto-generated or manual
```

### Optional

```bash
EXA_API_KEY=...              # For future Feature 2
KAGGLE_USERNAME=...          # For future Feature 3
KAGGLE_KEY=...               # For future Feature 3
DATA_DIR=/tmp/data           # Where to store uploads
MAX_UPLOAD_SIZE_MB=100       # Max file size
```

View/Set via dashboard: `https://dashboard.heroku.com/apps/YOUR_APP_NAME/settings`

Or via CLI:
```bash
heroku config                  # View all
heroku config:set KEY=VALUE   # Set
heroku config:unset KEY       # Remove
```

---

## Troubleshooting

### Build Fails

**Check logs:**
```bash
heroku logs --tail
```

**Common issues:**
- Missing buildpack: Add both nodejs and python
- Dependency error: Check `requirements.txt` syntax
- Frontend build error: Check `frontend/package.json`

### App Crashes

```bash
# Check dyno status
heroku ps

# Restart dyno
heroku restart

# View error logs
heroku logs --tail --dyno web
```

### "Application Error" Page

Usually means:
1. OPENAI_API_KEY not set
2. Python dependency failed to install
3. Port binding issue

**Fix:**
```bash
# Check config vars
heroku config

# Set missing vars
heroku config:set OPENAI_API_KEY=your_key

# Restart
heroku restart
```

### Frontend Not Loading

1. **Check if dist folder was built:**
```bash
heroku run ls -la frontend/
```

2. **Rebuild frontend:**
```bash
# Force rebuild
git commit --allow-empty -m "Rebuild"
git push heroku main
```

3. **Check app.main:app serves static files:**
```bash
heroku logs --tail | grep "Serving frontend"
```

### Data Upload Issues

Heroku has an **ephemeral filesystem**. Uploaded files are lost on dyno restart.

**Solution:**
- Use S3 for persistent storage (Feature 3)
- Or accept that uploads are temporary

---

## Scaling

### Free Tier
```bash
# 1 web dyno (free)
heroku ps:scale web=1
```

### Production
```bash
# Upgrade to paid dyno
heroku dyno:resize web=basic

# Or professional
heroku dyno:resize web=standard-1x
```

### Multiple Dynos
```bash
# Scale to 2 dynos
heroku ps:scale web=2
```

**Note:** Multiple dynos require session persistence (e.g., Redis) for job storage.

---

## Monitoring

### View Logs
```bash
heroku logs --tail
```

### Metrics (paid plans)
```bash
heroku metrics
```

### Add-ons
```bash
# Logging
heroku addons:create papertrail

# Monitoring
heroku addons:create newrelic
```

---

## Updating the App

```bash
# Make changes locally
git add .
git commit -m "Update feature"

# Deploy
git push heroku main

# Auto-deploys on push
```

### Enable Auto-Deploy from GitHub

1. Connect repo to Heroku app
2. Enable auto-deploy from main branch
3. Optionally enable "Wait for CI"

---

## Custom Domain

```bash
# Add domain
heroku domains:add www.yourdomain.com

# Get DNS target
heroku domains

# Update DNS records (CNAME)
# Point www.yourdomain.com to DNS target
```

---

## Database (Future)

For persistent storage:

```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Get connection string
heroku config:get DATABASE_URL
```

---

## Cost Estimate

### Free Tier
- 550-1000 dyno hours/month
- Good for testing
- Sleeps after 30min inactivity

### Basic ($7/month)
- No sleeping
- Always available
- Good for demos

### Standard ($25-50/month)
- Better performance
- Multiple dynos
- Metrics included

---

## Security

### Environment Variables
- ✅ Never commit `.env` to git
- ✅ Use `heroku config:set`
- ✅ Rotate keys regularly

### HTTPS
- ✅ Auto-enabled by Heroku
- ✅ Free SSL certificate

### API Keys
- ✅ OPENAI_API_KEY kept secret
- ✅ Only set via config vars

---

## Performance Tips

1. **Use Parquet files** for faster uploads
2. **Enable gzip** in FastAPI (add middleware)
3. **Use Redis** for job storage (instead of in-memory)
4. **Upgrade dyno** if slow
5. **Use CDN** for static files (CloudFlare)

---

## Backup Strategy

Since Heroku filesystem is ephemeral:

1. **Code**: Keep in Git/GitHub
2. **Uploads**: Use S3 (implement in Feature 3)
3. **Database**: Auto-backup with Heroku Postgres
4. **Config**: Document all env vars

---

## Next Steps

After deployment:

1. ✅ Test file upload
2. ✅ Test analysis with OpenAI
3. ✅ Monitor logs for errors
4. ✅ Set up custom domain
5. ✅ Enable auto-deploy from GitHub
6. ✅ Add monitoring (New Relic, Sentry)

---

## GitHub Integration (Recommended)

### Setup

1. Go to Heroku dashboard
2. Select your app
3. Click "Deploy" tab
4. Connect to GitHub
5. Select repository
6. Enable automatic deploys

### Benefits

- Auto-deploy on push to main
- Review apps for PRs
- Easy rollback
- Deployment history

---

## Heroku CLI Commands Cheat Sheet

```bash
# App Management
heroku create [app-name]
heroku apps
heroku apps:destroy [app-name]
heroku open

# Deployment
git push heroku main
heroku releases
heroku rollback

# Environment
heroku config
heroku config:set KEY=VALUE
heroku config:unset KEY

# Logs
heroku logs
heroku logs --tail
heroku logs --source app

# Dyno Management
heroku ps
heroku ps:scale web=1
heroku restart

# Database
heroku pg
heroku pg:backups
heroku pg:backups:download

# Add-ons
heroku addons
heroku addons:create ADDON_NAME
```

---

## Support

- **Heroku Docs**: https://devcenter.heroku.com
- **Status**: https://status.heroku.com
- **Support**: https://help.heroku.com

---

**Ready to deploy!** 🚀

Run `git push heroku main` to deploy your app!
