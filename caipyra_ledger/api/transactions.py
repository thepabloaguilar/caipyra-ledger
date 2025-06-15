from datetime import datetime
from decimal import Decimal
import uuid

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import insert, ScalarResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from caipyra_ledger.api import schemas
from caipyra_ledger.database import models
from caipyra_ledger.database.session import get_session

router = APIRouter()

@router.post(
    '',
    name='Create Transaction',
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(request: schemas.CreateTransactionRequest) -> schemas.CreateTransactionResponse:
    _validate_entries_values(request.entries)
    _validate_credits_and_debits(request.entries)

    account_names = [entry.account_name for entry in request.entries]
    async with get_session() as session:
        accounts = (
            await session.execute(
                select(models.Account)
                .where(models.Account.name.in_(account_names))
                .with_for_update()
            )
        ).scalars()

        _compute_new_accounts_balance(accounts, request.entries)
        saved_transaction = await _save_transaction(session, request)

        await session.commit()

    return schemas.CreateTransactionResponse(
        transaction=schemas.Transaction.model_validate(saved_transaction),
    )


def _validate_entries_values(entries: list[schemas.Entry]) -> None:
    if not all(entry.value > 0 for entry in entries):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                'message': 'entries cannot have zero or negative values',
            }
        )


def _validate_credits_and_debits(entries: list[schemas.Entry]) -> None:
    debit_credit_diff = Decimal(0)
    for entry in entries:
        match entry.type:
            case models.EntryType.DEBIT:
                debit_credit_diff += Decimal(entry.value)
            case models.EntryType.CREDIT:
                debit_credit_diff -= Decimal(entry.value)

    if debit_credit_diff != Decimal(0):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                'message': 'the difference between the debit and credit amount shuold be zero',
                'difference': str(debit_credit_diff),
            }
        )


def _compute_new_accounts_balance(accounts: ScalarResult[models.Account], entries: list[schemas.Entry]) -> None:
    accounts_by_name = {a.name: a for a in accounts}
    for entry in entries:
        account = accounts_by_name[entry.account_name]
        match (account.type, entry.type):
            case (models.AccountType.DEBIT_NORMAL, models.EntryType.DEBIT):
                account.balance += entry.value
            case (models.AccountType.DEBIT_NORMAL, models.EntryType.CREDIT):
                account.balance -= entry.value
            case (models.AccountType.CREDIT_NORMAL, models.EntryType.DEBIT):
                account.balance -= entry.value
            case (models.AccountType.CREDIT_NORMAL, models.EntryType.CREDIT):
                account.balance += entry.value

    if any(account.balance < 0 for account in accounts_by_name.values()):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                'message': 'account balances cannot have zero or negative values',
            }
        )


async def _save_transaction(session: AsyncSession, request: schemas.CreateTransactionRequest) -> schemas.Transaction:
    saved_transaction = (
        await session.execute(
            insert(models.Transaction)
            .values(
                id=uuid.uuid4(),
                occurred_at=request.occurred_at or datetime.now(),
            ).returning(models.Transaction)
        )
    ).scalar()

    await session.execute(
        insert(models.Entry).returning(models.Entry),
        [
            {
                'number': idx,
                'transaction_id': saved_transaction.id,  # type: ignore[union-attr]
                'account_name': entry.account_name,
                'type': entry.type,
                'value': entry.value,
            } for idx, entry in enumerate(request.entries, start=1)
        ]
    )

    return saved_transaction  # type: ignore[return-value]
