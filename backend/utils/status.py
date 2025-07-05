# utils/status

from typing import Dict, List, Union
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import database.crud as crud  # Importa as funções de criação do CRUD


async def obter_status_do_setup(db: AsyncSession) -> Dict[str, Union[bool, List[int], str]]:
    lista_de_cameras = [1, 2]  # Alterar no futuro -> Ler do banco Nauta ou de variáveis de ambiente

    cameras_faltando_setup = []

    try:
        for camera_id in lista_de_cameras:
            oee_setup = await crud.get_oee_setup_by_camera_name_id(db, camera_id)
            if not oee_setup:
                cameras_faltando_setup.append(camera_id)

        oee_ready = len(cameras_faltando_setup) == 0

        return {
            "oee_ready": oee_ready,
            "cameras_faltando_setup": cameras_faltando_setup
        }

    except SQLAlchemyError as e:
        print(f"❌ Erro ao verificar status setup: {e}")
        return {
            "error": str(e),
            "oee_ready": False,
            "cameras_faltando_setup": []
        }

    