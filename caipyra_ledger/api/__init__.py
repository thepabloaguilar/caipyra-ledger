from fastapi import APIRouter

from caipyra_ledger.api import accounts
from caipyra_ledger.api import health
from caipyra_ledger.api import transactions

api_router = APIRouter()

api_router.include_router(accounts.router, prefix='/accounts', tags=['accounts'])
api_router.include_router(transactions.router, prefix='/transactions', tags=['transactions'])
api_router.include_router(health.router, prefix='/health', tags=['health'])
