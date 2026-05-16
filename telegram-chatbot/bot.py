import os
import asyncio
import logging
import threading
import torch
from flask import Flask
from transformers import AutoModelForCausalLM, AutoTokenizer
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ DialoGPT Telegram Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=7860)

MODEL_NAME = "microsoft/DialoGPT-medium"
logger.info(f"Loading model: {MODEL_NAME} ...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()
logger.info("✅ Model loaded!")

user_histories: dict[int, list] = {}
MAX_HISTORY_TURNS = 5


def generate_response(user_id: int, user_text: str) -> str:
    history = user_histories.get(user_id, [])

    new_ids = tokenizer.encode(
        user_text + tokenizer.eos_token,
        return_tensors="pt"
    )

    if len(history) > MAX_HISTORY_TURNS:
        history = history[-MAX_HISTORY_TURNS:]

    bot_input_ids = (
        torch.cat([*history, new_ids], dim=-1) if history else new_ids
    )

    with torch.no_grad():
        output_ids = model.generate(
            bot_input_ids,
            max_length=1000,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.75,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.3,
        )

    response_ids  = output_ids[:, bot_input_ids.shape[-1]:]
    response_text = tokenizer.decode(response_ids[0], skip_special_tokens=True).strip()

    history.append(output_ids)
    user_histories[user_id] = history

    return response_text or "Could you rephrase that? I want to make sure I understand!"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text(
        "👋 Hello! I'm your AI assistant powered by DialoGPT.\n"
        "Ask me anything! Type /reset to start fresh."
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text("🔄 Conversation reset! Let's start fresh.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *DialoGPT Chatbot*\n\n"
        "/start — Start conversation\n"
        "/reset — Clear history\n"
        "/help  — Show this message\n\n"
        "Just type anything to chat!",
        parse_mode="Markdown",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id   = update.effective_user.id
    user_text = update.message.text.strip()

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    reply = await asyncio.to_thread(generate_response, user_id, user_text)
    await update.message.reply_text(reply)


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN secret not set in HF Spaces!")

    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    logger.info("✅ Flask server started on port 7860")

    app = (
        ApplicationBuilder()
        .token(token)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help",  help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Telegram bot is polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
