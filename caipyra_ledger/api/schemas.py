from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import PlainSerializer

from caipyra_ledger.database.models import AccountType
from caipyra_ledger.database.models import EntryType


class Entry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_name: str
    type: EntryType
    value: Decimal


class Transaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    occurred_at: datetime
    created_at: datetime


class Account(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    type: AccountType
    balance: Annotated[
        Decimal,
        PlainSerializer(
            lambda value: format(value, 'f'),
            return_type=str,
        ),
    ]
    created_at: datetime
    updated_at: datetime


class DetailedAccount(Account):
    entries: list[Entry]


class HealthCheckResponse(BaseModel):
    health: bool


class CreateAccountRequest(BaseModel):
    name: str
    type: AccountType


class CreateAccountResponse(BaseModel):
    account: Account


class GetAccountResponse(BaseModel):
    account: DetailedAccount


class CreateTransactionRequest(BaseModel):
    to_credit: str
    to_debit: str
    value: Decimal
    occurred_at: Optional[datetime] = None


class CreateTransactionResponse(BaseModel):
    transaction: Transaction
