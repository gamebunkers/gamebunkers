import datetime as dt

from sqlalchemy import Select, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Game, GameScenario, GameStatus, Player, PlayerCard, PlayerStats, Vote


async def get_active_game_by_chat(session: AsyncSession, chat_id: int) -> Game | None:
    stmt: Select[tuple[Game]] = select(Game).where(
        Game.chat_id == chat_id,
        Game.status.in_([GameStatus.waiting, GameStatus.active, GameStatus.voting]),
    )
    return await session.scalar(stmt)


async def create_game(session: AsyncSession, chat_id: int, host_user_id: int, game_code: str) -> Game:
    game = Game(chat_id=chat_id, host_user_id=host_user_id, game_code=game_code, status=GameStatus.waiting)
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return game


async def add_player(
    session: AsyncSession,
    game_id: int,
    user_id: int,
    username: str | None,
    full_name: str,
    is_host: bool = False,
) -> Player:
    player = Player(game_id=game_id, user_id=user_id, username=username, full_name=full_name, is_host=is_host)
    session.add(player)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        existing = await get_player(session, game_id, user_id)
        if existing:
            return existing
        raise
    await session.refresh(player)
    return player


async def get_game_players(session: AsyncSession, game_id: int, alive_only: bool = False) -> list[Player]:
    stmt = select(Player).where(Player.game_id == game_id)
    if alive_only:
        stmt = stmt.where(Player.is_alive.is_(True))
    return list(await session.scalars(stmt.order_by(Player.joined_at.asc())))


async def get_player(session: AsyncSession, game_id: int, user_id: int) -> Player | None:
    return await session.scalar(select(Player).where(Player.game_id == game_id, Player.user_id == user_id))


async def get_player_by_id(session: AsyncSession, player_id: int) -> Player | None:
    return await session.scalar(select(Player).where(Player.id == player_id))


async def assign_card(session: AsyncSession, player: Player, card_data: dict) -> PlayerCard:
    card = PlayerCard(player_id=player.id, **card_data)
    session.add(card)
    await session.flush()
    player.card_id = card.id
    await session.commit()
    await session.refresh(card)
    return card


async def set_game_started(session: AsyncSession, game: Game, scenario_id: int, bunker_capacity: int) -> None:
    game.status = GameStatus.active
    game.scenario_id = scenario_id
    game.bunker_capacity = bunker_capacity
    game.current_round = 1
    game.started_at = dt.datetime.utcnow()
    await session.commit()


async def set_game_status(session: AsyncSession, game: Game, status: GameStatus) -> None:
    game.status = status
    if status == GameStatus.finished:
        game.finished_at = dt.datetime.utcnow()
    await session.commit()


async def increment_round(session: AsyncSession, game: Game) -> None:
    game.current_round += 1
    await session.commit()


async def record_vote(session: AsyncSession, game_id: int, round_number: int, voter_id: int, target_id: int) -> Vote:
    vote = Vote(game_id=game_id, round_number=round_number, voter_id=voter_id, target_id=target_id)
    session.add(vote)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Bu raundda allaqachon ovoz bergansiz")
    await session.refresh(vote)
    return vote


async def get_round_votes(session: AsyncSession, game_id: int, round_number: int) -> list[Vote]:
    return list(await session.scalars(select(Vote).where(Vote.game_id == game_id, Vote.round_number == round_number)))


async def clear_round_votes(session: AsyncSession, game_id: int, round_number: int) -> None:
    await session.execute(delete(Vote).where(Vote.game_id == game_id, Vote.round_number == round_number))
    await session.commit()


async def cancel_vote(session: AsyncSession, game_id: int, round_number: int, voter_id: int) -> bool:
    result = await session.execute(
        delete(Vote).where(Vote.game_id == game_id, Vote.round_number == round_number, Vote.voter_id == voter_id)
    )
    await session.commit()
    return (result.rowcount or 0) > 0


async def set_player_action_used(session: AsyncSession, player: Player, used: bool = True) -> None:
    player.special_action_used = used
    await session.commit()


async def set_player_immunity(session: AsyncSession, player: Player, is_immune: bool) -> None:
    player.is_immune = is_immune
    await session.commit()


async def clear_round_immunity(session: AsyncSession, game_id: int) -> None:
    players = await get_game_players(session, game_id, alive_only=True)
    for p in players:
        p.is_immune = False
    await session.commit()


async def transfer_host_if_needed(session: AsyncSession, game: Game) -> Player | None:
    host = await get_player(session, game.id, game.host_user_id)
    if host and host.is_alive:
        return host
    alive = await get_game_players(session, game.id, alive_only=True)
    if not alive:
        return None
    for p in await get_game_players(session, game.id):
        p.is_host = False
    new_host = alive[0]
    new_host.is_host = True
    game.host_user_id = new_host.user_id
    await session.commit()
    return new_host


async def eliminate_player(session: AsyncSession, player: Player, round_number: int) -> None:
    player.is_alive = False
    player.elimination_round = round_number
    await session.commit()


async def get_or_create_stats(session: AsyncSession, user_id: int) -> PlayerStats:
    stats = await session.scalar(select(PlayerStats).where(PlayerStats.user_id == user_id))
    if stats:
        return stats
    stats = PlayerStats(user_id=user_id)
    session.add(stats)
    await session.commit()
    await session.refresh(stats)
    return stats


async def increase_total_games(session: AsyncSession, user_ids: list[int]) -> None:
    for uid in user_ids:
        stats = await get_or_create_stats(session, uid)
        stats.total_games += 1
    await session.commit()


async def increase_wins(session: AsyncSession, user_ids: list[int]) -> None:
    for uid in user_ids:
        stats = await get_or_create_stats(session, uid)
        stats.wins += 1
    await session.commit()


async def increase_eliminations(session: AsyncSession, user_id: int) -> None:
    stats = await get_or_create_stats(session, user_id)
    stats.eliminations += 1
    await session.commit()


async def increase_special_actions(session: AsyncSession, user_id: int) -> None:
    stats = await get_or_create_stats(session, user_id)
    stats.special_actions_used += 1
    await session.commit()


async def get_scenarios(session: AsyncSession) -> list[GameScenario]:
    return list(await session.scalars(select(GameScenario).order_by(GameScenario.id.asc())))


async def get_scenario_by_id(session: AsyncSession, scenario_id: int) -> GameScenario | None:
    return await session.get(GameScenario, scenario_id)


async def seed_scenarios_if_empty(session: AsyncSession, scenarios: list[dict]) -> None:
    count = await session.scalar(select(func.count()).select_from(GameScenario))
    if count and count > 0:
        return
    session.add_all(GameScenario(**s) for s in scenarios)
    await session.commit()
