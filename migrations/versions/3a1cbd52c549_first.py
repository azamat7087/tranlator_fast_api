"""First

Revision ID: 3a1cbd52c549
Revises: 
Create Date: 2022-02-25 11:43:15.476622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a1cbd52c549'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('app_name', sa.String(length=200), nullable=False),
    sa.Column('app_id', sa.String(length=40), nullable=False),
    sa.Column('app_secret', sa.String(length=128), nullable=False),
    sa.Column('date_of_add', sa.DateTime(), nullable=False),
    sa.Column('date_of_update', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('app_id'),
    sa.UniqueConstraint('app_name')
    )
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    op.drop_table('applications')
    # ### end Alembic commands ###
