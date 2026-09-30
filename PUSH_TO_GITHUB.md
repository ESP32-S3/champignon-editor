# Push Champignon Editor to GitHub

## Prerequisites

1. **GitHub Account** - Create one at https://github.com if you don't have one
2. **Git CLI** - Already installed (`git --version`)
3. **SSH or HTTPS Access** - Set up authentication

## Steps to Push to GitHub

### Option 1: Using HTTPS (Easier for first-time)

```bash
# Navigate to the project
cd ~/champignon-editor

# Add GitHub remote
git remote add origin https://github.com/esp32s3/champignon-editor.git

# Push to GitHub
git branch -M main
git push -u origin main
```

When prompted, use your GitHub personal access token (not password):
1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select scopes: `repo` (full control)
4. Copy the token
5. Paste when git asks for password

### Option 2: Using SSH (More secure)

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add SSH key to GitHub
# 1. Copy the public key:
cat ~/.ssh/id_ed25519.pub

# 2. Go to https://github.com/settings/keys
# 3. Click "New SSH key"
# 4. Paste and save

# Then push:
cd ~/champignon-editor
git remote add origin git@github.com:esp32s3/champignon-editor.git
git branch -M main
git push -u origin main
```

## Full Push Commands

All in one go:

```bash
cd ~/champignon-editor

# Create remote (choose HTTPS or SSH)
git remote add origin https://github.com/esp32s3/champignon-editor.git
# OR
git remote add origin git@github.com:esp32s3/champignon-editor.git

# Rename branch to 'main'
git branch -M main

# Push to GitHub
git push -u origin main
```

## Verify Success

After pushing, verify on GitHub:

```bash
# Check remote
git remote -v

# Should show:
# origin  https://github.com/esp32s3/champignon-editor.git (fetch)
# origin  https://github.com/esp32s3/champignon-editor.git (push)
```

Then visit: `https://github.com/esp32s3/champignon-editor`

## What Will Be Uploaded

✅ **Files:**
- `champignon_editor.py` - Main application (1000+ lines)
- `setup.py` - Installation script
- `requirements.txt` - Dependencies
- `config.json` - Configuration
- `fonts/` - Champignon font files
- `README.md` - Complete GitHub documentation
- `LICENSE` - MIT License
- `.gitignore` - Git exclusions
- Plus documentation files (GUIDE.md, UPDATES.md, etc.)

✅ **Included:**
- Champignon font (both OTF and TTF variants)
- Full source code
- Complete documentation
- License and attribution

❌ **Not Included:**
- `__pycache__/` - Python cache
- `.git/` - Git metadata (it's local)
- Temporary files

## After First Push

### Update Project Settings

On GitHub:

1. Go to Settings → General
   - Description: "A code editor with syntax highlighting and multi-language execution featuring Champignon font"
   - Homepage: (optional)

2. Go to Settings → Topics
   - Add: `python`, `pyqt6`, `code-editor`, `syntax-highlighting`, `multi-language`

3. Go to About → Release
   - Create release v1.2.0

### Create Release

```bash
# Tag the version
git tag -a v1.2.0 -m "Release version 1.2.0"

# Push tags
git push origin v1.2.0
```

Then on GitHub:
1. Go to Releases
2. Click "Create release from tag"
3. Add release notes
4. Publish

## Future Updates

For subsequent commits:

```bash
# Make changes
git add .
git commit -m "Description of changes"
git push origin main
```

## Troubleshooting

**"fatal: remote origin already exists"**
```bash
git remote remove origin
# Then add again
```

**"Permission denied (publickey)"**
- SSH key not set up correctly
- Use HTTPS instead
- Or check SSH key permissions: `chmod 600 ~/.ssh/id_ed25519`

**"fatal: 'origin' does not appear to be a 'git' repository"**
- Make sure you're in the right directory
- Check: `pwd` should be in `~/champignon-editor`

**"Your branch is ahead of 'origin/main' by X commits"**
```bash
git push origin main
```

## GitHub Features to Enable

After pushing:

1. **Issues** - For bug reports and feature requests
2. **Discussions** - For general questions
3. **GitHub Pages** (optional) - For documentation site
4. **GitHub Actions** (optional) - For CI/CD

## File Structure on GitHub

```
champignon-editor/
├── README.md                    # Main documentation
├── LICENSE                      # MIT License
├── GUIDE.md                     # Full user guide
├── UPDATES.md                   # Version history
├── RUN_EXAMPLES.md             # Code examples
├── PUSH_TO_GITHUB.md           # (This file)
├── champignon_editor.py        # Main application
├── setup.py                    # Installation script
├── requirements.txt            # Dependencies
├── config.json                 # Configuration
├── run_editor.sh               # Launch script
├── champignon-editor.desktop   # Desktop entry
├── test_hb_shaping.py         # Feature tests
├── .gitignore                 # Git exclusions
├── .git/                      # Git repository (local)
└── fonts/
    ├── Champignon-Regular.otf
    └── Champignon-AltSwash.ttf
```

---

**Status:** Ready to push! 🚀

Once pushed, the project will be publicly available at:
`https://github.com/esp32s3/champignon-editor`
