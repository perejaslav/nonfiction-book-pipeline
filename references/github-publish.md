# Publishing a Hermes Skill as a GitHub Repository

Complete recipe for turning a local skill into a public GitHub repo from a headless/VPS environment.

## 1. Prepare local directory

```bash
mkdir -p /path/to/repo-name/{docs,templates,examples,scripts}
cp -r /root/.hermes/skills/<category>/<skill>/templates/* templates/
cp -r /root/.hermes/skills/<category>/<skill>/references/* examples/
```

Minimum files:
- `README.md` — description, triggers, quickstart
- `LICENSE` — MIT
- `.gitignore`
- `docs/` — ARCHITECTURE.md, PIPELINE.md, TROUBLESHOOTING.md
- `templates/` — starter files
- `examples/` — real-world samples
- `scripts/` — helper scripts (Python, bash)

## 2. Create repo via GitHub REST API

```bash
# Read PAT from ~/.git-credentials
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "repo-name",
    "description": "Description here",
    "private": false
  }'
```

Response contains `"html_url": "https://github.com/user/repo-name"`.

## 3. Initialize and commit locally

```bash
cd /path/to/repo-name
git init
git add .
git commit -m "Initial commit"
git branch -m main
```

## 4. Push from non-interactive environment

**Problem:** `git push` fails with:
```
fatal: could not read Username for 'https://github.com': No such device or address
```

**Solution:** temporarily embed PAT into remote URL, push, then sanitize.

```bash
# Get token from ~/.git-credentials (format: https://USER:TOKEN@github.com)
TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
USER=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://\([^:]*\):.*|\1|')

# Set token-embedded remote
git remote add origin "https://${USER}:${TOKEN}@github.com/${USER}/repo-name.git"

# Push
git push -u origin main

# Sanitize — remove token from .git/config
git remote set-url origin "https://github.com/${USER}/repo-name.git"
```

Alternative: use credential store:
```bash
git config --global credential.helper 'store --file ~/.git-credentials'
```

## 5. Verify

```bash
curl -s https://api.github.com/repos/$USER/repo-name/contents/ | jq '.[].name'
```

## Reference: real-world example

Published repo: https://github.com/perejaslav/nonfiction-book-pipeline
Created: 2026-05-01 from local skill `/root/.hermes/skills/software-development/nonfiction-book-pipeline`.
