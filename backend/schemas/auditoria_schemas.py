from pydantic import BaseModel
from datetime import datetime

class AuditoriaCreate(BaseModel):
    usuario: str
    tela: str
    acao: str
    detalhe: str
