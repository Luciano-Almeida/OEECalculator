# services/auth_service.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import database_external.crud as crud_external

async def get_authenticated_user_data(db: AsyncSession):
    try:
        user_id = await crud_external.get_last_active_user_id(db)
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
