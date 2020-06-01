"""empty message

Revision ID: 6fdd341bf52c
Revises: 753b6a23b1e7
Create Date: 2020-05-16 23:12:46.766431

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fdd341bf52c'
down_revision = '753b6a23b1e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('city1', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'city1')
    # ### end Alembic commands ###
