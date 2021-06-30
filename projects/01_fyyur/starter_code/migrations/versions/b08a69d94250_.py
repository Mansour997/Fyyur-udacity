"""empty message

Revision ID: b08a69d94250
Revises: 22e28a0b529c
Create Date: 2021-06-29 14:12:54.248703

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b08a69d94250'
down_revision = '22e28a0b529c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shows_artist_id_fkey', 'shows', type_='foreignkey')
    op.drop_constraint('shows_venue_id_fkey', 'shows', type_='foreignkey')
    op.drop_column('shows', 'artist_id')
    op.drop_column('shows', 'start_time')
    op.drop_column('shows', 'venue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('shows_venue_id_fkey', 'shows', 'venues', ['venue_id'], ['id'])
    op.create_foreign_key('shows_artist_id_fkey', 'shows', 'artists', ['artist_id'], ['id'])
    # ### end Alembic commands ###
