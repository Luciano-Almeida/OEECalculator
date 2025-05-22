from typing import Dict, List
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, Text, Time, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.db import Base


# 📌 Tabela OEESetup
class OEESetup(Base):
    __tablename__ = "oee_setup"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String, nullable=False)
    stop_time: Mapped[float] = mapped_column(Float, nullable=False)
    digest_time: Mapped[float] = mapped_column(Float, nullable=False)
    line_speed: Mapped[float] = mapped_column(Float, nullable=False)
    #camera_name_id: Mapped[int] = mapped_column(ForeignKey("camera_name.id", ondelete="CASCADE"), nullable=False)
    camera_name_id: Mapped[int] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # ✅ Lista de objetos JSON
    shifts: Mapped[List[Dict]] = mapped_column(JSONB, nullable=True)


# 📌 Tabela DigestData
class DigestData(Base):
    __tablename__ = "digest_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ok: Mapped[int] = mapped_column(Integer, nullable=False)
    nok: Mapped[int] = mapped_column(Integer, nullable=False)
    #lote_id: Mapped[int] = mapped_column(ForeignKey("batch_id.id", ondelete="CASCADE"), nullable=False)
    #camera_name_id: Mapped[int] = mapped_column(ForeignKey("camera_name.id", ondelete="CASCADE"), nullable=False)
    lote_id: Mapped[int] = mapped_column(Integer, nullable=False)
    camera_name_id: Mapped[int] = mapped_column(Integer, nullable=True)
    start_digest: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    stop_digest: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    #timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


# 📌 Tabela PlannedDowntimeSetup
class PlannedDowntimeSetup(Base):
    __tablename__ = "planned_downtime_setup"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    stop_time: Mapped[Time] = mapped_column(Time, nullable=False)
    #camera_name_id: Mapped[int] = mapped_column(ForeignKey("camera_name.id", ondelete="CASCADE"), nullable=False)
    camera_name_id: Mapped[int] = mapped_column(Integer, nullable=False)


# 📌 Tabela UnplannedDowntimeSetup
class UnplannedDowntimeSetup(Base):
    __tablename__ = "unplanned_downtime_setup"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


# 📌 Tabela de Paradas
class Paradas(Base):
    __tablename__ = "paradas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    stop: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    #camera_name_id: Mapped[int] = mapped_column(ForeignKey("camera_name.id", ondelete="CASCADE"), nullable=False)
    camera_name_id: Mapped[int] = mapped_column(Integer, nullable=True)

# 📌 Tabela PlannedDowntime
class PlannedDowntime(Base):
    __tablename__ = "planned_downtime"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String, nullable=False)
    planned_downtime_id: Mapped[int] = mapped_column(ForeignKey("planned_downtime_setup.id", ondelete="CASCADE"), nullable=False)
    paradas_id: Mapped[int] = mapped_column(ForeignKey("paradas.id", ondelete="CASCADE"), nullable=False)
    observacoes: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


# 📌 Tabela UnplannedDowntime
class UnplannedDowntime(Base):
    __tablename__ = "unplanned_downtime"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String, nullable=False)
    unplanned_downtime_id: Mapped[int] = mapped_column(ForeignKey("unplanned_downtime_setup.id", ondelete="CASCADE"), nullable=False)
    paradas_id: Mapped[int] = mapped_column(ForeignKey("paradas.id", ondelete="CASCADE"), nullable=False)
    observacoes: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


# 📌 Tabela autoOEE
class AutoOEE(Base):
    __tablename__ = "auto_oee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    init: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    #camera_name_id: Mapped[int] = mapped_column(ForeignKey("camera_name.id", ondelete="CASCADE"), nullable=False)
    camera_name_id: Mapped[int] = mapped_column(Integer, nullable=True)
    availability: Mapped[float] = mapped_column(Float, nullable=False)
    performance: Mapped[float] = mapped_column(Float, nullable=False)
    quality: Mapped[float] = mapped_column(Float, nullable=False)
    oee: Mapped[float] = mapped_column(Float, nullable=False)
    total_ok: Mapped[int] = mapped_column(Integer, nullable=False)
    total_not_ok: Mapped[int] = mapped_column(Integer, nullable=False)
    downtime_summary: Mapped[dict] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
