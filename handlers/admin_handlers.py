from sqlalchemy import select
from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database.models import Game, GameStatus


async def admin_games_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in settings.admin_user_ids:
        await update.effective_message.reply_text("Ruxsat yo'q")
        return
    async with context.application.bot_data["session_factory"]() as session:
        games = list(await session.scalars(select(Game).where(Game.status != GameStatus.finished)))
    await update.effective_message.reply_text("\n".join([f"#{g.id} chat={g.chat_id} status={g.status.value}" for g in games]) if games else "Aktiv o'yin yo'q")


async def admin_end_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in settings.admin_user_ids:
        await update.effective_message.reply_text("Ruxsat yo'q")
        return
    if not context.args:
        await update.effective_message.reply_text("/admin_end <game_id>")
        return
    game_id = int(context.args[0])
    async with context.application.bot_data["session_factory"]() as session:
        game = await session.get(Game, game_id)
        if not game:
            await update.effective_message.reply_text("Topilmadi")
            return
        game.status = GameStatus.finished
        await session.commit()
    await update.effective_message.reply_text("Tugatildi")


async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in settings.admin_user_ids:
        await update.effective_message.reply_text("Ruxsat yo'q")
        return
    await update.effective_message.reply_text("Broadcast funksiyasi tayyorlandi")
