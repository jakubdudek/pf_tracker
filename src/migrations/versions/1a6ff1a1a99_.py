"""empty message

Revision ID: 1a6ff1a1a99
Revises: 457380eef1f
Create Date: 2015-05-19 20:38:25.062978

"""

# revision identifiers, used by Alembic.
revision = '1a6ff1a1a99'
down_revision = '457380eef1f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tmp')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tmp',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('pwel', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###
