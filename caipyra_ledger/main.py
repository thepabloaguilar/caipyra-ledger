from fastapi import FastAPI

from caipyra_ledger.api import api_router
from caipyra_ledger.configuration import settings

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    contact={
        'name': 'Pablo Aguilar',
        'url': 'https://thepabloaguilar.dev/',
        'email': 'pablo.aguilar@outlook.com.br',
    },
    license_info={
        'name': 'The Unlicense',
        'identifier': 'Unlicense',
        'url': 'https://github.com/thepabloaguilar/caipyra-ledger/blob/main/LICENSE',
    }
)

app.include_router(api_router, prefix='/api/v1')
