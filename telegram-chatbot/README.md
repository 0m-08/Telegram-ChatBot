---
title: DialoGPT Telegram Bot
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# DialoGPT Telegram Chatbot

A conversational AI Telegram bot powered by `microsoft/DialoGPT-medium`,
hosted for free on Hugging Face Spaces.

---

## Deployment Steps

### Step 1 — Get your Telegram Bot Token
1. Open Telegram → search **@BotFather**
2. Send `/newbot` → follow prompts
3. Copy the token (looks like `7412365890:AAFxyz...`)

### Step 2 — Create a Hugging Face Space
1. Go to **https://huggingface.co** → Sign up / Log in
2. Click your profile → **"New Space"**
3. Fill in:
   - **Space name:** `dialogpt-telegram-bot`
   - **SDK:** choose **Docker**
   - **Visibility:** Public (free) or Private
4. Click **"Create Space"**

### Step 3 — Add your Bot Token as a Secret
1. Inside your Space → go to **Settings** tab
2. Scroll to **"Repository Secrets"**
3. Click **"New Secret"**:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: *(paste your token)*
4. Click **Save**

### Step 4 — Upload your files
Upload these 3 files to your Space (drag & drop or via Git):
- `bot.py`
- `requirements.txt`
- `Dockerfile`

### Step 5 — Wait for build
HF Spaces will automatically build and start your bot (~3–5 min).
Once the Space shows **"Running"** ✅, your bot is live!

### Step 6 — Test it
Open Telegram → find your bot → send `/start` → chat away! 🎉

---

## How It Works
- A tiny **Flask server** runs on port 7860 (required by HF Spaces to stay alive)
- The **Telegram bot** runs in the main thread alongside Flask
- DialoGPT generates all responses dynamically — no hardcoded answers

---

## Bot Commands
| Command | Action |
|---------|--------|
| `/start` | Start a new conversation |
| `/reset` | Clear conversation history |
| `/help` | Show help |
| Any message | Chat with DialoGPT |
