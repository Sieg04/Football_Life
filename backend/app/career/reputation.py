from dataclasses import dataclass


@dataclass(frozen=True)
class CareerReputation:
    domestic_reputation: float
    international_reputation: float
    club_reputation: float
    league_reputation: float
    media_visibility: float
    market_value_reputation: float

    @property
    def overall_prestige(self) -> float:
        return round(
            (self.domestic_reputation * 0.3)
            + (self.international_reputation * 0.25)
            + (self.club_reputation * 0.25)
            + (self.media_visibility * 0.2),
            1,
        )


def calculate_reputation(
    player_ovr: float,
    age: int,
    appearances: int = 0,
    goals: int = 0,
    assists: int = 0,
    average_rating: float = 6.8,
    trophies_count: int = 0,
    awards_count: int = 0,
    intl_caps: int = 0,
    intl_goals: int = 0,
    club_prestige: float = 70.0,
    league_prestige: float = 70.0,
    previous_reputation: CareerReputation | None = None,
) -> CareerReputation:
    """Calculates deterministic career reputation metrics."""
    # Base from current ability/OVR
    base_rep = max(20.0, min(99.0, (player_ovr - 50.0) * 1.8))

    # Performance modifier
    rating_bonus = (average_rating - 6.8) * 5.0
    stat_bonus = min(15.0, (goals * 0.4) + (assists * 0.3) + (appearances * 0.1))

    # Honors modifier
    honors_bonus = (trophies_count * 3.0) + (awards_count * 5.0)

    # International modifier
    intl_rep = max(10.0, min(99.0, (intl_caps * 1.5) + (intl_goals * 2.5) + (base_rep * 0.4)))

    dom_rep = max(10.0, min(99.0, base_rep + rating_bonus + stat_bonus + (honors_bonus * 0.6)))
    media_vis = max(10.0, min(99.0, (club_prestige * 0.4) + (dom_rep * 0.4) + (intl_rep * 0.2)))

    # Blend with previous reputation for smooth career evolution if available
    if previous_reputation:
        dom_rep = (previous_reputation.domestic_reputation * 0.6) + (dom_rep * 0.4)
        intl_rep = (previous_reputation.international_reputation * 0.7) + (intl_rep * 0.3)
        media_vis = (previous_reputation.media_visibility * 0.6) + (media_vis * 0.4)

    market_val_rep = max(10.0, min(99.0, (dom_rep * 0.5) + (player_ovr * 0.3) + (100.0 - age) * 0.2))

    return CareerReputation(
        domestic_reputation=round(dom_rep, 1),
        international_reputation=round(intl_rep, 1),
        club_reputation=round(club_prestige, 1),
        league_reputation=round(league_prestige, 1),
        media_visibility=round(media_vis, 1),
        market_value_reputation=round(market_val_rep, 1),
    )
