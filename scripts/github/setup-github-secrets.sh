#!/bin/bash

# T002: Configure GitHub Actions secrets for deployment key
# This script helps set up GitHub Actions secrets for the financial-agentic-rag repository

set -e

echo "🔐 GitHub Actions Secrets Setup for MCP Integration"
echo "================================================="

# Check if GitHub CLI is authenticated
if ! gh auth status > /dev/null 2>&1; then
    echo "❌ GitHub CLI is not authenticated."
    echo "Please run: gh auth login"
    echo "Then re-run this script."
    exit 1
fi

echo "✅ GitHub CLI is authenticated"

# Set repository context
REPO="IDEA-Africa/financial-agentic-rag"
PRIVATE_KEY_PATH="$HOME/.ssh/financial_agentic_rag_github_deploy"
PUBLIC_KEY_PATH="$HOME/.ssh/financial_agentic_rag_github_deploy.pub"

echo "📁 Repository: $REPO"
echo "🔑 Private key: $PRIVATE_KEY_PATH"
echo "🔓 Public key: $PUBLIC_KEY_PATH"

# Verify keys exist
if [[ ! -f "$PRIVATE_KEY_PATH" ]]; then
    echo "❌ Private key not found at $PRIVATE_KEY_PATH"
    echo "Please ensure the SSH keys are generated."
    exit 1
fi

if [[ ! -f "$PUBLIC_KEY_PATH" ]]; then
    echo "❌ Public key not found at $PUBLIC_KEY_PATH"
    echo "Please ensure the SSH keys are generated."
    exit 1
fi

echo "✅ SSH keys found"

# Read the private key (be careful with this!)
echo "📖 Reading private key..."
PRIVATE_KEY_CONTENT=$(cat "$PRIVATE_KEY_PATH")

# Set GitHub Actions secret for deployment key
echo "🔐 Setting DEPLOY_SSH_PRIVATE_KEY secret..."
echo "$PRIVATE_KEY_CONTENT" | gh secret set DEPLOY_SSH_PRIVATE_KEY --repo "$REPO"

if [[ $? -eq 0 ]]; then
    echo "✅ DEPLOY_SSH_PRIVATE_KEY secret set successfully"
else
    echo "❌ Failed to set DEPLOY_SSH_PRIVATE_KEY secret"
    exit 1
fi

echo ""
echo "✅ T002 Completed: GitHub Actions secrets configured!"
echo ""
echo "Next steps:"
echo "1. Verify the secret is set: gh secret list --repo $REPO"
echo "2. Continue with T003: Setup environment variables"
