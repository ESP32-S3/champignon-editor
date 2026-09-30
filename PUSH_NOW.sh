#!/bin/bash
# Champignon Editor - Push to GitHub Script
# This script handles all the git operations to push to GitHub

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     CHAMPIGNON EDITOR - GITHUB PUSH SCRIPT                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

cd "$(dirname "$0")"

echo "📋 Current Git Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git log --oneline | head -3
echo

echo "🔐 GitHub Authentication:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "IMPORTANT: Before pushing, you need GitHub authentication."
echo "Choose one:"
echo
echo "1️⃣  HTTPS (uses GitHub Personal Access Token)"
echo "   - Go to: https://github.com/settings/tokens"
echo "   - Create new token with 'repo' scope"
echo "   - Use token as password when git asks"
echo
echo "2️⃣  SSH (uses SSH key)"
echo "   - Check if SSH key exists: ssh-keygen -t ed25519 -C 'your-email@example.com'"
echo "   - Add to GitHub: https://github.com/settings/keys"
echo "   - Copy: cat ~/.ssh/id_ed25519.pub"
echo "   - Paste in 'New SSH key' on GitHub"
echo

read -p "Press Enter when you have set up authentication (1 or 2 above)..."
echo

echo "🚀 Pushing to GitHub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Set up git config
git config user.name "esp32s3"
git config user.email "esp32s3@github.com"

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "Remote 'origin' already exists"
    git remote -v
else
    echo "Adding remote origin..."
    git remote add origin https://github.com/esp32s3/champignon-editor.git
fi

# Ensure on main branch
echo "Switching to main branch..."
git branch -M main

# Push to GitHub
echo "Pushing code to GitHub (you may need to authenticate)..."
git push -u origin main

echo
echo "✅ PUSH COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Your repository is now at:"
echo "  https://github.com/esp32s3/champignon-editor"
echo
echo "Share with others or deploy using:"
echo "  git clone https://github.com/esp32s3/champignon-editor.git"
echo
