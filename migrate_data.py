import sqlite3
import psycopg2
from datetime import datetime
import logging
import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from database.base import Base
from database.models.user import User
from database.models.running_log import RunningLog
from database.models.team import Team, TeamMember
from database.models.challenge import Challenge, ChallengeParticipant
from database.models.goals import GroupGoal, YearlyArchive
from database.models.training import TrainingTemplate, TrainingPlan, ScheduledTraining

from database.session import engine

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 