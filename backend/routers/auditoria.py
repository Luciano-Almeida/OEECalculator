# app.py
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from database.db import get_db
import database.crud as crud


router = APIRouter()

# Simulação de dados de usuários
users = [
    {"id": 1, "name": "João Silva"},
    {"id": 2, "name": "Maria Oliveira"},
    {"id": 3, "name": "Carlos Souza"},
    {"id": 4, "name": "Ana Costa"},
]

# Simulação de dados de trilha de auditoria
audit_trail_data = [
    {"userID": 1, "user": "João Silva", "action": "Login", "date": "2025-05-05", "details": "Login no sistema"},
    {"userID": 2, "user": "Maria Oliveira", "action": "Alteração de dados", "date": "2025-05-05", "details": "Alteração no perfil"},
    {"userID": 3, "user": "Carlos Souza", "action": "Logout", "date": "2025-05-05", "details": "Logout do sistema"},
    {"userID": 4, "user": "Ana Costa", "action": "Alteração de senha", "date": "2025-05-05", "details": "Alteração de senha do usuário"},
]

# Modelo para representar a estrutura dos dados de auditoria
class AuditEntry(BaseModel):
    user: str
    action: str
    date: str
    details: str

# Rota para obter a lista de usuários
@router.get("/users")
async def get_users():
    print("Get Users")
    return users

# Rota para obter a trilha de auditoria com base nos parâmetros
@router.get("/audit-trail")
async def get_audit_trail(
    userID: Optional[int] = None,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None
):
    print("Trilha de auditoria0", userID, startDate, endDate)
    filtered_data = audit_trail_data
    print("Trilha de auditoria11", filtered_data)
    # Filtra por usuário se fornecido
    if userID:
        filtered_data = [entry for entry in filtered_data if entry["userID"] == userID]
    print("Trilha de auditoria1", filtered_data)
    # Filtra por período (startDate e endDate) se fornecido
    if startDate:
        filtered_data = [entry for entry in filtered_data if entry["date"] >= startDate]
    if endDate:
        filtered_data = [entry for entry in filtered_data if entry["date"] <= endDate]
    print("Trilha de auditoria", filtered_data)
    return filtered_data
