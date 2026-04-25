import datetime as dt
import enum

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class GameStatus(str, enum.Enum):
    waiting = "waiting"
    active = "active"
    voting = "voting"
    finished = "finished"


class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    game_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus), default=GameStatus.waiting)
    host_user_id: Mapped[int] = mapped_column(BigInteger)
    scenario_id: Mapped[int | None] = mapped_column(ForeignKey("game_scenarios.id"), nullable=True)
    bunker_capacity: Mapped[int] = mapped_column(Integer, default=0)
    current_round: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    players = relationship("Player", back_populates="game", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="game", cascade="all, delete-orphan")
    scenario = relationship("GameScenario")


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (UniqueConstraint("game_id", "user_id", name="uq_game_user"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True)
    is_host: Mapped[bool] = mapped_column(Boolean, default=False)
    card_id: Mapped[int | None] = mapped_column(ForeignKey("player_cards.id"), nullable=True)
    special_action_used: Mapped[bool] = mapped_column(Boolean, default=False)
    is_immune: Mapped[bool] = mapped_column(Boolean, default=False)
    elimination_round: Mapped[int | None] = mapped_column(Integer, nullable=True)
    joined_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    game = relationship("Game", back_populates="players")
    card = relationship("PlayerCard", foreign_keys=[card_id], uselist=False)


class PlayerCard(Base):
    __tablename__ = "player_cards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), unique=True, index=True)
    profession: Mapped[str] = mapped_column(String(255))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(32))
    health: Mapped[str] = mapped_column(String(255))
    hobby: Mapped[str] = mapped_column(String(255))
    luggage: Mapped[str] = mapped_column(String(255))
    trait: Mapped[str] = mapped_column(String(255))
    phobia: Mapped[str] = mapped_column(String(255))
    special_action: Mapped[str] = mapped_column(String(255))
    profession_revealed: Mapped[bool] = mapped_column(Boolean, default=False)
    health_revealed: Mapped[bool] = mapped_column(Boolean, default=False)
    hobby_revealed: Mapped[bool] = mapped_column(Boolean, default=False)
    luggage_revealed: Mapped[bool] = mapped_column(Boolean, default=False)
    trait_revealed: Mapped[bool] = mapped_column(Boolean, default=False)
    phobia_revealed: Mapped[bool] = mapped_column(Boolean, default=False)


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("game_id", "round_number", "voter_id", name="uq_round_single_vote"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    round_number: Mapped[int] = mapped_column(Integer, index=True)
    voter_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    game = relationship("Game", back_populates="votes")


class GameScenario(Base):
    __tablename__ = "game_scenarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text)
    water_months: Mapped[int] = mapped_column(Integer)
    food_months: Mapped[int] = mapped_column(Integer)
    has_electricity: Mapped[bool] = mapped_column(Boolean, default=True)
    has_medical: Mapped[bool] = mapped_column(Boolean, default=True)
    special_condition: Mapped[str] = mapped_column(Text)
    capacity_formula: Mapped[str] = mapped_column(String(64), default="half")


class PlayerStats(Base):
    __tablename__ = "player_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    total_games: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    eliminations: Mapped[int] = mapped_column(Integer, default=0)
    special_actions_used: Mapped[int] = mapped_column(Integer, default=0)
