from pydantic import BaseModel
from datetime import datetime, time
from typing import List, Optional


# 📌 OEESetup
class Shift(BaseModel):
    #shift_id: Optional[int] = None
    name: str
    days: List[str]
    startTime: str
    endTime: str

class CREATEOEESetupSchema(BaseModel):
    user: str
    stop_time: float
    digest_time: float
    line_speed: float
    camera_name_id: Optional[int]
    shifts: Optional[List[Shift]] = None

    class Config:
        orm_mode = True


class OEESetupSchema(BaseModel):
    id: int
    user: str
    stop_time: float
    digest_time: float
    line_speed: float
    camera_name_id: Optional[int]
    timestamp: datetime
    shifts: Optional[List[Shift]] = None

    class Config:
        orm_mode = True


# 📌 DataReceived
class DataReceivedSchema(BaseModel):
    id: int
    ok_nok: int
    dados: str
    lote_id: int
    camera_name_id: Optional[int]
    timestamp: datetime

    class Config:
        orm_mode = True


# 📌 DigestData
class DigestDataSchema(BaseModel):
    id: int
    ok: int
    nok: int
    lote_id: int
    camera_name_id: Optional[int]
    start_digest: datetime
    stop_digest: datetime

    class Config:
        orm_mode = True


# 📌 PlannedDowntimeSetup
''' Modelo de entrada (request body) '''
class CREATEPlannedDowntimeSetup(BaseModel):
    name: str
    start_time: str  # No formato "HH:MM:SS"
    stop_time: str   # No formato "HH:MM:SS"
    camera_name_id: int

    class Config:
        orm_mode = True

''' Modelo de saída (response) '''
class PlannedDowntimeSetupSchema(BaseModel):
    id: int
    name: str
    start_time: time
    stop_time: time
    camera_name_id: int

    class Config:
        orm_mode = True


# 📌 UnplannedDowntimeSetup
''' Modelo de entrada (request body) '''
class CREATEUnplannedDowntimeSetupSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True

''' Modelo de saída (response) '''
class UnplannedDowntimeSetupSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# 📌 Paradas
class ParadaSchema(BaseModel):
    id: int
    start: datetime
    stop: datetime
    camera_name_id: Optional[int]

    class Config:
        orm_mode = True


# 📌 PlannedDowntime
class PlannedDowntimeSchema(BaseModel):
    id: int
    user: str
    planned_downtime_id: int
    paradas_id: int
    observacoes: Optional[str]
    #timestamp: datetime

    class Config:
        orm_mode = True


# 📌 UnplannedDowntime
''' Modelo de entrada (request body) '''
class CreateUnplannedDowntimeSchema(BaseModel):
    user: str
    unplanned_downtime_id: int
    paradas_id: int
    observacoes: str

''' Modelo de saída (response) '''
class UnplannedDowntimeSchema(BaseModel):
    id: int
    user: str
    unplanned_downtime_id: int
    paradas_id: int
    observacoes: Optional[str]
    #timestamp: datetime

    class Config:
        orm_mode = True


# 📌 AutoOEE
class AutoOEESchema(BaseModel):
    id: int
    availability: float
    performance: float
    quality: float
    oee: float
    total_ok: int
    total_not_ok: int
    timestamp: datetime

    class Config:
        orm_mode = True
