import logging
import random
import string

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import crud
from database.models import Game, GameStatus, Player
from game.cards import generate_card

logger = logging.getLogger(__name__)


class GameManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def generate_game_code() -> str:
        return "BNK-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

    async def create_game(self, chat_id: int, host_user_id: int, host_username: str | None, host_name: str) -> Game:
        game = await crud.create_game(self.session, chat_id, host_user_id, self.generate_game_code())
        await crud.add_player(self.session, game.id, host_user_id, host_username, host_name, is_host=True)
        logger.info("Game created %s", game.id)
        return game

    async def join_game(self, game: Game, user_id: int, username: str | None, full_name: str) -> Player:
        players = await crud.get_game_players(self.session, game.id)
        if len(players) >= settings.max_players:
            raise ValueError("O'yin to'lgan")
        if game.status != GameStatus.waiting:
            raise ValueError("O'yin allaqachon boshlangan")
        existing = await crud.get_player(self.session, game.id, user_id)
        if existing:
            return existing
        return await crud.add_player(self.session, game.id, user_id, username, full_name)

    async def start_game(self, game: Game, scenarios: list) -> tuple[list[Player], object, int]:
        players = await crud.get_game_players(self.session, game.id)
        if len(players) < settings.min_players:
            raise ValueError("Kamida 4 o'yinchi kerak")
        scenario = random.choice(scenarios)
        capacity = max(1, len(players) // 2)
        await crud.set_game_started(self.session, game, scenario.id, capacity)
        for player in players:
            await crud.assign_card(self.session, player, generate_card())
        await crud.increase_total_games(self.session, [p.user_id for p in players])
        return players, scenario, capacity

    async def finish_if_needed(self, game: Game) -> tuple[bool, list[Player]]:
        alive = await crud.get_game_players(self.session, game.id, alive_only=True)
        if len(alive) <= game.bunker_capacity and game.status != GameStatus.finished:
            await crud.set_game_status(self.session, game, GameStatus.finished)
            await crud.increase_wins(self.session, [p.user_id for p in alive])
            return True, alive
        return False, alive
