from collections.abc import Iterable, Mapping, Sequence

from app.player.engine import group_ratings
from app.world.entities import Club, ClubMembership, Manager, Player, SquadRole

ROLE_WEIGHTS: Mapping[SquadRole, float] = {
    SquadRole.STARTER: 1.0,
    SquadRole.ROTATION: 0.65,
    SquadRole.BACKUP: 0.35,
    SquadRole.YOUTH: 0.15,
}


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def normalize_external_value(raw_value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        return 50.0
    return clamp(100.0 * (raw_value - minimum) / (maximum - minimum))


def manager_quality(manager: Manager) -> float:
    return clamp(
        manager.tactical_quality * 0.30
        + manager.player_development * 0.25
        + manager.game_management * 0.20
        + manager.rotation * 0.10
        + manager.adaptability * 0.15
    )


def _roles_by_player(memberships: Iterable[ClubMembership]) -> dict[str, SquadRole]:
    return {membership.player_id: membership.role for membership in memberships}


def weighted_average(
    players: Iterable[Player],
    memberships: Iterable[ClubMembership] = (),
    role_weights: Mapping[SquadRole, float] = ROLE_WEIGHTS,
) -> float:
    players = tuple(players)
    if not players:
        return 0.0
    roles = _roles_by_player(memberships)
    weight_total = sum(role_weights[roles.get(player.id, SquadRole.STARTER)] for player in players)
    return sum(player.current_ability * role_weights[roles.get(player.id, SquadRole.STARTER)] for player in players) / weight_total


def squad_line_strengths(
    squad: Sequence[Player],
    memberships: Iterable[ClubMembership] = (),
    role_weights: Mapping[SquadRole, float] = ROLE_WEIGHTS,
) -> dict[str, float]:
    groups = {
        "attack": {"ST", "LW", "RW", "AM"},
        "midfield": {"CM", "DM", "AM"},
        "defense": {"CB", "LB", "RB"},
        "goalkeeper": {"GK"},
    }
    return {
        line: weighted_average(
            (player for player in squad if player.primary_position in positions), memberships, role_weights
        )
        for line, positions in groups.items()
    }


def squad_base(
    squad: Sequence[Player],
    memberships: Iterable[ClubMembership] = (),
    role_weights: Mapping[SquadRole, float] = ROLE_WEIGHTS,
) -> float:
    lines = squad_line_strengths(squad, memberships, role_weights)
    return (
        lines["attack"] * 0.30
        + lines["midfield"] * 0.28
        + lines["defense"] * 0.27
        + lines["goalkeeper"] * 0.15
    )


def squad_depth(
    squad: Sequence[Player],
    memberships: Iterable[ClubMembership] = (),
    role_weights: Mapping[SquadRole, float] = ROLE_WEIGHTS,
) -> float:
    roles = _roles_by_player(memberships)
    by_role = {
        role: weighted_average(
            (player for player in squad if roles.get(player.id, SquadRole.STARTER) == role),
            memberships,
            role_weights,
        )
        for role in SquadRole
    }
    positional_coverage = clamp(len({player.primary_position for player in squad}) / 10.0 * 100.0)
    return clamp(
        by_role[SquadRole.ROTATION] * 0.60
        + by_role[SquadRole.BACKUP] * 0.25
        + positional_coverage * 0.15
    )


def momentum_normalized(momentum: float) -> float:
    return clamp((momentum + 100.0) / 2.0)


def club_current_strength(club: Club, role_weights: Mapping[SquadRole, float] = ROLE_WEIGHTS) -> float:
    base = squad_base(club.squad, club.memberships, role_weights)
    return clamp(
        base * 0.75
        + manager_quality(club.manager) * 0.05
        + squad_depth(club.squad, club.memberships, role_weights) * 0.10
        + club.facilities * 0.03
        + momentum_normalized(club.momentum) * 0.07
    )


def league_strength(club_strengths: Sequence[float]) -> float:
    if not club_strengths:
        return 0.0
    ranked = sorted(club_strengths, reverse=True)

    def average(values: Sequence[float]) -> float:
        return sum(values) / len(values) if values else sum(ranked) / len(ranked)

    top_four = ranked[:4]
    top_eight = ranked[:8]
    middle = ranked[8:-4] or ranked
    bottom = ranked[-4:]
    return clamp(
        average(top_four) * 0.35
        + average(top_eight) * 0.25
        + average(middle) * 0.20
        + average(bottom) * 0.10
        + average(ranked) * 0.10
    )
