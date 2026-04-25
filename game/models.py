from dataclasses import dataclass


@dataclass(slots=True)
class VoteResult:
    eliminated_player_id: int | None
    tied_player_ids: list[int]
    vote_counts: dict[int, int]


@dataclass(slots=True)
class ActionResult:
    success: bool
    message: str
