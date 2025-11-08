# 📘 GitHub Setup & Deployment Guide

This guide will help you set up the GitHub repository and configure automatic deployment to Heroku.

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI

```bash
cd /Users/jotham/MEGA/Projects/Senalign

# Login to GitHub
gh auth login

# Create repository
gh repo create senalign --public --source=. --remote=origin

# Push code
git push -u origin main
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `senalign`
3. Description: "AI-powered dataset quality validation with GPT-4o"
4. Public/Private: Choose your preference
5. Don't initialize with README (we already have one)
6. Click "Create repository"

Then push your code:
```bash
cd /Users/jotham/MEGA/Projects/Senalign

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/senalign.git

# Push
git push -u origin main
```

---

## Step 2: Set Up Repository Secrets

For GitHub Actions to deploy to Heroku, you need to add secrets.

### Via GitHub Web Interface

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name | Value | Where to get it |
|------------|-------|-----------------|
| `HEROKU_API_KEY` | Your Heroku API key | https://dashboard.heroku.com/account |
| `HEROKU_APP_NAME` | Your Heroku app name | From `heroku create` |
| `HEROKU_EMAIL` | Your Heroku email | Your Heroku account email |
| `OPENAI_API_KEY` | Your OpenAI key | https://platform.openai.com |

### Get Heroku API Key

```bash
heroku auth:token
```

Copy the output and use it as `HEROKU_API_KEY`.

---

## Step 3: Configure Automatic Deployment

### Method 1: GitHub Actions (Recommended)

The repository already includes:
- `.github/workflows/deploy.yml` - Auto-deploy on push to main
- `.github/workflows/test.yml` - Run tests on push/PR

**Setup:**
1. Add secrets (Step 2 above)
2. Push to main branch
3. GitHub Actions will automatically deploy

**Monitor:**
- Go to repository → **Actions** tab
- Watch deployment progress
- Check logs if deployment fails

### Method 2: Heroku GitHub Integration

1. Go to Heroku Dashboard
2. Select your app
3. Click **Deploy** tab
4. Click **GitHub** under "Deployment method"
5. Connect to your GitHub account
6. Search for `senalign` repository
7. Click **Connect**
8. Enable **Automatic deploys** from main branch
9. Optionally check "Wait for CI to pass"

**Benefits:**
- Review apps for pull requests
- Easy rollback
- Deployment history in Heroku dashboard

---

## Step 4: Project Structure

Make sure your repository has:

```
senalign/
├── .github/
│   └── workflows/
│       ├── deploy.yml       # Auto-deploy to Heroku
│       └── test.yml         # Run tests
├── app/                     # Backend code
├── frontend/                # Frontend code
├── tests/                   # Test files
├── Procfile                 # Heroku process file
├── runtime.txt              # Python version
├── requirements.txt         # Python dependencies
├── package.json             # Node scripts
├── app.json                 # Heroku app config
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
├── HEROKU_DEPLOY.md        # Deployment guide
└── GITHUB_SETUP.md         # This file
```

---

## Step 5: Test Deployment

### Trigger Manual Deployment

```bash
# Make a change
echo "# Test" >> README.md

# Commit
git add .
git commit -m "Test deployment"

# Push (triggers auto-deploy)
git push origin main
```

### Watch Deployment

**GitHub Actions:**
```
Repository → Actions → Latest workflow run
```

**Heroku:**
```bash
heroku logs --tail
```

Or via dashboard:
```
https://dashboard.heroku.com/apps/YOUR_APP_NAME/activity
```

---

## Step 6: Add README Badges

Update your README.md with deployment status:

```markdown
# Senalign Dataset Quality Validator

![Deployment](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/senalign/deploy.yml?label=deployment)
![Tests](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/senalign/test.yml?label=tests)
![Heroku](https://img.shields.io/badge/heroku-deployed-purple)

[Live Demo](https://your-app-name.herokuapp.com)
```

---

## Step 7: Branch Protection (Recommended)

Protect your main branch:

1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Branch name pattern: `main`
4. Check:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass (Tests)
   - ✅ Require branches to be up to date
5. Save

---

## Development Workflow

### Feature Branch Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ...

# Commit
git add .
git commit -m "Add my feature"

# Push
git push origin feature/my-feature

# Create Pull Request on GitHub
# Tests will run automatically
# Merge when ready → Auto-deploys to Heroku
```

---

## Environment Variables

### GitHub Secrets (for Actions)

Set in: Repository → Settings → Secrets

```
HEROKU_API_KEY      # For deployment
HEROKU_APP_NAME     # For deployment
HEROKU_EMAIL        # For deployment
OPENAI_API_KEY      # For running tests
```

### Heroku Config Vars

Set in: Heroku Dashboard → Settings → Config Vars

Or via CLI:
```bash
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
```

---

## Troubleshooting

### Deployment Fails

1. **Check GitHub Actions logs:**
   - Repository → Actions → Failed workflow → View logs

2. **Common issues:**
   - Missing secret: Add all required secrets
   - Heroku API key invalid: Regenerate with `heroku auth:token`
   - App name wrong: Check Heroku dashboard

### Tests Fail

1. **Check test logs:**
   - Actions → Failed test run → View logs

2. **Run locally:**
   ```bash
   export OPENAI_API_KEY=your_key
   export SECRET_KEY=test-key
   pytest tests/ -v
   ```

### Can't Push to GitHub

```bash
# Check remote
git remote -v

# Fix if needed
git remote set-url origin https://github.com/YOUR_USERNAME/senalign.git

# Try again
git push origin main
```

---

## Repository Settings

### Recommended Settings

**General:**
- ✅ Issues enabled
- ✅ Discussions enabled (for community)
- ✅ Allow squash merging

**Actions:**
- ✅ Allow all actions and reusable workflows
- ✅ Save workflow runs for 90 days

**Secrets:**
- ✅ All secrets added
- ✅ Environment secrets for production

**Webhooks:**
- Heroku webhook (auto-added if using Heroku GitHub integration)

---

## Continuous Integration

### What Runs on Push

1. **Tests** (`test.yml`):
   - Runs pytest
   - Checks code quality
   - Reports status to PR

2. **Deploy** (`deploy.yml`):
   - Only on main branch
   - Deploys to Heroku
   - Reports deployment status

### What Runs on Pull Request

1. **Tests** only
2. Blocks merge if tests fail
3. Heroku review app (if configured)

---

## Monitoring

### GitHub Insights

- **Pulse**: Recent activity
- **Contributors**: Who's contributing
- **Traffic**: Views and clones
- **Commits**: Commit history

### Deployment History

- **GitHub**: Actions tab
- **Heroku**: Activity tab in dashboard

---

## Collaboration

### Adding Collaborators

```bash
# Via CLI
gh repo edit --add-collaborator username

# Or via web
Repository → Settings → Manage access → Invite
```

### Setting Permissions

- **Read**: Can view code
- **Write**: Can push to non-protected branches
- **Admin**: Full access

---

## License

Add a LICENSE file:

```bash
# Create LICENSE file
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge...
EOF

git add LICENSE
git commit -m "Add LICENSE"
git push
```

---

## Next Steps

After setup:

1. ✅ Repository created
2. ✅ Secrets configured
3. ✅ Auto-deploy enabled
4. ✅ Tests running
5. ✅ Branch protection set up

**Now you can:**
- Share repository with team
- Accept pull requests
- Auto-deploy to Heroku on merge
- Monitor deployment status

---

## Quick Commands Reference

```bash
# Repository
gh repo create senalign --public
gh repo view --web

# Deploy
git push origin main                    # Triggers auto-deploy

# Secrets
gh secret set HEROKU_API_KEY
gh secret list

# Actions
gh run list                            # List workflow runs
gh run view                            # View latest run
gh run watch                           # Watch current run

# Heroku
heroku logs --tail                     # View logs
heroku open                            # Open app
heroku config                          # View env vars
```

---

**Your repository is ready for collaboration and auto-deployment!** 🚀
