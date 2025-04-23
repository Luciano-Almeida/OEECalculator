from fastapi import APIRouter

from .db_routes import router as db_routes_router
from .db_routes_testes import router as db_routes_router_testes
from .digest_routes import router as digest_routes_router
from .oee_routes import router as oee_routes_router
from .paradas_routes import router as paradas_routes_router
from .setup_paradas_routes import router as setup_paradas_routes_router
from .setup_oee_routes import router as setup_oee_routes_router


# Criar um objeto APIRouter para centralizar todas as rotas
api_router = APIRouter()

# Incluir os routers individuais
api_router.include_router(db_routes_router_testes, tags=["db_routes_router_testes"]) 
api_router.include_router(db_routes_router, tags=["db_routes_router"]) 
api_router.include_router(digest_routes_router, tags=["digest_routes_router"]) 
api_router.include_router(oee_routes_router, tags=["oee_routes_router"]) 
api_router.include_router(paradas_routes_router, tags=["paradas_routes_router"])
api_router.include_router(setup_paradas_routes_router, tags=["setup_paradas_routes_router"])
api_router.include_router(setup_oee_routes_router, tags=["setup_oee_routes_router"])
