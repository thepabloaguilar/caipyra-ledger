from datetime import datetime
from decimal import Decimal
from typing import Sequence
import uuid

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import insert
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
    _validate_value(request.value)

    async with get_session() as session:
        accounts = (
            await session.execute(
                select(models.Account)
                .where(models.Account.name.in_([request.to_credit, request.to_debit]))
                .with_for_update()
            )
        ).scalars().all()

        if len(accounts) != 2:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail={
                    'message': 'one of the accounts does not exist',
                    'found_accounts': [account.name for account in accounts],
                }
            )

        _compute_new_accounts_balance(accounts, request)
        saved_transaction = await _save_transaction(session, request)

        await session.commit()

    return schemas.CreateTransactionResponse(
        transaction=schemas.Transaction.model_validate(saved_transaction),
    )


def _validate_value(value: Decimal) -> None:
    if value <= Decimal(0):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                'message': 'value cannot be zero or negative',
            }
        )


def _compute_new_accounts_balance(accounts: Sequence[models.Account], request: schemas.CreateTransactionRequest) -> None:
    accounts_by_name = {a.name: a for a in accounts}

    account_to_credit = accounts_by_name[request.to_credit]
    match account_to_credit.type:
        case models.AccountType.DEBIT_NORMAL:
            account_to_credit.balance -= request.value
        case models.AccountType.CREDIT_NORMAL:
            account_to_credit.balance += request.value

    account_to_debit = accounts_by_name[request.to_debit]
    match account_to_debit.type:
        case models.AccountType.DEBIT_NORMAL:
            account_to_debit.balance += request.value
        case models.AccountType.CREDIT_NORMAL:
            account_to_debit.balance -= request.value

    if account_to_credit.balance < 0 or account_to_debit.balance < 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                'message': 'account balances cannot have zero or negative values',
            }
        )


async def _save_transaction(session: AsyncSession, request: schemas.CreateTransactionRequest) -> schemas.Transaction:
    occurred_at = request.occurred_at or datetime.now()
    saved_transaction = (
        await session.execute(
            insert(models.Transaction)
            .values(
                id=uuid.uuid4(),
                occurred_at=occurred_at.replace(tzinfo=None),
            ).returning(models.Transaction)
        )
    ).scalar()

    await session.execute(
        insert(models.Entry),
        [
            {
                'number': 1,
                'transaction_id': saved_transaction.id,  # type: ignore[union-attr]
                'account_name': request.to_credit,
                'type': models.EntryType.CREDIT,
                'value': request.value,
            },
            {
                'number': 2,
                'transaction_id': saved_transaction.id,  # type: ignore[union-attr]
                'account_name': request.to_debit,
                'type': models.EntryType.DEBIT,
                'value': request.value,
            },
        ]
    )

    return saved_transaction  # type: ignore[return-value]
