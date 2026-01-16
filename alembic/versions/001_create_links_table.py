from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'links',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('target_url', sa.String(), nullable=False),
        sa.Column('extra', sa.String(), nullable=True),
        sa.Column('is_disabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_links_id'), 'links', ['id'], unique=False)
    op.create_index(op.f('ix_links_slug'), 'links', ['slug'], unique=False)
    op.create_index('idx_links_slug', 'links', ['slug'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_links_slug', table_name='links')
    op.drop_index(op.f('ix_links_slug'), table_name='links')
    op.drop_index(op.f('ix_links_id'), table_name='links')
    op.drop_table('links')
