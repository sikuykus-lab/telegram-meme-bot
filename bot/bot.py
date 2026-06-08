"""
Telegram-бот «предложка» для мемов.
Пользователь шлёт картинку/видео и текст — админу приходит медиа и подпись с именем автора.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "YOUR_ADMIN_USERNAME").lstrip("@").lower()
ADMIN_CHAT_ID_FILE = Path(__file__).resolve().parent / "admin_chat_id.txt"


def display_name(user) -> str:
    """Имя, как его видят в Telegram (не @ник)."""
    parts = [user.first_name or "", user.last_name or ""]
    name = " ".join(p for p in parts if p).strip()
    return name or "Без имени"


def build_caption(text: str | None, author: str) -> str:
    lines: list[str] = []
    if text and text.strip():
        lines.append(text.strip())
    lines.append(f"Автор: {author}")
    return "\n\n".join(lines)


def load_admin_chat_id() -> int | None:
    if not ADMIN_CHAT_ID_FILE.exists():
        return None
    raw = ADMIN_CHAT_ID_FILE.read_text(encoding="utf-8").strip()
    if raw.isdigit():
        return int(raw)
    return None


def save_admin_chat_id(chat_id: int) -> None:
    ADMIN_CHAT_ID_FILE.write_text(str(chat_id), encoding="utf-8")


def is_admin_user(user) -> bool:
    if not user or not user.username:
        return False
    return user.username.lower() == ADMIN_USERNAME


async def ensure_admin_registered(update: Update) -> int | None:
    user = update.effective_user
    if user and is_admin_user(user):
        save_admin_chat_id(update.effective_chat.id)
        return update.effective_chat.id
    return load_admin_chat_id()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user and is_admin_user(user):
        save_admin_chat_id(update.effective_chat.id)
        await update.message.reply_text(
            "Вы зарегистрированы как админ. Сюда будут приходить предложки.\n"
            "Пользователи пишут этому боту — вы копируете пост в канал вручную."
        )
        return

    await update.message.reply_text(
        "Здаров, ебана\n\n"
        "Это моя предложка. Кидай сюда свой мемас и если он мне понравится, "
        "я его опубликую. Можешь подписать сообщение чтоб смешнее было.\n\n"
        "Твоё имя будет отображаться в посте на канале "
        "(не ссылка, а просто имя)"
    )


async def send_to_admin(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    chat_id: int,
    caption: str,
    photo_id: str | None = None,
    video_id: str | None = None,
    animation_id: str | None = None,
    document_id: str | None = None,
    text_only: str | None = None,
) -> None:
    if photo_id:
        await context.bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption)
    elif video_id:
        await context.bot.send_video(chat_id=chat_id, video=video_id, caption=caption)
    elif animation_id:
        await context.bot.send_animation(
            chat_id=chat_id, animation=animation_id, caption=caption
        )
    elif document_id:
        await context.bot.send_document(
            chat_id=chat_id, document=document_id, caption=caption
        )
    elif text_only:
        await context.bot.send_message(chat_id=chat_id, text=caption)
    else:
        await context.bot.send_message(chat_id=chat_id, text=caption)


async def handle_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    user = message.from_user
    if user and is_admin_user(user):
        return

    admin_id = await ensure_admin_registered(update)
    if admin_id is None:
        admin_id = load_admin_chat_id()

    if admin_id is None:
        await message.reply_text(
            "Бот ещё не настроен: админ должен один раз написать боту /start."
        )
        return

    author = display_name(user)
    user_text = message.caption or message.text
    caption = build_caption(user_text, author)

    try:
        if message.photo:
            await send_to_admin(
                context,
                chat_id=admin_id,
                caption=caption,
                photo_id=message.photo[-1].file_id,
            )
        elif message.video:
            await send_to_admin(
                context,
                chat_id=admin_id,
                caption=caption,
                video_id=message.video.file_id,
            )
        elif message.animation:
            await send_to_admin(
                context,
                chat_id=admin_id,
                caption=caption,
                animation_id=message.animation.file_id,
            )
        elif message.document and message.document.mime_type and message.document.mime_type.startswith(
            "image/"
        ):
            await send_to_admin(
                context,
                chat_id=admin_id,
                caption=caption,
                document_id=message.document.file_id,
            )
        elif message.text and not message.text.startswith("/"):
            await send_to_admin(
                context, chat_id=admin_id, caption=caption, text_only=message.text
            )
        else:
            await message.reply_text(
                "Отправьте картинку, GIF, видео или текст. Другие форматы пока не принимаются."
            )
            return

        await message.reply_text(
            "Заебись, мем будет проверен и если он мне понравится - "
            "увидите его в канале)"
        )
    except Exception:
        logger.exception("Failed to forward submission to admin")
        await message.reply_text("Не удалось отправить. Попробуйте позже.")


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Задайте BOT_TOKEN в файле .env")

    app = (
        Application.builder()
        .token(token)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(
        MessageHandler(
            filters.PHOTO
            | filters.VIDEO
            | filters.ANIMATION
            | filters.Document.IMAGE
            | (filters.TEXT & ~filters.COMMAND),
            handle_submission,
        )
    )

    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
