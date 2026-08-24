"""create career engine tables

Revision ID: c4a91f38e210
Revises: e2c31d282bfb
Create Date: 2026-08-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4a91f38e210'
down_revision: Union[str, None] = 'e2c31d282bfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'careers',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('player_id', sa.String(length=64), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('current_season_number', sa.Integer(), nullable=False),
        sa.Column('current_season_label', sa.String(length=16), nullable=False),
        sa.Column('current_club_id', sa.Integer(), nullable=False),
        sa.Column('career_phase', sa.String(length=32), nullable=False),
        sa.Column('peak_ability', sa.Float(), nullable=False),
        sa.Column('peak_ovr', sa.Float(), nullable=False),
        sa.Column('peak_age', sa.Integer(), nullable=False),
        sa.Column('peak_position', sa.String(length=8), nullable=False),
        sa.Column('peak_club_id', sa.Integer(), nullable=False),
        sa.Column('seed', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['current_club_id'], ['clubs.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_careers_current_club_id'), 'careers', ['current_club_id'], unique=False)
    op.create_index(op.f('ix_careers_player_id'), 'careers', ['player_id'], unique=False)

    op.create_table(
        'seasons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('career_id', sa.String(length=64), nullable=False),
        sa.Column('season_number', sa.Integer(), nullable=False),
        sa.Column('season_label', sa.String(length=16), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('player_id', sa.String(length=64), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('starting_age', sa.Integer(), nullable=False),
        sa.Column('ending_age', sa.Integer(), nullable=False),
        sa.Column('starting_position', sa.String(length=8), nullable=False),
        sa.Column('ending_position', sa.String(length=8), nullable=False),
        sa.Column('starting_ability', sa.Float(), nullable=False),
        sa.Column('ending_ability', sa.Float(), nullable=False),
        sa.Column('starting_ovr', sa.Float(), nullable=False),
        sa.Column('ending_ovr', sa.Float(), nullable=False),
        sa.Column('career_phase_at_start', sa.String(length=32), nullable=False),
        sa.Column('career_phase_at_end', sa.String(length=32), nullable=False),
        sa.Column('playing_time_input', sa.JSON(), nullable=False),
        sa.Column('performance_input', sa.JSON(), nullable=False),
        sa.Column('environment_input', sa.JSON(), nullable=False),
        sa.Column('development_budget', sa.Float(), nullable=False),
        sa.Column('development_summary', sa.JSON(), nullable=False),
        sa.Column('attribute_changes', sa.JSON(), nullable=False),
        sa.Column('season_seed', sa.String(length=128), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['career_id'], ['careers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seasons_career_id'), 'seasons', ['career_id'], unique=False)
    op.create_index(op.f('ix_seasons_club_id'), 'seasons', ['club_id'], unique=False)
    op.create_index(op.f('ix_seasons_player_id'), 'seasons', ['player_id'], unique=False)

    op.create_table(
        'season_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('career_id', sa.String(length=64), nullable=False),
        sa.Column('season_number', sa.Integer(), nullable=False),
        sa.Column('season_label', sa.String(length=16), nullable=False),
        sa.Column('starting_age', sa.Integer(), nullable=False),
        sa.Column('ending_age', sa.Integer(), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('starting_position', sa.String(length=8), nullable=False),
        sa.Column('ending_position', sa.String(length=8), nullable=False),
        sa.Column('starting_ability', sa.Float(), nullable=False),
        sa.Column('ending_ability', sa.Float(), nullable=False),
        sa.Column('starting_ovr', sa.Float(), nullable=False),
        sa.Column('ending_ovr', sa.Float(), nullable=False),
        sa.Column('career_phase_at_start', sa.String(length=32), nullable=False),
        sa.Column('career_phase_at_end', sa.String(length=32), nullable=False),
        sa.Column('playing_time_input', sa.JSON(), nullable=False),
        sa.Column('performance_input', sa.JSON(), nullable=False),
        sa.Column('environment_input', sa.JSON(), nullable=False),
        sa.Column('development_budget', sa.Float(), nullable=False),
        sa.Column('development_summary', sa.JSON(), nullable=False),
        sa.Column('attribute_changes', sa.JSON(), nullable=False),
        sa.Column('season_seed', sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(['career_id'], ['careers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_season_snapshots_career_id'), 'season_snapshots', ['career_id'], unique=False)
    op.create_index(op.f('ix_season_snapshots_club_id'), 'season_snapshots', ['club_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_season_snapshots_club_id'), table_name='season_snapshots')
    op.drop_index(op.f('ix_season_snapshots_career_id'), table_name='season_snapshots')
    op.drop_table('season_snapshots')
    op.drop_index(op.f('ix_seasons_player_id'), table_name='seasons')
    op.drop_index(op.f('ix_seasons_club_id'), table_name='seasons')
    op.drop_index(op.f('ix_seasons_career_id'), table_name='seasons')
    op.drop_table('seasons')
    op.drop_index(op.f('ix_careers_player_id'), table_name='careers')
    op.drop_index(op.f('ix_careers_current_club_id'), table_name='careers')
    op.drop_table('careers')
