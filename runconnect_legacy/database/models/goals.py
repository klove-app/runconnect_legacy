from database.base import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class GroupGoal(Base):
    __tablename__ = "group_goals"

    year = Column(Integer, primary_key=True)
    total_goal = Column(Float)
    description = Column(String(1000))

class YearlyArchive(Base):
    __tablename__ = "yearly_archive"

    year = Column(Integer, primary_key=True)
    total_km = Column(Float)
    total_users = Column(Integer)
    goal_achieved = Column(Float) 