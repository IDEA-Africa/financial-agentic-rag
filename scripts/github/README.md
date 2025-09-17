# GitHub MCP Integration Setup Scripts

This directory contains scripts for setting up GitHub Actions automation for the MCP (Model Context Protocol) integration with the financial-agentic-rag project.

## Quick Start

1. **Authenticate with GitHub CLI** (required):
   ```bash
   gh auth login
   ```

2. **Run complete setup**:
   ```bash
   ./complete-github-setup.sh
   ```

## Individual Scripts

### T002: setup-github-secrets.sh
Configures GitHub Actions secrets for SSH deployment key.
- Sets `DEPLOY_SSH_PRIVATE_KEY` secret
- Uses existing SSH key at `~/.ssh/financial_agentic_rag_github_deploy`

### T003: setup-github-environment-vars.sh
Sets up repository-level environment variables for MCP server configuration.
- MCP server settings (host, port, protocol version)
- GitHub integration settings (API version, repository details)
- IDEA Africa branding configuration

### T004: setup-deployment-environment.sh
Creates GitHub Actions deployment environment with protection rules.
- Creates `financial-agentic-rag-deploy` environment
- Sets environment-specific secrets
- Configures deployment protection (reviewers can be added later)

## GitHub Actions Workflows

### .github/workflows/ssh-agent-config.yml
Reusable workflow template for SSH agent configuration.
- Configures SSH agent with deployment key
- Sets up SSH known hosts and configuration
- Tests SSH connection

### .github/workflows/test-ssh-deployment.yml
Manual workflow for testing SSH authentication and deployment setup.
- Dry-run mode: Tests SSH connection only
- Full-test mode: Simulates complete deployment
- Generates detailed test report

## Usage

1. Ensure you have the SSH deployment key generated:
   ```bash
   ls -la ~/.ssh/financial_agentic_rag_github_deploy*
   ```

2. Authenticate GitHub CLI:
   ```bash
   gh auth status
   ```

3. Run the complete setup:
   ```bash
   cd /path/to/financial-agentic-rag
   ./scripts/github/complete-github-setup.sh
   ```

4. Verify setup:
   ```bash
   gh secret list --repo IDEA-Africa/financial-agentic-rag
   gh variable list --repo IDEA-Africa/financial-agentic-rag
   ```

5. Test SSH deployment:
   ```bash
   gh workflow run test-ssh-deployment.yml --repo IDEA-Africa/financial-agentic-rag
   ```

## Security Notes

- SSH private key is stored securely in GitHub Actions secrets
- Environment variables are repository-scoped
- Deployment environment can have reviewer requirements for production
- All secrets are encrypted and only accessible to authorized workflows

## Next Steps

After completing the GitHub setup phase:
1. Implement GitHub Actions CI/CD workflows (Phase 2)
2. Set up MCP server infrastructure (Phase 3)
3. Begin MCP server implementation (Phase 4+)

## Support

For issues with GitHub setup:
- Check GitHub CLI authentication: `gh auth status`
- Verify repository access: `gh repo view IDEA-Africa/financial-agentic-rag`
- Review GitHub Actions logs in the repository Actions tab