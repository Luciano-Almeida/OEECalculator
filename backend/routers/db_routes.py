from datetime import datetime, time, timedelta
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso

from database.crud import create_parada
import schemas as schemas

# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup

router = APIRouter()



