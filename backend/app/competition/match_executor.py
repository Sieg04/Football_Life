from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.competition.domain import Competition, CompetitionSeason
from app.competition.fixtures import Fixture
from app.competition.orchestrator import (
    FixtureExecutionResult,
    FixtureExecutor,
    OrchestrationContext,
    SeasonSimulationConfig,
)
from app.match.domain import MatchContext, MatchResult, SimulationMode
from app.match.lineup import (
    FORMATION_PRESETS,
    TacticalPreset,
    calculate_effective_team_strength,
    calculate_xi_quality,
    select_lineup,
)
from app.match.performance import simulate_player_performances
from app.match.resolution import resolve_match_resolution
from app.world.entities import Club, Manager, Player


@dataclass(frozen=True)
class MatchFixtureExecutionResult(FixtureExecutionResult):
    match_result: MatchResult

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.match_result is None:
            raise ValueError("match_result must not be None")
        if not isinstance(self.match_result, MatchResult):
            raise TypeError(
                f"match_result must be a MatchResult instance, got '{type(self.match_result).__name__}'"
            )
        if self.match_result.match_id != self.fixture_id:
            raise ValueError(
                f"MatchResult.match_id '{self.match_result.match_id}' "
                f"does not match fixture_id '{self.fixture_id}'"
            )


@dataclass(frozen=True)
class MatchSimulationParticipants:
    home_club: Club
    away_club: Club
    home_manager: Manager
    away_manager: Manager
    home_formation: str = "4-3-3"
    away_formation: str = "4-3-3"
    home_tactical_preset: TacticalPreset | None = None
    away_tactical_preset: TacticalPreset | None = None

    def __post_init__(self) -> None:
        if self.home_club is None:
            raise ValueError("home_club must not be None")
        if self.away_club is None:
            raise ValueError("away_club must not be None")
        if self.home_manager is None:
            raise ValueError("home_manager must not be None")
        if self.away_manager is None:
            raise ValueError("away_manager must not be None")

        if not isinstance(self.home_club, Club):
            raise TypeError("home_club must be a Club instance")
        if not isinstance(self.away_club, Club):
            raise TypeError("away_club must be a Club instance")
        if not isinstance(self.home_manager, Manager):
            raise TypeError("home_manager must be a Manager instance")
        if not isinstance(self.away_manager, Manager):
            raise TypeError("away_manager must be a Manager instance")

        if not self.home_club.squad or len(self.home_club.squad) < 11:
            raise ValueError("home_club.squad must contain at least 11 players")
        if not self.away_club.squad or len(self.away_club.squad) < 11:
            raise ValueError("away_club.squad must contain at least 11 players")


ParticipantResolver = Callable[
    [Fixture, OrchestrationContext],
    MatchSimulationParticipants,
]


def build_match_context(
    fixture: Fixture,
    competition: Competition,
    competition_season: CompetitionSeason,
    config: SeasonSimulationConfig,
    simulation_mode: SimulationMode = SimulationMode.FAST,
) -> MatchContext:
    if fixture is None:
        raise ValueError("fixture must not be None")
    if competition is None:
        raise ValueError("competition must not be None")
    if competition_season is None:
        raise ValueError("competition_season must not be None")
    if config is None:
        raise ValueError("config must not be None")

    if fixture.competition_season_id != competition_season.id:
        raise ValueError(
            f"fixture competition_season_id '{fixture.competition_season_id}' "
            f"does not match competition_season.id '{competition_season.id}'"
        )
    if competition_season.competition_id != competition.id:
        raise ValueError(
            f"competition_season competition_id '{competition_season.competition_id}' "
            f"does not match competition.id '{competition.id}'"
        )

    if not isinstance(simulation_mode, SimulationMode):
        try:
            simulation_mode = SimulationMode(simulation_mode)
        except ValueError as err:
            raise ValueError(f"Invalid simulation_mode '{simulation_mode}'") from err

    return MatchContext(
        match_id=fixture.id,
        home_club_id=fixture.home_club_id,
        away_club_id=fixture.away_club_id,
        competition_type=competition.competition_type,
        competition_importance=competition.importance,
        match_importance=fixture.importance,
        seed=fixture.seed,
        rivalry_factor=fixture.rivalry_factor,
        simulation_mode=simulation_mode,
    )


def execute_fixture_with_match_engine(
    fixture: Fixture,
    context: OrchestrationContext,
    participant_resolver: ParticipantResolver,
    simulation_mode: SimulationMode = SimulationMode.FAST,
) -> MatchFixtureExecutionResult:
    if fixture is None:
        raise ValueError("fixture must not be None")
    if context is None:
        raise ValueError("context must not be None")
    if participant_resolver is None or not callable(participant_resolver):
        raise ValueError("participant_resolver must be callable")

    if fixture.competition_season_id != context.competition_season.id:
        raise ValueError(
            f"fixture competition_season_id '{fixture.competition_season_id}' "
            f"does not match orchestration context season id '{context.competition_season.id}'"
        )
    if context.competition_season.competition_id != context.competition.id:
        raise ValueError(
            f"context competition_season competition_id '{context.competition_season.competition_id}' "
            f"does not match context competition id '{context.competition.id}'"
        )

    participants = participant_resolver(fixture, context)
    if not isinstance(participants, MatchSimulationParticipants):
        raise TypeError(
            f"participant_resolver returned object of type '{type(participants).__name__}', "
            f"expected MatchSimulationParticipants"
        )

    # Validate club IDs if available on club object
    if hasattr(participants.home_club, "id"):
        h_id = getattr(participants.home_club, "id")
        if h_id != fixture.home_club_id:
            raise ValueError(
                f"Resolved home_club.id '{h_id}' does not match fixture home_club_id '{fixture.home_club_id}'"
            )
    if hasattr(participants.away_club, "id"):
        a_id = getattr(participants.away_club, "id")
        if a_id != fixture.away_club_id:
            raise ValueError(
                f"Resolved away_club.id '{a_id}' does not match fixture away_club_id '{fixture.away_club_id}'"
            )

    match_context = build_match_context(
        fixture=fixture,
        competition=context.competition,
        competition_season=context.competition_season,
        config=context.config,
        simulation_mode=simulation_mode,
    )

    home_fmt = (
        participants.home_tactical_preset
        if participants.home_tactical_preset is not None
        else FORMATION_PRESETS.get(participants.home_formation, FORMATION_PRESETS["4-3-3"])
    )
    away_fmt = (
        participants.away_tactical_preset
        if participants.away_tactical_preset is not None
        else FORMATION_PRESETS.get(participants.away_formation, FORMATION_PRESETS["4-3-3"])
    )

    home_lineup = select_lineup(
        squad=list(participants.home_club.squad),
        club_id=fixture.home_club_id,
        formation=home_fmt,
        manager=participants.home_manager,
        competition_importance=fixture.importance,
        as_of=fixture.scheduled_date,
    )
    away_lineup = select_lineup(
        squad=list(participants.away_club.squad),
        club_id=fixture.away_club_id,
        formation=away_fmt,
        manager=participants.away_manager,
        competition_importance=fixture.importance,
        as_of=fixture.scheduled_date,
    )

    h_xi_quality = calculate_xi_quality(home_lineup.starters, home_fmt)
    a_xi_quality = calculate_xi_quality(away_lineup.starters, away_fmt)

    home_form_avg = (
        sum(p.state.form for p in participants.home_club.squad) / len(participants.home_club.squad)
        if participants.home_club.squad
        else 75.0
    )
    away_form_avg = (
        sum(p.state.form for p in participants.away_club.squad) / len(participants.away_club.squad)
        if participants.away_club.squad
        else 75.0
    )

    home_fitness_avg = (
        sum(p.state.fitness for p in participants.home_club.squad) / len(participants.home_club.squad)
        if participants.home_club.squad
        else 100.0
    )
    away_fitness_avg = (
        sum(p.state.fitness for p in participants.away_club.squad) / len(participants.away_club.squad)
        if participants.away_club.squad
        else 100.0
    )

    home_eff_strength = calculate_effective_team_strength(
        xi_quality=h_xi_quality,
        club_strength=participants.home_club.prestige,
        manager_quality=participants.home_manager.tactical_quality,
        tactical_fit=home_lineup.tactical_fit,
        form_factor=home_form_avg,
        fitness_factor=home_fitness_avg,
        club_id=fixture.home_club_id,
    )
    away_eff_strength = calculate_effective_team_strength(
        xi_quality=a_xi_quality,
        club_strength=participants.away_club.prestige,
        manager_quality=participants.away_manager.tactical_quality,
        tactical_fit=away_lineup.tactical_fit,
        form_factor=away_form_avg,
        fitness_factor=away_fitness_avg,
        club_id=fixture.away_club_id,
    )

    resolution_state = resolve_match_resolution(
        context=match_context,
        home_strength=home_eff_strength,
        away_strength=away_eff_strength,
    )

    performances, events = simulate_player_performances(
        context=match_context,
        resolution=resolution_state,
        home_lineup=home_lineup,
        away_lineup=away_lineup,
    )

    match_result = MatchResult(
        match_id=match_context.match_id,
        home_club_id=match_context.home_club_id,
        away_club_id=match_context.away_club_id,
        home_score=resolution_state.home_score,
        away_score=resolution_state.away_score,
        home_xg=resolution_state.home_xg,
        away_xg=resolution_state.away_xg,
        home_possession=resolution_state.home_possession,
        away_possession=resolution_state.away_possession,
        home_shots=resolution_state.home_shots,
        away_shots=resolution_state.away_shots,
        player_performances=performances,
        events=events,
    )

    if match_result.match_id != fixture.id:
        raise ValueError(
            f"Generated MatchResult.match_id '{match_result.match_id}' "
            f"does not match fixture.id '{fixture.id}'"
        )
    if match_result.home_club_id != fixture.home_club_id:
        raise ValueError(
            f"Generated MatchResult.home_club_id '{match_result.home_club_id}' "
            f"does not match fixture.home_club_id '{fixture.home_club_id}'"
        )
    if match_result.away_club_id != fixture.away_club_id:
        raise ValueError(
            f"Generated MatchResult.away_club_id '{match_result.away_club_id}' "
            f"does not match fixture.away_club_id '{fixture.away_club_id}'"
        )

    return MatchFixtureExecutionResult(
        fixture_id=fixture.id,
        completed=True,
        match_result=match_result,
    )


def build_match_engine_executor(
    participant_resolver: ParticipantResolver,
    simulation_mode: SimulationMode = SimulationMode.FAST,
) -> FixtureExecutor:
    if participant_resolver is None or not callable(participant_resolver):
        raise ValueError("participant_resolver must be callable")

    def _executor(fixture: Fixture, context: OrchestrationContext) -> MatchFixtureExecutionResult:
        return execute_fixture_with_match_engine(
            fixture=fixture,
            context=context,
            participant_resolver=participant_resolver,
            simulation_mode=simulation_mode,
        )

    return _executor
