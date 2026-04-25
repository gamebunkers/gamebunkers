import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import crud
from database.models import GameStatus
from utils.keyboards import voting_keyboard

logger = logging.getLogger(__name__)


async def _send_countdown(chat_id: int, context: ContextTypes.DEFAULT_TYPE, phase: str, seconds_left: int) -> None:
    await context.bot.send_message(chat_id=chat_id, text=f"⏳ {phase}: {seconds_left} soniya qoldi")


def _schedule_countdowns(chat_id: int, context: ContextTypes.DEFAULT_TYPE, phase: str, duration: int) -> None:
    tick = settings.reminder_interval
    mark = duration - tick
    while mark > 0:
        context.job_queue.run_once(
            lambda c, s=mark: _send_countdown(chat_id, c, phase, s),
            when=duration - mark,
            name=f"{phase}-countdown-{chat_id}-{mark}",
        )
        mark -= tick


async def _start_voting_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with context.application.bot_data["session_factory"]() as session:
        game = await crud.get_active_game_by_chat(session, chat_id)
        if not game or game.status == GameStatus.finished:
            return
        game.status = GameStatus.voting
        await session.commit()
        players = await crud.get_game_players(session, game.id, alive_only=True)

    await context.bot.send_message(
        chat_id=chat_id,
        text="🗳️ Ovoz berish boshlandi! Kimni chiqaramiz?",
        reply_markup=voting_keyboard([(p.id, p.full_name) for p in players]),
    )
    _schedule_countdowns(chat_id, context, "Ovoz berish", settings.voting_timeout)

    from handlers.voting_handlers import finish_voting_phase

    context.job_queue.run_once(
        lambda c: finish_voting_phase(chat_id, c),
        when=settings.voting_timeout,
        name=f"finish-voting-{chat_id}",
    )


async def schedule_round_flow(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=chat_id, text="🧠 Muhokama boshlandi.")
    _schedule_countdowns(chat_id, context, "Muhokama", settings.discussion_timeout)

    context.job_queue.run_once(
        lambda c: _start_voting_phase(chat_id, c),
        when=settings.discussion_timeout,
        name=f"start-voting-{chat_id}",
    )
    logger.info("Round flow scheduled for chat_id=%s", chat_id)


async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    change = update.chat_member
    if not change:
        return
    old_status = change.old_chat_member.status
    new_status = change.new_chat_member.status
    if old_status == new_status:
        return
    if new_status not in ("left", "kicked"):
        return

    chat_id = change.chat.id
    user_id = change.new_chat_member.user.id

    async with context.application.bot_data["session_factory"]() as session:
        game = await crud.get_active_game_by_chat(session, chat_id)
        if not game:
            return
        player = await crud.get_player(session, game.id, user_id)
        if not player or not player.is_alive:
            return

        await crud.eliminate_player(session, player, game.current_round)
        await context.bot.send_message(chat_id=chat_id, text=f"🚪 {player.full_name} chatni tark etdi va o'yindan chiqarildi.")

        if player.is_host or game.host_user_id == user_id:
            new_host = await crud.transfer_host_if_needed(session, game)
            if new_host:
                await context.bot.send_message(chat_id=chat_id, text=f"👑 Yangi host: {new_host.full_name}")

        finished, winners = await context.application.bot_data["manager_factory"](session).finish_if_needed(game)
        if finished:
            await context.bot.send_message(chat_id=chat_id, text=f"🏆 O'yin tugadi. G'oliblar: {', '.join(w.full_name for w in winners)}")
