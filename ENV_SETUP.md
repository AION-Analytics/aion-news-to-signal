# AION Open-Source - Environment Setup Guide

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Git installed
- GitHub account
- HuggingFace account

---

## 1. GitHub Setup

### Generate Personal Access Token (PAT)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "AION Analytics")
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token** (starts with `ghp_...`)
   - ⚠️ Save it securely - you can't see it again!

### Configure Git

```bash
# Set your git identity
git config --global user.name "Your Name"
git config --global user.email "aionlabs@tutamail.com"

# Store credentials (optional but convenient)
git config --global credential.helper osxkeychain  # macOS
git config --global credential.helper store        # Linux/Windows
```

### Clone Repository

```bash
# Using HTTPS (recommended)
git clone https://github.com/AION-Analytics/market-sentiments.git

# Or using SSH (if you have SSH key set up)
git clone git@github.com:AION-Analytics/market-sentiments.git
```

### Push Changes

```bash
cd market-sentiments

# Make your changes
git add .
git commit -m "Your commit message"

# Push to GitHub
git push origin main
```

**If prompted for credentials:**
- Username: `aionlabs@tutamail.com`
- Password: Your PAT (starts with `ghp_...`)

---

## 2. HuggingFace Setup

### Generate Access Token

1. Go to: https://huggingface.co/settings/tokens
2. Click "Create new token"
3. Give it a name (e.g., "AION Analytics")
4. Select role: **Write**
5. Click "Generate token"
6. **Copy the token** (starts with `hf_...`)

### Install HuggingFace Hub

```bash
pip install huggingface_hub
```

### Login to HuggingFace

```bash
# Method 1: Interactive login
huggingface-cli login
# Paste your token when prompted

# Method 2: Set environment variable
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Method 3: Login with token directly
huggingface-cli login --token hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Upload Model

```bash
# Navigate to model directory
cd aion-sentiment-in

# Upload using CLI
huggingface-cli upload AION-Analytics/aion-sentiment-in-v1 ./models/aion-sentiment-in-v1

# Or use Python
python upload_to_huggingface.py --repo-id AION-Analytics/aion-sentiment-in-v1
```

### Download Model

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "AION-Analytics/aion-sentiment-in-v1"

# Downloads automatically on first use
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```

---

## 3. Python Environment Setup

### Create Virtual Environment

```bash
cd /Users/lokeshgupta/aion_open_source

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
# For aion-sentiment (inference)
cd aion-sentiment
pip install -e ".[dev]"

# For aion-sentiment-in (training)
cd ../aion-sentiment-in
pip install -e ".[dev]"

# For aion-sectormap
cd ../aion-sectormap
pip install -e ".[dev]"

# For aion-volweight
cd ../aion-volweight
pip install -e ".[dev]"

# For aion-newsimpact
cd ../aion-newsimpact
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Test imports
python3 -c "from aion_sentiment import AIONSentimentAnalyzer; print('OK')"
python3 -c "from aion_sectormap import SectorMapper; print('OK')"
python3 -c "from aion_volweight import weight_confidence; print('OK')"
python3 -c "from aion_newsimpact import NewsImpact; print('OK')"
```

---

## 4. Environment Variables

### Required for GitHub

```bash
# Optional - if you don't want to enter credentials each time
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Required for HuggingFace

```bash
# Required for model upload
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional - for faster downloads
export HF_HUB_ENABLE_HF_TRANSFER=1
```

### Make Permanent (macOS/Linux)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# GitHub
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# HuggingFace
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

---

## 5. Quick Reference

### GitHub Commands

```bash
# Clone repository
git clone https://github.com/AION-Analytics/market-sentiments.git

# Check status
git status

# Add files
git add .

# Commit
git commit -m "Your message"

# Push
git push origin main

# Pull latest changes
git pull origin main
```

### HuggingFace Commands

```bash
# Login
huggingface-cli login

# Upload model
huggingface-cli upload AION-Analytics/aion-sentiment-in-v1 ./models/aion-sentiment-in-v1

# Download model (Python)
from transformers import AutoModel
model = AutoModel.from_pretrained("AION-Analytics/aion-sentiment-in-v1")
```

### Package Installation

```bash
# Activate virtual environment
cd /Users/lokeshgupta/aion_open_source
source venv/bin/activate

# Install all packages
pip install aion-sentiment aion-sectormap aion-volweight aion-newsimpact

# Or install individually
pip install aion-sentiment
pip install aion-sectormap
pip install aion-volweight
pip install aion-newsimpact
```

---

## 6. Troubleshooting

### GitHub Authentication Failed

**Error:** `fatal: Authentication failed`

**Solution:**
1. Generate new PAT: https://github.com/settings/tokens
2. Update stored credentials:
   ```bash
   git config --global --unset credential.helper
   git config --global credential.helper osxkeychain
   git push
   # Enter new PAT when prompted
   ```

### HuggingFace Upload Failed

**Error:** `403 Forbidden: You don't have the rights`

**Solution:**
1. Check token has Write permission
2. Verify organization name is correct: `AION-Analytics` (not `aion-analytics`)
3. Regenerate token: https://huggingface.co/settings/tokens

### Model Download Failed

**Error:** `Repository Not Found`

**Solution:**
1. Check model URL: https://huggingface.co/AION-Analytics/aion-sentiment-in-v1
2. Verify you're logged in: `huggingface-cli whoami`
3. Login again: `huggingface-cli login`

### Virtual Environment Issues

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 7. Repository Links

| Platform | URL | Credentials |
|----------|-----|-------------|
| **GitHub** | https://github.com/AION-Analytics/market-sentiments | PAT (ghp_...) |
| **HuggingFace** | https://huggingface.co/AION-Analytics/aion-sentiment-in-v1 | HF Token (hf_...) |

---

## 8. Contact

- **Email:** aionlabs@tutamail.com
- **GitHub:** https://github.com/AION-Analytics
- **HuggingFace:** https://huggingface.co/AION-Analytics

---

*Last Updated: March 14, 2026*  
*AION Open-Source Project*
