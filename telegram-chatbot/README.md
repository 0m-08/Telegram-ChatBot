# DialoGPT Telegram Chatbot

A conversational AI Telegram bot powered by `microsoft/DialoGPT-medium`
from Hugging Face Transformers, deployed on Render (free tier).

---

## Project Structure

```
telegram-chatbot/
├── bot.py            ← Main bot code (model + Telegram handlers)
├── requirements.txt  ← Python dependencies
├── render.yaml       ← Render deployment config
└── README.md
```

---

## Deployment Guide (Step by Step)

### Step 1 — Create your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name: e.g. `DialoGPT Assistant`
4. Choose a username: e.g. `my_dialogpt_bot` (must end in `bot`)
5. BotFather gives you a token like:
   ```
        7958476702:YOUR_TOKEN   ```
   **Save this token — you'll need it in Step 3.**

---

### Step 2 — Push code to GitHub

```bash
# In your project folder
git init
git add .
git commit -m "DialoGPT Telegram bot"

# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/dialogpt-telegram-bot.git
git push -u origin main
```

---

### Step 3 — Deploy on Render

1. Go to **https://render.com** → Sign up (free)
2. Click **"New +"** → **"Background Worker"**
3. Connect your GitHub account → Select your repo
4. Render auto-detects `render.yaml` — confirm settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Scroll to **Environment Variables** → Add:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: *(paste your token from Step 1)*
6. Click **"Create Background Worker"**
7. Wait ~5 minutes for the build to complete (model download included)

---

### Step 4 — Test your bot

1. Open Telegram → search your bot username
2. Send `/start`
3. Start chatting! 🎉

---

## 💬 Available Commands

| Command  | Description                        |
|----------|------------------------------------|
| `/start` | Start a new conversation           |
| `/reset` | Clear conversation history         |
| `/help`  | Show help message                  |
| Any text | Chat with DialoGPT                 |

---

## ⚙️ How It Works

```
User message (Telegram)
        ↓
Tokenizer encodes text → token IDs
        ↓
Concatenate with conversation history
        ↓
DialoGPT model generates next tokens
        ↓
Decode new tokens → response text
        ↓
Send reply back to Telegram
```

---

## ⚠️ Render Free Tier Notes

- **Cold starts**: If no messages for 15 min, the service sleeps.
  First message after sleep takes ~30 seconds to respond.
- **RAM**: Free tier has 512 MB — DialoGPT-medium uses ~400 MB, so it fits.
- **No GPU**: Runs on CPU. Response time: 3–8 seconds per message.

---

## 🛠️ Local Testing (before deploying)

```bash
# Install dependencies
pip install -r requirements.txt

# Set your token (Windows PowerShell)
$env:TELEGRAM_BOT_TOKEN = "your_token_here"

# Set your token (Mac/Linux)
export TELEGRAM_BOT_TOKEN="your_token_here"

# Run the bot
python bot.py
```

---

## 📦 Tech Stack

| Component     | Technology                          |
|---------------|-------------------------------------|
| AI Model      | microsoft/DialoGPT-medium           |
| Framework     | Hugging Face Transformers + PyTorch |
| Bot Library   | python-telegram-bot v20             |
| Hosting       | Render (free background worker)     |
