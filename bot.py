# demo_bot_ids.py
# Requires: python-telegram-bot==20.6+
# Install: python -m pip install python-telegram-bot==20.6

import os
import asyncio
import logging
from telegram import Update, MessageEntity
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8050773888:AAF_DoMdVcf8VsWhYVjugLkTqGRujmCwU1Y"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"Hello {user.first_name or 'there'}!\n\n"
        "This demo bot returns IDs for you, chats, groups, channels and forwarded messages.\n\n"
        "Commands:\n"
        "/myid - your Telegram user id\n"
        "/chatid - the current chat id (private/group/channel)\n\n"
        "Forward any message to me and I will show the original sender/chat IDs if available."
    )
    await update.message.reply_text(text)


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Your user id: `{user.id}`\nusername: @{user.username or 'N/A'}",
        parse_mode="Markdown",
    )


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    # show chat type, id and title (if any)
    title = getattr(chat, "title", None)
    await update.message.reply_text(
        f"Chat type: `{chat.type}`\nChat id: `{chat.id}`\nTitle: {title or 'N/A'}",
        parse_mode="Markdown",
    )


def _fmt(val):
    return str(val) if val is not None else "N/A"


async def forwarded_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg:
        return

    # Basic details about the message and where it was sent
    info_lines = [
        f"📬 Received a message in chat `{update.effective_chat.id}` (type: {update.effective_chat.type})",
        f"Message id in this chat: `{msg.message_id}`",
        "---- Forward metadata (if present) ----",
    ]

    # When a message is forwarded from a user (non-channel)
    if msg.forward_from:
        f = msg.forward_from
        info_lines.append("Forwarded from individual user:")
        info_lines.append(f"  forward_from.id: `{_fmt(f.id)}`")
        info_lines.append(f"  forward_from.username: @{_fmt(f.username)}")
        info_lines.append(f"  forward_from.first_name: {_fmt(f.first_name)}")
        info_lines.append(f"  forward_from.last_name: {_fmt(f.last_name)}")

    # When a message is forwarded from a channel or chat (supergroup/channel)
    if msg.forward_from_chat:
        fc = msg.forward_from_chat
        info_lines.append("Forwarded from chat (channel / group / supergroup):")
        info_lines.append(f"  forward_from_chat.id: `{_fmt(fc.id)}`")
        info_lines.append(f"  forward_from_chat.title: {_fmt(getattr(fc, 'title', None))}")
        info_lines.append(f"  forward_from_chat.type: {_fmt(fc.type)}")

    # forward_from_message_id: original message id within the source chat
    if msg.forward_from_message_id is not None:
        info_lines.append(f"forward_from_message_id (original message id): `{msg.forward_from_message_id}`")
    else:
        info_lines.append("forward_from_message_id: N/A")

    # Other forwarding metadata
    info_lines.append(f"forward_sender_name: {_fmt(msg.forward_sender_name)}")
    info_lines.append(f"forward_signature: {_fmt(msg.forward_signature)}")
    info_lines.append(f"forward_date (timestamp): {_fmt(msg.forward_date)}")

    # NOTE about privacy: forwarded messages may not always include forward_from (depends on source privacy)
    info_lines.append("\n⚠️ Note: `forward_from` may be missing for some forwards (e.g., if the sender disallows forwards or forwarded from certain private chats).")

    await update.message.reply_text("\n".join(info_lines), parse_mode="Markdown")


async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This handler triggers on any message. We use it to:
    - reply with forwarded metadata if message is forwarded
    - otherwise show the chat id when the user asks via plain text 'chatid' or sends /chatid
    """
    msg = update.message
    if not msg:
        return

    # If the message is a forwarded message, show detailed info.
    if msg.forward_date or msg.forward_from or msg.forward_from_chat:
        await forwarded_info(update, context)
        return

    # If the user types plain text 'chatid' (without slash), show chat id too
    text = (msg.text or "").strip().lower()
    if text in ("chatid", "id", "whereami"):
        await chatid(update, context)
        return

    # otherwise a small help hint
    await msg.reply_text("Send /myid or /chatid, or forward a message to me to see its original IDs.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)
    # Keep silent for users; log only


async def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("ERROR: Replace YOUR_BOT_TOKEN_HERE with your bot token or set TG_BOT_TOKEN env var.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("chatid", chatid))

    # catch-all messages
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, any_message))

    app.add_error_handler(error_handler)

    print("Demo bot started (polling). Ctrl+C to stop.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
