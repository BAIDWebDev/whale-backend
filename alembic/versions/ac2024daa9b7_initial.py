"""initial

Revision ID: ac2024daa9b7
Revises: 
Create Date: 2024-05-31 12:19:34.117884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac2024daa9b7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=12), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('optiontypes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('settingsitems',
    sa.Column('key', sa.String(length=32), nullable=False),
    sa.Column('value', sa.String(length=2048), nullable=True),
    sa.PrimaryKeyConstraint('key')
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('color', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.String(length=9), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('pinyin', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=255), nullable=True),
    sa.Column('permissions', sa.String(length=1024), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itemtypes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('categoryId', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('image', sa.String(length=1024), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('shortDescription', sa.String(length=256), nullable=True),
    sa.Column('basePrice', sa.DECIMAL(precision=5, scale=2), nullable=True),
    sa.Column('salePercent', sa.DECIMAL(precision=5, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['categoryId'], ['categories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('optionitems',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('typeId', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('isDefault', sa.Boolean(), nullable=False),
    sa.Column('priceChange', sa.DECIMAL(precision=5, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['typeId'], ['optiontypes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('totalPrice', sa.DECIMAL(precision=5, scale=2), nullable=True),
    sa.Column('number', sa.String(length=5), nullable=True),
    sa.Column('status', sa.Enum('notStarted', 'inProgress', 'ready', 'pickedUp', name='orderstatus'), nullable=True),
    sa.Column('createdTime', sa.DateTime(), nullable=True),
    sa.Column('type', sa.Enum('pickUp', 'delivery', name='ordertype'), nullable=True),
    sa.Column('deliveryRoom', sa.String(length=64), nullable=True),
    sa.Column('userId', sa.String(length=9), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item_option_association',
    sa.Column('item_type_id', sa.Integer(), nullable=False),
    sa.Column('option_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_type_id'], ['itemtypes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['option_type_id'], ['optiontypes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('item_type_id', 'option_type_id')
    )
    op.create_table('ordereditems',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('orderId', sa.Integer(), nullable=True),
    sa.Column('itemTypeId', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['itemTypeId'], ['itemtypes.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['orderId'], ['orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag_item_type_association',
    sa.Column('item_type_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_type_id'], ['itemtypes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('item_type_id', 'tag_id')
    )
    op.create_table('ordered_item_option_association',
    sa.Column('ordered_item_id', sa.Integer(), nullable=False),
    sa.Column('option_item_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['option_item_id'], ['optionitems.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ordered_item_id'], ['ordereditems.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('ordered_item_id', 'option_item_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ordered_item_option_association')
    op.drop_table('tag_item_type_association')
    op.drop_table('ordereditems')
    op.drop_table('item_option_association')
    op.drop_table('orders')
    op.drop_table('optionitems')
    op.drop_table('itemtypes')
    op.drop_table('users')
    op.drop_table('tags')
    op.drop_table('settingsitems')
    op.drop_table('optiontypes')
    op.drop_table('categories')
    # ### end Alembic commands ###
