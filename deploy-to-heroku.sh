#!/bin/bash

# Quick deploy script for Heroku
# This script helps you deploy Senalign to Heroku quickly

set -e

echo "=========================================="
echo "Senalign Heroku Deployment Script"
echo "=========================================="
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found!"
    echo "Install it from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✓ Heroku CLI found"

# Check if logged in
if ! heroku auth:whoami &> /dev/null; then
    echo "Please login to Heroku first:"
    heroku login
fi

echo "✓ Logged in to Heroku"
echo ""

# Ask for app name
read -p "Enter your Heroku app name (or press Enter for auto-generated): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "Creating Heroku app with auto-generated name..."
    heroku create
else
    echo "Creating Heroku app: $APP_NAME..."
    heroku create $APP_NAME
fi

echo ""
echo "✓ Heroku app created"
echo ""

# Get app name
APP_NAME=$(heroku apps:info --json | grep -o '"name":"[^"]*' | grep -o '[^"]*$')
echo "App URL: https://$APP_NAME.herokuapp.com"
echo ""

# Ask for OpenAI API key
read -p "Enter your OPENAI_API_KEY (required): " OPENAI_KEY

if [ -z "$OPENAI_KEY" ]; then
    echo "❌ OPENAI_API_KEY is required!"
    exit 1
fi

echo "Setting environment variables..."
heroku config:set OPENAI_API_KEY=$OPENAI_KEY

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)
heroku config:set SECRET_KEY=$SECRET_KEY

echo "✓ Environment variables set"
echo ""

# Add buildpacks
echo "Adding buildpacks..."
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python

echo "✓ Buildpacks added"
echo ""

# Deploy
echo "Deploying to Heroku..."
git push heroku main

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your app is available at:"
echo "https://$APP_NAME.herokuapp.com"
echo ""
echo "View logs with:"
echo "heroku logs --tail"
echo ""
echo "Open app with:"
echo "heroku open"
echo ""
