#!/bin/bash

# T003: Setup GitHub Actions environment variables for MCP server configuration
# This script sets up repository-level environment variables for MCP server

set -e

echo "🌐 GitHub Actions Environment Variables Setup"
echo "============================================"

# Check if GitHub CLI is authenticated
if ! gh auth status > /dev/null 2>&1; then
    echo "❌ GitHub CLI is not authenticated."
    echo "Please run: gh auth login"
    echo "Then re-run this script."
    exit 1
fi

REPO="IDEA-Africa/financial-agentic-rag"
echo "📁 Repository: $REPO"

# Set MCP server configuration variables
echo "🔧 Setting MCP server environment variables..."

# MCP Server Configuration
gh variable set MCP_SERVER_HOST --body "localhost" --repo "$REPO"
gh variable set MCP_SERVER_PORT --body "8000" --repo "$REPO"
gh variable set MCP_PROTOCOL_VERSION --body "1.0.0" --repo "$REPO"

# GitHub Integration Configuration
gh variable set MCP_GITHUB_ENABLED --body "true" --repo "$REPO"
gh variable set GH_API_VERSION --body "2022-11-28" --repo "$REPO"
gh variable set GH_REPO_OWNER --body "IDEA-Africa" --repo "$REPO"
gh variable set GH_REPO_NAME --body "financial-agentic-rag" --repo "$REPO"

# Deployment Configuration
gh variable set DEPLOYMENT_TARGET --body "localhost" --repo "$REPO"
gh variable set DEPLOYMENT_USER --body "ubuntu" --repo "$REPO"
gh variable set DEPLOYMENT_PATH --body "/opt/financial-agentic-rag" --repo "$REPO"

# MCP Tool Configuration
gh variable set MCP_TOOLS_ENABLED --body "github_commit,github_pr_create,github_review" --repo "$REPO"
gh variable set HUMAN_APPROVAL_REQUIRED --body "true" --repo "$REPO"
gh variable set APPROVAL_TIMEOUT_MINUTES --body "5" --repo "$REPO"

# Database Configuration
gh variable set DATABASE_TYPE --body "postgresql" --repo "$REPO"
gh variable set DATABASE_HOST --body "localhost" --repo "$REPO"
gh variable set DATABASE_PORT --body "5432" --repo "$REPO"
gh variable set DATABASE_NAME --body "financial_rag_mcp" --repo "$REPO"

# Performance Configuration
gh variable set MCP_MAX_CONCURRENT_OPERATIONS --body "10" --repo "$REPO"
gh variable set GH_API_RATE_LIMIT_BUFFER --body "100" --repo "$REPO"

# IDEA Africa Branding
gh variable set ENABLE_IDEA_AFRICA_BRANDING --body "true" --repo "$REPO"
gh variable set THEME_PRIMARY_COLOR --body "#2E8B57" --repo "$REPO" # Digital Earth Africa green
gh variable set THEME_SECONDARY_COLOR --body "#4682B4" --repo "$REPO" # Steel blue

echo "✅ Environment variables set successfully!"
echo ""
echo "📋 Configured variables:"
echo "  - MCP_SERVER_HOST=localhost"
echo "  - MCP_SERVER_PORT=8000"
echo "  - GH_REPO_OWNER=IDEA-Africa"
echo "  - GH_REPO_NAME=financial-agentic-rag"
echo "  - HUMAN_APPROVAL_REQUIRED=true"
echo "  - ENABLE_IDEA_AFRICA_BRANDING=true"
echo ""
echo "🔍 Verify variables: gh variable list --repo $REPO"
echo ""
echo "✅ T003 Completed: GitHub Actions environment variables configured!"