"""initial1

Revision ID: 020a3ecc4cb6
Revises: 
Create Date: 2025-03-16 12:36:43.094003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from models import User, BankAccount

# revision identifiers, used by Alembic.
revision: str = '020a3ecc4cb6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создание таблицы users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('password', sa.String(50), nullable=False),
        sa.Column('is_admin', sa.Boolean, nullable=False, default=False),
    )

    # Создание таблицы bank_accounts
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('balance', sa.Integer, nullable=False, default=0),
    )

    # Создание таблицы orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('transaction_id', sa.String(50), nullable=False, unique=True),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('bank_account_id', sa.Integer, sa.ForeignKey('bank_accounts.id'), nullable=False),
        sa.Column('datetime', sa.DateTime, nullable=False),
    )

    users: list[dict] = [
        {
            "username": "admin",
            "password": "admin",
            "is_admin": True
        },
        {
            "username": "user",
            "password": "user",
            "is_admin": False
        }
    ]
    op.bulk_insert(
        User.__table__,
        users
    )
    op.bulk_insert(
        BankAccount.__table__,
        [
            {
                "user_id": 1,
                "balance": 0
            },
            {
                "user_id": 2,
                "balance": 0
            }
        ]
    )



def downgrade():
    # Удалите таблицы в обратном порядке
    op.drop_table('orders')
    op.drop_table('bank_accounts')
    op.drop_table('users')