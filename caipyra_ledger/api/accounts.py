from decimal import Decimal

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from caipyra_ledger.api import schemas
from caipyra_ledger.database import models
from caipyra_ledger.database.session import get_session

router = APIRouter()


@router.post(
    '',
    name='Create Account',
    status_code=status.HTTP_201_CREATED,
)
async def create_account(request: schemas.CreateAccountRequest) -> schemas.CreateAccountResponse:
    async with get_session() as session:
        created_account = (
            await session.execute(
                insert(models.Account)
                .values(
                    name=request.name,
                    type=request.type,
                    balance=Decimal(0),
                ).returning(models.Account)
            )
        ).scalar()
        await session.commit()

    return schemas.CreateAccountResponse(
        account=schemas.Account.model_validate(created_account)
    )


@router.get(
    '/{account_name}',
    name='Get Account',
    status_code=status.HTTP_200_OK,
)
async def get_account(account_name: str) -> schemas.GetAccountResponse:
    async with get_session() as session:
        account = (
            await session.execute(
                select(models.Account)
                .where(models.Account.name == account_name)
                .options(joinedload(models.Account.entries))
            )
        ).scalar()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'message': 'Account not found',
            }
        )

    return schemas.GetAccountResponse(
        account=schemas.DetailedAccount.model_validate(account)
    )
