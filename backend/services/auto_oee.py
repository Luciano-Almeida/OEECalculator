async def auto_oee():
    # Pegar todos os turnos

    # Verificar a última data no AutoOEE e verificar se precisa de um nov cálculo
    pass


from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from database.models import AutoOEE, OEESetup, DigestData 
from typing import Optional
import asyncio

class OEECalculatorService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_last_auto_oee(self, camera_name_id: int, shift: dict) -> Optional[AutoOEE]:
        """Fetch the latest AutoOEE record for a camera and shift."""
        result = await self.db_session.execute(
            select(AutoOEE)
            .where(AutoOEE.timestamp < shift["end_time"])
            .where(AutoOEE.camera_name_id == camera_name_id)
            .order_by(AutoOEE.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def calculate_oee(self, oee_setup: OEESetup, digest_data: DigestData) -> dict:
        """Calculate OEE metrics based on setup and digest data."""
        availability = (digest_data.stop_digest - digest_data.start_digest).total_seconds() / (
            oee_setup.digest_time * 3600
        )
        performance = digest_data.ok / (oee_setup.line_speed * oee_setup.digest_time)
        quality = digest_data.ok / (digest_data.ok + digest_data.nok)
        oee = availability * performance * quality
        return {
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "oee": oee,
            "total_ok": digest_data.ok,
            "total_not_ok": digest_data.nok,
        }

    async def save_auto_oee(self, camera_name_id: int, oee_metrics: dict):
        """Save the calculated OEE metrics into the AutoOEE table."""
        auto_oee = AutoOEE(camera_name_id=camera_name_id, **oee_metrics)
        self.db_session.add(auto_oee)
        await self.db_session.commit()

    async def process_camera_shifts(self):
        """Process all cameras and their shifts to calculate OEE if needed."""
        oee_setups = await self.db_session.execute(select(OEESetup))
        oee_setups = oee_setups.scalars().all()

        for oee_setup in oee_setups:
            for shift in oee_setup.shifts:
                last_auto_oee = await self.get_last_auto_oee(oee_setup.camera_name_id, shift)
                if last_auto_oee and last_auto_oee.timestamp >= shift["end_time"]:
                    continue  # Skip if the last OEE is already calculated for this shift

                # Fetch digest data for the shift
                digest_data = await self.db_session.execute(
                    select(DigestData)
                    .where(
                        and_(
                            DigestData.camera_name_id == oee_setup.camera_name_id,
                            DigestData.start_digest >= shift["start_time"],
                            DigestData.stop_digest <= shift["end_time"],
                        )
                    )
                )
                digest_data = digest_data.scalar_one_or_none()
                if not digest_data:
                    continue  # Skip if no digest data available for the shift

                # Calculate and save OEE
                oee_metrics = await self.calculate_oee(oee_setup, digest_data)
                await self.save_auto_oee(oee_setup.camera_name_id, oee_metrics)

    async def start_service(self, interval: int = 60):
        """Start the OEE calculation service."""
        while True:
            await self.process_camera_shifts()
            await asyncio.sleep(interval)