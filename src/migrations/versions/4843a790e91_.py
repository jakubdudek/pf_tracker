"""empty message

Revision ID: 4843a790e91
Revises: 1a6ff1a1a99
Create Date: 2015-05-19 22:07:57.865026

"""

# revision identifiers, used by Alembic.
revision = '4843a790e91'
down_revision = '1a6ff1a1a99'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('portfolios')
    op.drop_table('transactions2')
    op.drop_table('transactions')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transactions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('Trade', sa.VARCHAR(length=64), nullable=True),
    sa.Column('Symbol', sa.VARCHAR(length=64), nullable=True),
    sa.Column('Shares', sa.FLOAT(), nullable=True),
    sa.Column('Price', sa.FLOAT(), nullable=True),
    sa.Column('Comission', sa.FLOAT(), nullable=True),
    sa.Column('Fee', sa.FLOAT(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions2',
    sa.Column('index', sa.DATETIME(), nullable=True),
    sa.Column('ID', sa.BIGINT(), nullable=True),
    sa.Column('Trade', sa.TEXT(), nullable=True),
    sa.Column('Symbol', sa.TEXT(), nullable=True),
    sa.Column('Shares', sa.FLOAT(), nullable=True),
    sa.Column('Price', sa.FLOAT(), nullable=True),
    sa.Column('Commission', sa.FLOAT(), nullable=True),
    sa.Column('Fee', sa.FLOAT(), nullable=True)
    )
    op.create_table('portfolios',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('holdings', sa.BLOB(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###
