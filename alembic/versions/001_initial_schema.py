"""initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create transfers table
    op.create_table(
        'transfers',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('jugador', sa.String(length=120), nullable=False),
        sa.Column('edad', sa.Integer(), nullable=False),
        sa.Column('posicion', sa.String(length=30), nullable=False),
        sa.Column('liga', sa.String(length=30), nullable=False),
        sa.Column('club_origen', sa.String(length=120), nullable=False),
        sa.Column('club_destino', sa.String(length=120), nullable=False),
        sa.Column('valor', sa.Float(), nullable=False),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('fecha', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes
    op.create_index('ix_transfers_liga', 'transfers', ['liga'], unique=False)
    op.create_index('ix_transfers_posicion', 'transfers', ['posicion'], unique=False)
    op.create_index('ix_transfers_club_destino', 'transfers', ['club_destino'], unique=False)
    op.create_index('ix_transfers_valor', 'transfers', ['valor'], unique=False)
    op.create_index('ix_transfers_fecha', 'transfers', ['fecha'], unique=False)
    
    # Unique constraint
    op.create_unique_constraint('uq_transfer_jugador_destino_fecha', 'transfers', ['jugador', 'club_destino', 'fecha'])

    # Create sync_logs table
    op.create_table(
        'sync_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('records_fetched', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_inserted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_index('ix_sync_logs_status', 'sync_logs', ['status'], unique=False)
    op.create_index('ix_sync_logs_created_at', 'sync_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_sync_logs_created_at', table_name='sync_logs')
    op.drop_index('ix_sync_logs_status', table_name='sync_logs')
    op.drop_table('sync_logs')
    
    op.drop_constraint('uq_transfer_jugador_destino_fecha', 'transfers', type_='unique')
    op.drop_index('ix_transfers_fecha', table_name='transfers')
    op.drop_index('ix_transfers_valor', table_name='transfers')
    op.drop_index('ix_transfers_club_destino', table_name='transfers')
    op.drop_index('ix_transfers_posicion', table_name='transfers')
    op.drop_index('ix_transfers_liga', table_name='transfers')
    op.drop_table('transfers')