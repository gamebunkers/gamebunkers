from collections import Counter

from game.models import VoteResult


def resolve_votes(votes: list[tuple[int, int]]) -> VoteResult:
    if not votes:
        return VoteResult(eliminated_player_id=None, tied_player_ids=[], vote_counts={})
    counts = Counter(target for _, target in votes)
    top = max(counts.values())
    tops = [pid for pid, count in counts.items() if count == top]
    if len(tops) > 1:
        return VoteResult(eliminated_player_id=None, tied_player_ids=tops, vote_counts=dict(counts))
    return VoteResult(eliminated_player_id=tops[0], tied_player_ids=[], vote_counts=dict(counts))
