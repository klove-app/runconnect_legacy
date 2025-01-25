from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, DECIMAL, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from database.base import Base
from datetime import datetime

class TrainingTemplate(Base):
    __tablename__ = 'training_templates'

    template_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False)
    difficulty_level = Column(String(50))
    target_metrics = Column(JSONB)
    instructions = Column(Text)
    created_at = Column(DateTime)

    # Отношения
    scheduled_trainings = relationship("ScheduledTraining", back_populates="template")

class TrainingPlan(Base):
    __tablename__ = 'training_plans'

    plan_id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    generation_params = Column(JSONB)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Отношения
    user = relationship("User")
    scheduled_trainings = relationship("ScheduledTraining", back_populates="plan")

class ScheduledTraining(Base):
    __tablename__ = 'scheduled_trainings'

    training_id = Column(BigInteger, primary_key=True)
    plan_id = Column(Integer, ForeignKey('training_plans.plan_id'))
    template_id = Column(Integer, ForeignKey('training_templates.template_id'))
    scheduled_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    target_metrics = Column(JSONB)
    completed_activity_id = Column(BigInteger, ForeignKey('running_log.log_id'))
    notes = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Отношения
    plan = relationship("TrainingPlan", back_populates="scheduled_trainings")
    template = relationship("TrainingTemplate", back_populates="scheduled_trainings")
    completed_activity = relationship("RunningLog", back_populates="completed_trainings") 