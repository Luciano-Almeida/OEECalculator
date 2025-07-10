# utils/status

from typing import Dict, List, Optional, Union
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import database.crud as crud  # Importa as funções de criação do CRUD

class DigestStatus(BaseModel):
    camera_id: int
    status: str  # "ok", "atrasado", "aguardando"
    digest_time_control: Optional[float]  # em segundos



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

def calcular_status_digest(servico_oee, camera_id: int, digest_time_config: int = 600) -> DigestStatus:
    """
    Calcula o status do digest_time_control para uma única câmera.
    Retorna um objeto DigestStatus.
    """
    digest_time_control = servico_oee.digest_time_control.get(camera_id)

    if digest_time_control is None:
        return DigestStatus(
            camera_id=camera_id,
            status="aguardando",
            digest_time_control=None
        )
    
    digest_seconds = digest_time_control.total_seconds()
    status = "ok" if digest_seconds <= digest_time_config else "atrasado"
    
    return DigestStatus(
        camera_id=camera_id,
        status=status,
        digest_time_control=digest_seconds
    )

  