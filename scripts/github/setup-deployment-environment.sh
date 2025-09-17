#!/bin/bash

# T004: Create GitHub Actions deployment environment for financial-agentic-rag
# This script creates and configures a deployment environment with protection rules

set -e

echo "🏗️ GitHub Actions Deployment Environment Setup"
echo "=============================================="

# Check if GitHub CLI is authenticated
if ! gh auth status > /dev/null 2>&1; then
    echo "❌ GitHub CLI is not authenticated."
    echo "Please run: gh auth login"
    echo "Then re-run this script."
    exit 1
fi

REPO="IDEA-Africa/financial-agentic-rag"
ENV_NAME="financial-agentic-rag-deploy"

echo "📁 Repository: $REPO"
echo "🌍 Environment: $ENV_NAME"

# Create deployment environment
echo "🔧 Creating deployment environment..."

# Note: GitHub CLI doesn't have direct environment creation commands yet
# We need to use the GitHub API directly
echo "📋 Environment creation requires GitHub API calls..."

# Create the environment using GitHub REST API
echo "🚀 Creating environment '$ENV_NAME'..."
gh api repos/$REPO/environments/$ENV_NAME --method PUT -F wait_timer=0 -F prevent_self_review=false --silent

if [[ $? -eq 0 ]]; then
    echo "✅ Environment '$ENV_NAME' created successfully"
else
    echo "ℹ️ Environment may have already existed, or the API call failed. Continuing..."
fi

# Add environment-specific secrets (these override repository secrets for this environment)
echo "🔐 Setting environment-specific secrets..."

echo "localhost" | gh secret set DEPLOY_HOST --env "$ENV_NAME" --repo "$REPO"
echo "ubuntu" | gh secret set DEPLOY_USER --env "$ENV_NAME" --repo "$REPO"
echo "/opt/financial-agentic-rag" | gh secret set DEPLOY_PATH --env "$ENV_NAME" --repo "$REPO"
echo "✅ Environment secrets DEPLOY_HOST, DEPLOY_USER, and DEPLOY_PATH set."

# Note: For production, you would add protection rules like:
# - Required reviewers
# - Deployment branches (main, staging, etc.)
# - Wait timers before deployment

echo ""
echo "✅ T004 Completed: GitHub Actions deployment environment configured!"
echo ""
echo "Environment Details:"
echo "  - Name: $ENV_NAME"
echo "  - Repository: $REPO"
echo "  - Protection: Basic (can be enhanced for production)"
echo ""
echo "Next steps:"
echo "1. View environment: https://github.com/$REPO/settings/environments"
echo "2. Add reviewers if needed for production deployments"
echo "3. Configure branch protection rules"