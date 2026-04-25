import asyncio
import logging
import signal
from contextlib import suppress

from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ChatMemberHandler, CommandHandler, ContextTypes

from config import settings
from database import crud
from database.db import SessionLocal, init_db
from database import models as db_models
from game.manager import GameManager
from game.scenarios import SCENARIOS
from handlers import admin_handlers, commands, game_handlers, voting_handlers
from utils import keyboards, messages

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("bunker-bot")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error: %s", context.error)


async def health(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def run_web() -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", settings.port)
    await site.start()
    return runner


async def build_app() -> Application:
    app = Application.builder().token(settings.bot_token).build()
    app.bot_data["session_factory"] = SessionLocal
    app.bot_data["crud"] = crud
    app.bot_data["manager_factory"] = lambda session: GameManager(session)
    app.bot_data["chat_locks"] = {}
    app.bot_data["settings"] = settings
    app.bot_data["keyboards"] = keyboards
    app.bot_data["messages"] = messages
    app.bot_data["models"] = db_models

    app.add_handler(CommandHandler("start", commands.start_cmd))
    app.add_handler(CommandHandler("help", commands.help_cmd))
    app.add_handler(CommandHandler("rules", commands.rules_cmd))
    app.add_handler(CommandHandler("stats", commands.stats_cmd))
    app.add_handler(CommandHandler("newgame", commands.newgame_cmd))
    app.add_handler(CommandHandler("join", commands.join_cmd))
    app.add_handler(CommandHandler("players", commands.players_cmd))
    app.add_handler(CommandHandler("begin", commands.begin_cmd))
    app.add_handler(CommandHandler("status", commands.status_cmd))
    app.add_handler(CommandHandler("endgame", commands.endgame_cmd))
    app.add_handler(CommandHandler("card", commands.card_cmd))
    app.add_handler(CommandHandler("reveal", commands.reveal_cmd))
    app.add_handler(CommandHandler("action", commands.action_cmd))

    app.add_handler(CommandHandler("admin_games", admin_handlers.admin_games_cmd))
    app.add_handler(CommandHandler("admin_end", admin_handlers.admin_end_cmd))
    app.add_handler(CommandHandler("broadcast", admin_handlers.broadcast_cmd))

    app.add_handler(CallbackQueryHandler(voting_handlers.vote_callback, pattern=r"^vote:"))
    app.add_handler(CallbackQueryHandler(commands.action_callback, pattern=r"^action_"))
    app.add_handler(ChatMemberHandler(game_handlers.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    app.add_error_handler(error_handler)
    return app


async def bootstrap_data() -> None:
    async with SessionLocal() as session:
        await crud.seed_scenarios_if_empty(session, SCENARIOS)


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN kerak")

    await init_db()
    await bootstrap_data()

    app = await build_app()
    scheduler = AsyncIOScheduler()
    scheduler.start()

    await app.initialize()
    await app.start()

    runner = await run_web()

    stop_event = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            asyncio.get_running_loop().add_signal_handler(sig, stop_event.set)

    if settings.webhook_url:
        await app.bot.set_webhook(
            url=f"{settings.webhook_url}/telegram",
            secret_token=settings.webhook_secret or None,
            allowed_updates=Update.ALL_TYPES,
        )
        logger.info("Webhook mode")
    else:
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Polling mode")

    await stop_event.wait()

    scheduler.shutdown(wait=False)
    await app.stop()
    await app.shutdown()
    await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
