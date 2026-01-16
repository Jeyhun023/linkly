from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'link_clicks',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('link_id', sa.BigInteger(), nullable=False),
        sa.Column('clicked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('referrer', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('ip_hash', sa.String(), nullable=False),
        sa.Column('ip_truncated', sa.String(), nullable=True),
        sa.Column('day', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['link_id'], ['links.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_link_clicks_id'), 'link_clicks', ['id'], unique=False)
    op.create_index('idx_link_clicks_link_id_clicked_at', 'link_clicks', ['link_id', 'clicked_at'], unique=False)
    op.create_index('idx_link_clicks_link_id_ip_hash', 'link_clicks', ['link_id', 'ip_hash'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_link_clicks_link_id_ip_hash', table_name='link_clicks')
    op.drop_index('idx_link_clicks_link_id_clicked_at', table_name='link_clicks')
    op.drop_index(op.f('ix_link_clicks_id'), table_name='link_clicks')
    op.drop_table('link_clicks')
