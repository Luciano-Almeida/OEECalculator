# services/auth_service.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import database_external.crud as crud_external

async def get_authenticated_user_data(db: AsyncSession):
    try:
        user_id = await crud_external.get_last_active_user_id(db)
        if user_id is None:
            print("***********Nenhum usuário ativo, retorna None")
            return None  # Nenhum usuário ativo, retorna None
        elif user_id == 0:
            return {
            "nome": "gaugau",
            "nivel_acesso": 0,
            "permissoes": ["OEE.OEE_DINAMICO", "OEE.PARADAS", "OEE.OEE_SEARCH", "OEE.OEE_SETUP", "OEE.PARADAS_SETUP"]
            }
        user_data = await crud_external.get_user_info_by_id(db, user_id)
        permissoes = await crud_external.get_permissoes_ativas_por_nivel_acesso(db, user_data["nivel_acesso"])

        user = {
            "nome": user_data["nome"],
            "nivel_acesso": user_data["nivel_acesso"],
            "permissoes": permissoes["permissoes"]
        }

        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
