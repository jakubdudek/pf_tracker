"""empty message

Revision ID: 53a251ecf99
Revises: 498ed61c5d9
Create Date: 2015-05-21 22:24:44.311602

"""

# revision identifiers, used by Alembic.
revision = '53a251ecf99'
down_revision = '498ed61c5d9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions2')
    op.drop_table('transaction_1')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction_1',
    sa.Column('index', sa.DATETIME(), nullable=True),
    sa.Column('ID', sa.BIGINT(), nullable=True),
    sa.Column('Trade', sa.TEXT(), nullable=True),
    sa.Column('Symbol', sa.TEXT(), nullable=True),
    sa.Column('Shares', sa.FLOAT(), nullable=True),
    sa.Column('Price', sa.FLOAT(), nullable=True),
    sa.Column('Commission', sa.FLOAT(), nullable=True),
    sa.Column('Fee', sa.FLOAT(), nullable=True)
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
    ### end Alembic commands ###
