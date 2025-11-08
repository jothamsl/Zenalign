#!/bin/bash

# Senalign Heroku Deployment Script
# This script automates the deployment of Senalign to Heroku

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

# Check if Heroku CLI is installed
check_heroku_cli() {
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI is not installed"
        print_info "Install it from: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    print_success "Heroku CLI is installed"
}

# Check if user is logged in to Heroku
check_heroku_login() {
    if ! heroku auth:whoami &> /dev/null; then
        print_error "Not logged in to Heroku"
        print_info "Please run: heroku login"
        exit 1
    fi
    HEROKU_USER=$(heroku auth:whoami)
    print_success "Logged in as: $HEROKU_USER"
}

# Check if git is initialized
check_git() {
    if [ ! -d .git ]; then
        print_warning "Git repository not initialized"
        print_info "Initializing git repository..."
        git init
        git add .
        git commit -m "Initial commit for Heroku deployment"
        print_success "Git repository initialized"
    else
        print_success "Git repository exists"
    fi
}

# Create Heroku app
create_heroku_app() {
    local APP_NAME=$1

    if [ -z "$APP_NAME" ]; then
        print_info "Creating Heroku app with auto-generated name..."
        APP_NAME=$(heroku create --json | grep -o '"name":"[^"]*' | grep -o '[^"]*$')
    else
        print_info "Creating Heroku app: $APP_NAME..."
        heroku create "$APP_NAME" || {
            print_error "Failed to create app. App name might be taken."
            exit 1
        }
    fi

    print_success "Heroku app created: $APP_NAME"
    echo "$APP_NAME" > .heroku_app_name
    echo "$APP_NAME"
}

# Add MongoDB Atlas add-on
add_mongodb() {
    local APP_NAME=$1

    print_info "Adding MongoDB Atlas add-on..."

    # Try to add MongoDB Atlas (free tier)
    if heroku addons:create mongolab:sandbox -a "$APP_NAME" 2>/dev/null; then
        print_success "MongoDB Atlas add-on added (mongolab)"
    elif heroku addons:create mongodb-atlas:free -a "$APP_NAME" 2>/dev/null; then
        print_success "MongoDB Atlas add-on added (mongodb-atlas)"
    else
        print_warning "Could not auto-add MongoDB. You'll need to:"
        print_info "1. Go to https://cloud.mongodb.com/ and create a free cluster"
        print_info "2. Get your connection string"
        print_info "3. Set it with: heroku config:set MONGODB_URI='your-connection-string' -a $APP_NAME"
        read -p "Press Enter to continue..."
    fi
}

# Set environment variables
set_environment_variables() {
    local APP_NAME=$1

    print_info "Setting environment variables..."

    # Check if .env file exists
    if [ -f .env ]; then
        print_info "Found .env file. Extracting variables..."

        # Read .env and set each variable
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ $key =~ ^#.*$ ]] && continue
            [[ -z $key ]] && continue

            # Remove quotes from value
            value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")

            # Skip MongoDB URI (will be set by add-on)
            [[ $key == "MONGODB_URI" ]] && continue

            print_info "Setting $key..."
            heroku config:set "$key=$value" -a "$APP_NAME" > /dev/null 2>&1
        done < .env

        print_success "Environment variables set from .env file"
    else
        print_warning "No .env file found. Setting default variables..."
    fi

    # Set production-specific variables
    print_info "Setting production variables..."
    heroku config:set INTERSWITCH_MODE=LIVE -a "$APP_NAME" > /dev/null 2>&1 || true
    heroku config:set PYTHON_ENV=production -a "$APP_NAME" > /dev/null 2>&1 || true

    print_success "Environment variables configured"

    # Display all config
    print_info "Current configuration:"
    heroku config -a "$APP_NAME"
}

# Build and deploy
deploy_app() {
    local APP_NAME=$1

    print_info "Deploying to Heroku..."

    # Add Heroku remote if not exists
    if ! git remote | grep -q heroku; then
        heroku git:remote -a "$APP_NAME"
        print_success "Added Heroku remote"
    fi

    # Commit any changes
    if ! git diff-index --quiet HEAD --; then
        print_info "Committing local changes..."
        git add .
        git commit -m "Deploy to Heroku" || true
    fi

    # Push to Heroku
    print_info "Pushing to Heroku (this may take a few minutes)..."
    git push heroku main || git push heroku master || {
        print_error "Failed to push to Heroku"
        print_info "If you're on a different branch, try:"
        print_info "  git push heroku your-branch:main"
        exit 1
    }

    print_success "Deployment complete!"
}

# Scale dynos
scale_dynos() {
    local APP_NAME=$1

    print_info "Scaling web dyno..."
    heroku ps:scale web=1 -a "$APP_NAME"
    print_success "Web dyno scaled to 1"
}

# Run migrations (if needed)
run_migrations() {
    local APP_NAME=$1

    print_info "Checking for migrations..."

    if [ -d "migrations" ]; then
        print_warning "Found migrations directory"
        print_info "You may need to run migrations manually:"
        print_info "  heroku run python migrations/grant_free_tokens_to_existing_users.py --live -a $APP_NAME"
    fi
}

# Open app in browser
open_app() {
    local APP_NAME=$1

    print_info "Opening app in browser..."
    heroku open -a "$APP_NAME"
}

# Display logs
show_logs() {
    local APP_NAME=$1

    print_info "Recent logs:"
    heroku logs --tail -n 50 -a "$APP_NAME"
}

# Main deployment flow
main() {
    print_header "Senalign Heroku Deployment"

    # Parse command line arguments
    APP_NAME=""
    SKIP_OPEN=false
    SHOW_LOGS=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --app|-a)
                APP_NAME="$2"
                shift 2
                ;;
            --skip-open)
                SKIP_OPEN=true
                shift
                ;;
            --logs|-l)
                SHOW_LOGS=true
                shift
                ;;
            --help|-h)
                echo "Usage: ./deploy_heroku.sh [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --app, -a NAME     Specify app name (optional)"
                echo "  --skip-open        Don't open browser after deploy"
                echo "  --logs, -l         Show logs after deployment"
                echo "  --help, -h         Show this help message"
                echo ""
                echo "Examples:"
                echo "  ./deploy_heroku.sh                    # Create new app with auto name"
                echo "  ./deploy_heroku.sh --app senalign     # Create app named 'senalign'"
                echo "  ./deploy_heroku.sh --logs             # Deploy and show logs"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                print_info "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Step 1: Pre-flight checks
    print_header "Step 1: Pre-flight Checks"
    check_heroku_cli
    check_heroku_login
    check_git

    # Step 2: Create or use existing app
    print_header "Step 2: Heroku App Setup"

    # Check if app already exists
    if [ -f .heroku_app_name ]; then
        EXISTING_APP=$(cat .heroku_app_name)
        print_info "Found existing app configuration: $EXISTING_APP"
        read -p "Use this app? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            APP_NAME=$EXISTING_APP
            print_success "Using existing app: $APP_NAME"
        else
            APP_NAME=$(create_heroku_app "$APP_NAME")
        fi
    else
        APP_NAME=$(create_heroku_app "$APP_NAME")
    fi

    # Step 3: Add MongoDB
    print_header "Step 3: Database Setup"
    add_mongodb "$APP_NAME"

    # Step 4: Configure environment
    print_header "Step 4: Environment Configuration"
    set_environment_variables "$APP_NAME"

    # Step 5: Deploy
    print_header "Step 5: Deployment"
    deploy_app "$APP_NAME"

    # Step 6: Scale dynos
    print_header "Step 6: Scaling"
    scale_dynos "$APP_NAME"

    # Step 7: Migrations
    print_header "Step 7: Post-Deployment"
    run_migrations "$APP_NAME"

    # Success!
    print_header "Deployment Complete! 🎉"

    APP_URL=$(heroku info -a "$APP_NAME" | grep "Web URL" | awk '{print $3}')

    echo ""
    print_success "Your app is now live!"
    echo ""
    print_info "App Name:    $APP_NAME"
    print_info "App URL:     $APP_URL"
    print_info "API Docs:    ${APP_URL}docs"
    echo ""

    print_info "Useful commands:"
    echo "  heroku logs --tail -a $APP_NAME           # View logs"
    echo "  heroku ps -a $APP_NAME                    # Check dyno status"
    echo "  heroku config -a $APP_NAME                # View config vars"
    echo "  heroku restart -a $APP_NAME               # Restart app"
    echo "  heroku run bash -a $APP_NAME              # Open shell"
    echo ""

    # Show logs if requested
    if [ "$SHOW_LOGS" = true ]; then
        print_header "Application Logs"
        show_logs "$APP_NAME"
    fi

    # Open app in browser
    if [ "$SKIP_OPEN" = false ]; then
        read -p "Open app in browser? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open_app "$APP_NAME"
        fi
    fi

    print_success "Deployment script completed successfully!"
}

# Run main function
main "$@"
