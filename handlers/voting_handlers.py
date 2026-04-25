import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from database import crud
from database.models import GameStatus
from game.voting import resolve_votes
from handlers.game_handlers import schedule_round_flow

logger = logging.getLogger(__name__)


def _chat_lock(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    return context.application.bot_data["chat_locks"].setdefault(chat_id, asyncio.Lock())


async def vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.startswith("vote:"):
        return

    target_player_id = int(query.data.split(":", 1)[1])

    lock = _chat_lock(context, query.message.chat.id)
    async with lock:
        async with context.application.bot_data["session_factory"]() as session:
            game = await crud.get_active_game_by_chat(session, query.message.chat.id)
            if not game or game.status != GameStatus.voting:
                await query.answer("Hozir ovoz berish bosqichi emas", show_alert=True)
                return

            voter = await crud.get_player(session, game.id, query.from_user.id)
            if not voter or not voter.is_alive:
                await query.answer("Siz ovoz bera olmaysiz", show_alert=True)
                return

            target = await crud.get_player_by_id(session, target_player_id)
            if not target or target.game_id != game.id or not target.is_alive:
                await query.answer("Noto'g'ri nomzod", show_alert=True)
                return
            if target.is_immune:
                await query.answer("Bu o'yinchi ushbu raundda immunitetga ega.", show_alert=True)
                return

            votes = await crud.get_round_votes(session, game.id, game.current_round)
            if any(v.voter_id == voter.id for v in votes):
                await query.answer("Siz allaqachon ovoz bergansiz", show_alert=True)
                return

            if voter.id == target_player_id:
                await query.answer("O'zingizga ovoz bera olmaysiz", show_alert=True)
                return

            try:
                await crud.record_vote(session, game.id, game.current_round, voter.id, target_player_id)
            except ValueError as exc:
                await query.answer(str(exc), show_alert=True)
                return
            await query.answer("✅ Ovoz qabul qilindi")


async def finish_voting_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    lock = _chat_lock(context, chat_id)
    async with lock:
        async with context.application.bot_data["session_factory"]() as session:
            game = await crud.get_active_game_by_chat(session, chat_id)
            if not game or game.status != GameStatus.voting:
                return

            votes = await crud.get_round_votes(session, game.id, game.current_round)
            result = resolve_votes([(v.voter_id, v.target_id) for v in votes])

            if result.tied_player_ids:
                await context.bot.send_message(chat_id=chat_id, text="⚖️ Teng ovoz! Qayta ovoz berish boshlanadi.")
                await crud.clear_round_votes(session, game.id, game.current_round)
                game.status = GameStatus.voting
                await session.commit()
                alive = await crud.get_game_players(session, game.id, alive_only=True)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="🗳️ Qayta ovoz berish: kimni chiqaramiz?",
                    reply_markup=context.application.bot_data["keyboards"].voting_keyboard([(p.id, p.full_name) for p in alive]),
                )
                context.job_queue.run_once(
                    lambda c: finish_voting_phase(chat_id, c),
                    when=context.application.bot_data["settings"].voting_timeout,
                    name=f"revote-finish-{chat_id}",
                )
                return

            if result.eliminated_player_id is None:
                await context.bot.send_message(chat_id=chat_id, text="Ovozlar yetarli emas. Raund qayta boshlanadi.")
                await crud.clear_round_votes(session, game.id, game.current_round)
                game.status = GameStatus.active
                await session.commit()
                await schedule_round_flow(chat_id, context)
                return

            eliminated = await crud.get_player_by_id(session, result.eliminated_player_id)
            if not eliminated:
                return

            await crud.eliminate_player(session, eliminated, game.current_round)
            await crud.increase_eliminations(session, eliminated.user_id)
            await crud.increment_round(session, game)

            card = await session.get(context.application.bot_data["models"].PlayerCard, eliminated.card_id)
            full_card = context.application.bot_data["messages"].card_message(card)
            await context.bot.send_message(chat_id=chat_id, text=f"😔 {eliminated.full_name} chiqarildi!\n\n{full_card}")

            finished, winners = await context.application.bot_data["manager_factory"](session).finish_if_needed(game)
            if finished:
                await context.bot.send_message(chat_id=chat_id, text=f"🏆 O'yin tugadi. G'oliblar: {', '.join(w.full_name for w in winners)}")
                return

            await crud.clear_round_immunity(session, game.id)
            game.status = GameStatus.active
            await session.commit()

    await schedule_round_flow(chat_id, context)
    logger.info("Next round scheduled chat_id=%s", chat_id)
