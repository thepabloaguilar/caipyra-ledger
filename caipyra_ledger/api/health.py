from fastapi import APIRouter

from caipyra_ledger.api.schemas import HealthCheckResponse

router = APIRouter()


@router.get('/check', response_model=HealthCheckResponse, name='Health Check')
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(health=True)
