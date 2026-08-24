from random import Random

from app.player.generation import generate_player
from app.world.entities import Player

POSITIONS = ("GK", "CB", "LB", "RB", "DM", "CM", "AM", "LW", "RW", "ST")


def generate_generic_squad(
    target_strength: float, rng: Random, club_name: str = "World Club", nationality: str = "UNK"
) -> tuple[Player, ...]:
    squad: list[Player] = []
    for position_index, position in enumerate(POSITIONS):
        for role_index, adjustment in enumerate((0.0, -4.0, -9.0, -15.0)):
            rating = target_strength + adjustment + rng.uniform(-5.0, 5.0)
            rating = round(max(1.0, min(100.0, rating)), 2)
            squad.append(
                generate_player(
                    rng.getrandbits(64),
                    player_id=f"{club_name.lower().replace(' ', '-')}-{position_index:02d}-{role_index:02d}",
                    name="World",
                    surname=f"{club_name} {position} {role_index + 1}",
                    position=position,
                    nationality=nationality,
                    target_ability=rating,
                )
            )
    return tuple(squad)
