from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class DevelopmentProfile(StrEnum):
    BALANCED = "BALANCED"
    TECHNICAL = "TECHNICAL"
    PHYSICAL = "PHYSICAL"
    CREATIVE = "CREATIVE"
    DEFENSIVE = "DEFENSIVE"
    FINISHER = "FINISHER"
    PLAYMAKER = "PLAYMAKER"
    ATHLETIC = "ATHLETIC"
    LATE_BLOOMER = "LATE_BLOOMER"


INTERNAL_ATTRIBUTE_NAMES = (
    "acceleration", "sprint_speed", "finishing", "shot_power", "long_shots", "volleys", "penalties",
    "vision", "short_passing", "long_passing", "crossing", "curve", "agility", "balance", "ball_control",
    "dribbling", "reactions", "defensive_awareness", "standing_tackle", "interceptions", "heading",
    "strength", "stamina", "jumping", "aggression", "decision_making", "composure", "creativity",
    "positioning", "concentration", "work_rate", "leadership",
    "diving", "handling", "kicking", "reflexes", "speed", "goalkeeper_positioning",
)


@dataclass
class PlayerAttributes:
    acceleration: float
    sprint_speed: float
    finishing: float
    shot_power: float
    long_shots: float
    volleys: float
    penalties: float
    vision: float
    short_passing: float
    long_passing: float
    crossing: float
    curve: float
    agility: float
    balance: float
    ball_control: float
    dribbling: float
    reactions: float
    defensive_awareness: float
    standing_tackle: float
    interceptions: float
    heading: float
    strength: float
    stamina: float
    jumping: float
    aggression: float
    decision_making: float
    composure: float
    creativity: float
    positioning: float
    concentration: float
    work_rate: float
    leadership: float
    diving: float
    handling: float
    kicking: float
    reflexes: float
    speed: float
    goalkeeper_positioning: float

    def __post_init__(self) -> None:
        for name in INTERNAL_ATTRIBUTE_NAMES:
            value = getattr(self, name)
            if not 1 <= value <= 100:
                raise ValueError(f"{name} must be between 1 and 100")


@dataclass
class PlayerState:
    confidence: float = 70.0
    morale: float = 70.0
    form: float = 70.0
    fitness: float = 100.0
    fatigue: float = 0.0
    happiness: float = 70.0
    reputation: float = 0.0

    def __post_init__(self) -> None:
        for value in vars(self).values():
            if not 0 <= value <= 100:
                raise ValueError("Player state values must be between 0 and 100")


@dataclass
class Player:
    id: str
    name: str
    surname: str
    nationality: str
    birth_date: date
    height: float
    weight: float
    preferred_foot: str
    primary_position: str
    secondary_positions: tuple[str, ...]
    attributes: PlayerAttributes
    current_ability: float
    potential: float
    development_rate: float
    development_profile: DevelopmentProfile
    role_familiarity: dict[str, float] = field(default_factory=dict)
    traits: tuple[str, ...] = ()
    personality: dict[str, float] = field(default_factory=dict)
    state: PlayerState = field(default_factory=PlayerState)
    archetype: str = "BALANCED"

    def __post_init__(self) -> None:
        if not 1 <= self.current_ability <= 100:
            raise ValueError("current_ability must be between 1 and 100")
        if not self.current_ability <= self.potential <= 100:
            raise ValueError("potential must be between current_ability and 100")
        if not 0 <= self.development_rate <= 100:
            raise ValueError("development_rate must be between 0 and 100")
        if any(not 0 <= value <= 100 for value in self.role_familiarity.values()):
            raise ValueError("role familiarity values must be between 0 and 100")
        if any(not 0 <= value <= 100 for value in self.personality.values()):
            raise ValueError("personality values must be between 0 and 100")
