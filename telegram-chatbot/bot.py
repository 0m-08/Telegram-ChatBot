# ─────────────────────────────────────────────────────────────────────────────
#  DialoGPT Telegram Chatbot
#  Model  : microsoft/DialoGPT-medium (Hugging Face)
#  Host   : Render (free tier)
#  Library: python-telegram-bot v20
# ─────────────────────────────────────────────────────────────────────────────

import os
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Load pre-trained transformer model from Hugging Face ─────────────────────
MODEL_NAME = "microsoft/DialoGPT-medium"

logger.info(f"Loading model: {MODEL_NAME} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()
logger.info("Model loaded successfully!")

# ── In-memory conversation history (per user) ─────────────────────────────────
# Key  : telegram user_id (int)
# Value: list of past output token tensors (for multi-turn context)
user_histories: dict[int, list] = {}
MAX_HISTORY_TURNS = 5   # Keep last 5 turns to stay within 1024-token limit


# ── Core response generation ──────────────────────────────────────────────────
def generate_response(user_id: int, user_text: str) -> str:
    """
    Tokenize user_text, append to per-user history, run DialoGPT inference,
    decode and return the bot's reply.
    """
    history = user_histories.get(user_id, [])

    # Step 1: Tokenize new user input (add EOS separator between turns)
    new_ids = tokenizer.encode(
        user_text + tokenizer.eos_token,
        return_tensors="pt"
    )

    # Step 2: Trim history to avoid exceeding context window
    if len(history) > MAX_HISTORY_TURNS:
        history = history[-MAX_HISTORY_TURNS:]

    # Step 3: Build full context tensor (history + new input)
    bot_input_ids = (
        torch.cat([*history, new_ids], dim=-1) if history else new_ids
    )

    # Step 4: Generate response using the transformer model
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

    # Step 5: Decode only the newly generated tokens (skip the prompt)
    response_ids  = output_ids[:, bot_input_ids.shape[-1]:]
    response_text = tokenizer.decode(response_ids[0], skip_special_tokens=True).strip()

    # Step 6: Update per-user history
    history.append(output_ids)
    user_histories[user_id] = history

    return response_text or "Could you rephrase that? I want to make sure I understand you."


# ── Telegram command handlers ─────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — greet the user and reset their history."""
    user_id = update.effective_user.id
    user_histories[user_id] = []          # Fresh conversation

    await update.message.reply_text(
        "👋 Hello! I'm your AI assistant powered by DialoGPT.\n\n"
        "Ask me anything — I'll do my best to respond!\n"
        "Type /reset anytime to start a fresh conversation."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/reset — clear conversation history for this user."""
    user_id = update.effective_user.id
    user_histories[user_id] = []

    await update.message.reply_text(
        "🔄 Conversation reset! Let's start fresh. What's on your mind?"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help — show available commands."""
    await update.message.reply_text(
        "🤖 *DialoGPT Chatbot Help*\n\n"
        "/start — Start a new conversation\n"
        "/reset — Clear conversation history\n"
        "/help  — Show this message\n\n"
        "Just send any message to chat!",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle every regular text message — generate and send bot reply."""
    user_id   = update.effective_user.id
    user_text = update.message.text.strip()

    logger.info(f"User {user_id}: {user_text}")

    # Show 'typing...' indicator while model runs
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    reply = generate_response(user_id, user_text)
    logger.info(f"Bot  → {reply}")

    await update.message.reply_text(reply)


# ── App entry point ───────────────────────────────────────────────────────────
def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

    app = ApplicationBuilder().token(token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help",  help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running... Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
