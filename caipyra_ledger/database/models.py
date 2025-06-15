from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship

from caipyra_ledger.database.functions import utcnow

DefaultNumeric = Annotated[Decimal, 40]


@as_declarative()
class Base:
    registry = registry(
        type_annotation_map={
            DefaultNumeric: Numeric(40, 10),
        },
    )


class AccountType(StrEnum):
    DEBIT_NORMAL = 'DEBIT_NORMAL'
    CREDIT_NORMAL = 'CREDIT_NORMAL'


class Account(Base):
    __tablename__ = 'accounts'

    name: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    type: Mapped[AccountType] = mapped_column(nullable=False)
    balance: Mapped[DefaultNumeric] = mapped_column(nullable=False, default=Decimal(0))
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utcnow(),
        onupdate=utcnow(),
    )

    entries: Mapped[list['Entry']] = relationship()


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[UUID] = mapped_column(nullable=False, primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow())
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow())

    entries: Mapped[list['Entry']] = relationship()


class EntryType(StrEnum):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'


class Entry(Base):
    __tablename__ = 'entries'

    number: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey(Transaction.id),
        nullable=False,
        primary_key=True,
    )
    account_name: Mapped[str] = mapped_column(ForeignKey(Account.name), nullable=False)
    type: Mapped[EntryType] = mapped_column(nullable=False)
    value: Mapped[DefaultNumeric] = mapped_column(nullable=False)

    transaction: Mapped[Transaction] = relationship(back_populates='entries')
    account: Mapped[Account] = relationship(back_populates='entries')
