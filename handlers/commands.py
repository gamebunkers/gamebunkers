import asyncio

from sqlalchemy import select
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from config import settings
from database import crud
from database.models import Game, GameStatus, Player, PlayerCard, PlayerStats
from game.actions import apply_special_action
from game.manager import GameManager
from handlers.game_handlers import schedule_round_flow
from utils import messages
from utils.keyboards import action_keyboard


def _chat_lock(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    return context.application.bot_data["chat_locks"].setdefault(chat_id, asyncio.Lock())


async def _close_join_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with context.application.bot_data["session_factory"]() as session:
        game = await crud.get_active_game_by_chat(session, chat_id)
        if not game or game.status != GameStatus.waiting:
            return
        await crud.set_game_status(session, game, GameStatus.finished)
    await context.bot.send_message(
        chat_id=chat_id,
        text="⌛ Qo'shilish vaqti tugadi. O'yin avtomatik yopildi. Qayta boshlash uchun /newgame",
    )


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("Salom! Bunker Botga xush kelibsiz.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(messages.help_text())


async def rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(messages.rules_text())


async def newgame_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await update.effective_message.reply_text("Bu buyruq faqat guruhda.")
        return

    lock = _chat_lock(context, update.effective_chat.id)
    async with lock:
        async with context.application.bot_data["session_factory"]() as session:
            game = await crud.get_active_game_by_chat(session, update.effective_chat.id)
            if game:
                await update.effective_message.reply_text("Bu chatda aktiv o'yin bor.")
                return
            gm = GameManager(session)
            await gm.create_game(
                update.effective_chat.id,
                update.effective_user.id,
                update.effective_user.username,
                update.effective_user.full_name,
            )
            await update.effective_message.reply_text(messages.game_created(update.effective_user.full_name))
            context.job_queue.run_once(
                lambda c: _close_join_phase(update.effective_chat.id, c),
                when=settings.join_timeout,
                name=f"join-timeout-{update.effective_chat.id}",
            )


async def join_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await update.effective_message.reply_text("Bu buyruq faqat guruhda.")
        return

    lock = _chat_lock(context, update.effective_chat.id)
    async with lock:
        async with context.application.bot_data["session_factory"]() as session:
            game = await crud.get_active_game_by_chat(session, update.effective_chat.id)
            if not game:
                await update.effective_message.reply_text("Aktiv o'yin yo'q")
                return
            try:
                gm = GameManager(session)
                await gm.join_game(game, update.effective_user.id, update.effective_user.username, update.effective_user.full_name)
                await update.effective_message.reply_text(messages.join_success(update.effective_user.full_name))
            except ValueError as exc:
                await update.effective_message.reply_text(str(exc))


async def players_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with context.application.bot_data["session_factory"]() as session:
        game = await crud.get_active_game_by_chat(session, update.effective_chat.id)
        if not game:
            await update.effective_message.reply_text("Aktiv o'yin yo'q")
            return
        players = await crud.get_game_players(session, game.id)
        await update.effective_message.reply_text("\n".join([f"- {p.full_name}{' (host)' if p.is_host else ''}" for p in players]))


async def begin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lock = _chat_lock(context, update.effective_chat.id)
    async with lock:
        async with context.application.bot_data["session_factory"]() as session:
            game = await crud.get_active_game_by_chat(session, update.effective_chat.id)
            if not game:
                await update.effective_message.reply_text("Aktiv o'yin yo'q")
                return
            if game.status != GameStatus.waiting:
                await update.effective_message.reply_text("O'yin allaqachon boshlangan.")
                return
            host = await crud.get_player(session, game.id, update.effective_user.id)
            if not host or not host.is_host:
                await update.effective_message.reply_text("Faqat host boshlaydi")
                return
            scenarios = await crud.get_scenarios(session)
            gm = GameManager(session)
            players, scenario, capacity = await gm.start_game(game, scenarios)
            await update.effective_message.reply_text(messages.game_start_announcement(scenario, len(players), capacity))
            failed_dm = []
            me = await context.bot.get_me()
            for player in players:
                card = await session.get(PlayerCard, player.card_id)
                try:
                    await context.bot.send_message(chat_id=player.user_id, text=messages.card_message(card))
                except Exception:
                    failed_dm.append(player.full_name)
            if failed_dm:
                await update.effective_message.reply_text(
                    f"⚠️ Bu o'yinchilar DM ololmadi: {', '.join(failed_dm)}. @{me.username} ga /start yozsin."
                )

    await schedule_round_flow(update.effective_chat.id, context)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with context.application.bot_data["session_factory"]() as session:
        game = await crud.get_active_game_by_chat(session, update.effective_chat.id)
        if not game:
            await update.effective_message.reply_text("Aktiv o'yin yo'q")
            return
        alive = await crud.get_game_players(session, game.id, alive_only=True)
        await update.effective_message.reply_text(
            f"Status: {game.status.value}, Raund: {game.current_round}, Tirik: {len(alive)}, Sig'im: {game.bunker_capacity}"
        )


async def endgame_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with context.application.bot_data["session_factory"]() as session:
        game = await crud.get_active_game_by_chat(session, update.effective_chat.id)
        if not game:
            await update.effective_message.reply_text("Aktiv o'yin yo'q")
            return
        player = await crud.get_player(session, game.id, update.effective_user.id)
        if not player and update.effective_user.id not in settings.admin_user_ids:
            await update.effective_message.reply_text("Ruxsat yo'q")
            return
        if player and not player.is_host and update.effective_user.id not in settings.admin_user_ids:
            await update.effective_message.reply_text("Faqat host yoki admin")
            return
        await crud.set_game_status(session, game, GameStatus.finished)
        await update.effective_message.reply_text("O'yin tugatildi")


async def card_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != ChatType.PRIVATE:
        await update.effective_message.reply_text("/card private chatda")
        return
    async with context.application.bot_data["session_factory"]() as session:
        player = await session.scalar(
            select(Player).where(Player.user_id == update.effective_user.id, Player.is_alive.is_(True)).order_by(Player.joined_at.desc())
        )
        if not player:
            await update.effective_message.reply_text("Aktiv kartangiz yo'q")
            return
        card = await session.get(PlayerCard, player.card_id)
        await update.effective_message.reply_text(messages.card_message(card))


async def reveal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != ChatType.PRIVATE:
        await update.effective_message.reply_text("/reveal private chatda")
        return
    if not context.args:
        await update.effective_message.reply_text("/reveal health kabi yozing")
        return
    attr = context.args[0].strip().lower()
    allowed = {
        "profession": "profession_revealed",
        "health": "health_revealed",
        "hobby": "hobby_revealed",
        "luggage": "luggage_revealed",
        "trait": "trait_revealed",
        "phobia": "phobia_revealed",
    }
    if attr not in allowed:
        await update.effective_message.reply_text("Noto'g'ri atribut")
        return
    async with context.application.bot_data["session_factory"]() as session:
        player = await session.scalar(
            select(Player).where(Player.user_id == update.effective_user.id, Player.is_alive.is_(True)).order_by(Player.joined_at.desc())
        )
        if not player:
            await update.effective_message.reply_text("Aktiv o'yin yo'q")
            return
        card = await session.get(PlayerCard, player.card_id)
        setattr(card, allowed[attr], True)
        await session.commit()
        await update.effective_message.reply_text("✅ Atribut ochildi")


async def action_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != ChatType.PRIVATE:
        await update.effective_message.reply_text("/action private chatda")
        return
    async with context.application.bot_data["session_factory"]() as session:
        player = await session.scalar(
            select(Player).where(Player.user_id == update.effective_user.id, Player.is_alive.is_(True)).order_by(Player.joined_at.desc())
        )
        if not player:
            await update.effective_message.reply_text("Aktiv o'yin topilmadi")
            return
        game = await session.get(Game, player.game_id)
        if not game or game.status != GameStatus.voting:
            await update.effective_message.reply_text("Maxsus harakat faqat ovoz berish bosqichida ishlaydi.")
            return
        if player.special_action_used:
            await update.effective_message.reply_text("Siz maxsus harakatni allaqachon ishlatgansiz")
            return
        card = await session.get(PlayerCard, player.card_id)
        await update.effective_message.reply_text(
            f"Maxsus harakatingiz: {card.special_action}",
            reply_markup=action_keyboard(card.special_action),
        )


async def action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not query.data:
        return

    if query.data == "action_cancel":
        await query.edit_message_text("Bekor qilindi")
        return

    if not query.data.startswith("action_confirm:"):
        return

    action_name = query.data.split(":", 1)[1]
    async with context.application.bot_data["session_factory"]() as session:
        player = await session.scalar(
            select(Player).where(Player.user_id == query.from_user.id, Player.is_alive.is_(True)).order_by(Player.joined_at.desc())
        )
        if not player:
            await query.edit_message_text("Aktiv o'yin topilmadi")
            return
        game = await session.get(Game, player.game_id)
        if not game or game.status != GameStatus.voting:
            await query.edit_message_text("Action faqat ovoz bosqichida ishlaydi.")
            return
        if player.special_action_used:
            await query.edit_message_text("Siz bu actionni avval ishlatgansiz")
            return

        result = await apply_special_action(action_name, session, player, game)
        if result.success:
            await crud.set_player_action_used(session, player, True)
            await crud.increase_special_actions(session, player.user_id)

    prefix = "✅" if result.success else "❌"
    await query.edit_message_text(f"{prefix} {result.message}")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with context.application.bot_data["session_factory"]() as session:
        stats = await session.scalar(select(PlayerStats).where(PlayerStats.user_id == update.effective_user.id))
        if not stats:
            await update.effective_message.reply_text("Statistika yo'q")
            return
        await update.effective_message.reply_text(
            f"📊 O'yinlar: {stats.total_games}\n🏆 G'alaba: {stats.wins}\n❌ Chiqarilgan: {stats.eliminations}\n⚡ Action: {stats.special_actions_used}"
        )
