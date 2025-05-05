from fastapi import APIRouter

from .db_routes import router as db_routes_router
from .db_routes_testes import router as db_routes_router_testes
from .digest_data import router as digest_data_router
from .oee import router as oee_router
from .paradas import router as paradas_router
from .setup_paradas import router as setup_paradas_router
from .setup_oee import router as setup_oee_router


# Criar um objeto APIRouter para centralizar todas as rotas
api_router = APIRouter()

# Incluir os routers individuais
api_router.include_router(db_routes_router_testes, tags=["db_routes_router_testes"]) 
api_router.include_router(db_routes_router, tags=["db_routes_router"]) 
api_router.include_router(digest_data_router, tags=["digest_data_router"]) 
api_router.include_router(oee_router, tags=["oee_router"]) 
api_router.include_router(paradas_router, tags=["paradas_router"])
api_router.include_router(setup_oee_router, tags=["setup_oee_router"])
api_router.include_router(setup_paradas_router, tags=["setup_paradas_router"])

