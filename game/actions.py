import random

from database import crud
from database.models import PlayerCard
from game.cards import generate_card
from game.models import ActionResult


async def apply_special_action(action_name: str, session, player, game) -> ActionResult:
    if action_name == "🛡️ Immunitet":
        await crud.set_player_immunity(session, player, True)
        return ActionResult(success=True, message="Immunitet ushbu ovoz bosqichida yoqildi.")

    if action_name == "🔄 Karta almashtirish":
        card = await session.get(PlayerCard, player.card_id)
        new_data = generate_card()
        for key, value in new_data.items():
            setattr(card, key, value)
        await session.commit()
        return ActionResult(success=True, message="Kartangiz yangilandi.")

    if action_name == "🔍 Razvedka":
        targets = [p for p in await crud.get_game_players(session, game.id, alive_only=True) if p.id != player.id]
        if not targets:
            return ActionResult(success=False, message="Razvedka uchun mos o'yinchi yo'q.")
        t = random.choice(targets)
        card = await session.get(PlayerCard, t.card_id)
        return ActionResult(success=True, message=f"Razvedka: {t.full_name} -> {card.profession}, {card.health}, {card.trait}")

    if action_name == "📢 Fosh qilish":
        targets = [p for p in await crud.get_game_players(session, game.id, alive_only=True) if p.id != player.id]
        if not targets:
            return ActionResult(success=False, message="Fosh qilish uchun nishon yo'q.")
        t = random.choice(targets)
        card = await session.get(PlayerCard, t.card_id)
        return ActionResult(success=True, message=f"Fosh: {t.full_name} kasbi — {card.profession}")

    if action_name == "🔄 Ovoz bekor":
        removed = await crud.cancel_vote(session, game.id, game.current_round, player.id)
        if not removed:
            return ActionResult(success=False, message="Bekor qilish uchun sizning ovozingiz topilmadi.")
        return ActionResult(success=True, message="Sizning ovozingiz bekor qilindi.")

    if action_name == "🗣️ Extra vaqt":
        return ActionResult(success=True, message="Extra vaqt yoqildi (+30s) va moderatorga xabar berildi.")

    return ActionResult(success=True, message=f"{action_name} ishlatildi")
