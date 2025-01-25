from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DECIMAL, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text, func, extract
from datetime import datetime
from database.base import Base
from database.session import Session
from database.logger import logger
from typing import List
import traceback

class RunningLog(Base):
    __tablename__ = "running_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey("users.user_id"))
    km = Column(Float)
    date_added = Column(Date)
    notes = Column(String(1000))
    chat_id = Column(String(255))
    chat_type = Column(String(50))
    
    # Новые поля для расширенных данных
    external_id = Column(String(255))
    external_source = Column(String(50))
    detailed_metrics = Column(JSONB)
    splits = Column(JSONB)
    elevation_data = Column(JSONB)
    average_heartrate = Column(DECIMAL)
    max_heartrate = Column(DECIMAL)
    perceived_effort = Column(Integer)
    training_load = Column(DECIMAL)
    recovery_time = Column(Interval)

    # Отношения
    user = relationship("User", back_populates="running_logs")
    completed_trainings = relationship("ScheduledTraining", back_populates="completed_activity")

    @classmethod
    def add_entry(cls, user_id: str, km: float, date_added: datetime.date, notes: str = None, chat_id: str = None, chat_type: str = None) -> bool:
        """Добавить новую запись о пробежке"""
        logger.info(f"Adding new run entry for user {user_id}: {km} km, chat_id: {chat_id}, chat_type: {chat_type}")
        
        with Session() as session:
            try:
                # Проверяем максимальную дистанцию
                if km > 100:
                    logger.warning(f"Attempt to add run with distance {km} km for user {user_id}")
                    return False
                    
                log_entry = cls(
                    user_id=user_id,
                    km=km,
                    date_added=date_added,
                    notes=notes,
                    chat_id=chat_id,
                    chat_type=chat_type
                )
                logger.debug(f"Created log entry: {log_entry.__dict__}")
                
                session.add(log_entry)
                logger.debug("Added log entry to session")
                
                session.commit()
                logger.info(f"Successfully committed run entry for user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error adding run entry: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                session.rollback()
                return False

    @classmethod
    def get_user_total_km(cls, user_id: str, chat_type: str = None) -> float:
        """Получить общую дистанцию пользователя за текущий год"""
        logger.info(f"Getting total km for user {user_id}, chat_type: {chat_type}")
        
        with Session() as session:
            try:
                current_year = datetime.now().year
                query = session.query(cls).with_entities(
                    func.sum(cls.km)
                ).filter(
                    cls.user_id == user_id,
                    extract('year', cls.date_added) == current_year
                )
                
                if chat_type:
                    query = query.filter(cls.chat_type == chat_type)
                
                logger.debug(f"Executing query: {query}")
                result = query.scalar()
                logger.info(f"Total km for user {user_id}: {result or 0.0}")
                return float(result or 0.0)
            except Exception as e:
                logger.error(f"Error getting total km: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return 0.0

    @classmethod
    def get_top_runners(cls, limit: int = 10, year: int = None) -> list:
        """Получить топ бегунов за год"""
        if year is None:
            year = datetime.now().year
            
        with Session() as session:
            try:
                results = session.query(
                    cls.user_id,
                    func.sum(cls.km).label('total_km'),
                    func.count().label('runs_count'),
                    func.avg(cls.km).label('avg_km'),
                    func.max(cls.km).label('best_run')
                ).filter(
                    extract('year', cls.date_added) == year
                ).group_by(
                    cls.user_id
                ).order_by(
                    func.sum(cls.km).desc()
                ).limit(limit).all()
                
                return [{
                    'user_id': r.user_id,
                    'total_km': float(r.total_km or 0),
                    'runs_count': r.runs_count,
                    'avg_km': float(r.avg_km or 0),
                    'best_run': float(r.best_run or 0)
                } for r in results]
            except Exception as e:
                logger.error(f"Error getting top runners: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return []

    @classmethod
    def get_user_global_rank(cls, user_id: str, year: int = None) -> dict:
        """Получить позицию пользователя в глобальном рейтинге"""
        if year is None:
            year = datetime.now().year
            
        with Session() as session:
            try:
                # Подзапрос для получения общего километража каждого пользователя
                subq = session.query(
                    cls.user_id,
                    func.sum(cls.km).label('total_km')
                ).filter(
                    extract('year', cls.date_added) == year
                ).group_by(
                    cls.user_id
                ).subquery()
                
                # Получаем ранг пользователя
                rank_query = session.query(
                    func.row_number().over(
                        order_by=subq.c.total_km.desc()
                    ).label('rank'),
                    subq.c.user_id,
                    subq.c.total_km
                ).from_self().filter(
                    subq.c.user_id == user_id
                ).first()
                
                if rank_query:
                    total_users = session.query(
                        func.count(func.distinct(cls.user_id))
                    ).filter(
                        extract('year', cls.date_added) == year
                    ).scalar()
                    
                    return {
                        'rank': rank_query.rank,
                        'total_users': total_users,
                        'total_km': float(rank_query.total_km or 0)
                    }
                return {'rank': 0, 'total_users': 0, 'total_km': 0.0}
                
            except Exception as e:
                logger.error(f"Error getting user global rank: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {'rank': 0, 'total_users': 0, 'total_km': 0.0}

    @classmethod
    def get_personal_stats(cls, user_id: str, year: int = None) -> dict:
        """Получить подробную личную статистику пользователя"""
        if year is None:
            year = datetime.now().year
            
        with Session() as session:
            try:
                # Базовая статистика
                base_stats = cls.get_user_stats(user_id, year)
                
                # Дополнительная статистика
                additional_stats = session.query(
                    func.max(cls.km).label('longest_run'),
                    func.min(cls.km).label('shortest_run'),
                    func.avg(cls.km).label('average_run'),
                    func.count(func.distinct(cls.date_added)).label('active_days')
                ).filter(
                    cls.user_id == user_id,
                    extract('year', cls.date_added) == year
                ).first()
                
                # Статистика по месяцам
                monthly_stats = session.query(
                    extract('month', cls.date_added).label('month'),
                    func.sum(cls.km).label('monthly_km')
                ).filter(
                    cls.user_id == user_id,
                    extract('year', cls.date_added) == year
                ).group_by(
                    extract('month', cls.date_added)
                ).all()
                
                return {
                    **base_stats,
                    'longest_run': float(additional_stats.longest_run or 0),
                    'shortest_run': float(additional_stats.shortest_run or 0),
                    'average_run': float(additional_stats.average_run or 0),
                    'active_days': additional_stats.active_days or 0,
                    'monthly_progress': [
                        {'month': int(stat.month), 'km': float(stat.monthly_km or 0)}
                        for stat in monthly_stats
                    ]
                }
                
            except Exception as e:
                logger.error(f"Error getting personal stats: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {
                    'runs_count': 0,
                    'total_km': 0.0,
                    'avg_km': 0.0,
                    'longest_run': 0.0,
                    'shortest_run': 0.0,
                    'average_run': 0.0,
                    'active_days': 0,
                    'monthly_progress': []
                }

    @classmethod
    def get_user_runs(cls, user_id: str, limit: int = 5) -> List['RunningLog']:
        """Получает список последних пробежек пользователя"""
        with Session() as session:
            query = (
                session.query(cls)
                .filter(cls.user_id == user_id)
                .order_by(cls.date_added.desc())
                .limit(limit)
            )
            return query.all()

    @classmethod
    def get_user_stats(cls, user_id: str, year: int, month: int = None) -> dict:
        """Получить статистику пользователя"""
        with Session() as session:
            try:
                query = session.query(
                    func.count().label('runs_count'),
                    func.sum(cls.km).label('total_km'),
                    func.avg(cls.km).label('avg_km')
                ).filter(
                    cls.user_id == user_id,
                    extract('year', cls.date_added) == year
                )
                
                if month:
                    query = query.filter(extract('month', cls.date_added) == month)
                
                result = query.first()
                
                return {
                    'runs_count': result.runs_count or 0,
                    'total_km': float(result.total_km or 0),
                    'avg_km': float(result.avg_km or 0)
                }
            except Exception as e:
                logger.error(f"Error getting user stats: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {
                    'runs_count': 0,
                    'total_km': 0.0,
                    'avg_km': 0.0
                }

    @classmethod
    def get_best_stats(cls, user_id: str, chat_type: str = None) -> dict:
        """Получить лучшие показатели пользователя"""
        with Session() as session:
            try:
                query = session.query(
                    func.max(cls.km).label('best_run'),
                    func.count().label('total_runs'),
                    func.sum(cls.km).label('total_km')
                ).filter(
                    cls.user_id == user_id
                )
                
                if chat_type:
                    query = query.filter(cls.chat_type == chat_type)
                    
                result = query.first()
                
                return {
                    'best_run': float(result.best_run or 0),
                    'total_runs': result.total_runs or 0,
                    'total_km': float(result.total_km or 0)
                }
            except Exception as e:
                logger.error(f"Error getting best stats: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {'best_run': 0.0, 'total_runs': 0, 'total_km': 0.0}

    @classmethod
    def get_recent_runs(cls, user_id: str, chat_type: str = None, limit: int = 5):
        """Получить последние пробежки пользователя"""
        with Session() as session:
            query = session.query(cls).filter(
                cls.user_id == user_id
            )
            
            if chat_type:
                query = query.filter(cls.chat_type == chat_type)
                
            runs = query.order_by(
                cls.date_added.desc()
            ).limit(limit).all()

            return [{'date': run.date_added, 'distance_km': run.km} for run in runs]

    @classmethod
    def get_chat_stats(cls, chat_id: str, year: int = None, month: int = None, chat_type: str = None):
        """Получить статистику чата"""
        if year is None:
            year = datetime.now().year
            
        with Session() as session:
            try:
                query = session.query(
                    func.count().label('runs_count'),
                    func.sum(cls.km).label('total_km'),
                    func.avg(cls.km).label('avg_km'),
                    func.count(func.distinct(cls.user_id)).label('users_count')
                ).filter(
                    cls.chat_id == chat_id,
                    extract('year', cls.date_added) == year
                )
                
                if month:
                    query = query.filter(extract('month', cls.date_added) == month)
                
                if chat_type:
                    query = query.filter(cls.chat_type == chat_type)
                
                result = query.first()
                
                return {
                    'runs_count': result.runs_count or 0,
                    'total_km': float(result.total_km or 0),
                    'avg_km': float(result.avg_km or 0),
                    'users_count': result.users_count or 0
                }
                
            except Exception as e:
                logger.error(f"Error getting chat stats: {e}")
                return {
                    'runs_count': 0,
                    'total_km': 0.0,
                    'avg_km': 0.0,
                    'users_count': 0
                }

    @classmethod
    def get_chat_top_users(cls, chat_id: str, year: int = None, limit: int = 5, chat_type: str = None) -> list[dict]:
        """Получить топ пользователей чата"""
        if year is None:
            year = datetime.now().year
            
        with Session() as session:
            try:
                query = session.query(
                    cls.user_id,
                    func.sum(cls.km).label('total_km'),
                    func.count().label('runs_count'),
                    func.avg(cls.km).label('avg_km')
                ).join(
                    User, User.user_id == cls.user_id
                ).filter(
                    cls.chat_id == chat_id,
                    extract('year', cls.date_added) == year
                )
                
                if chat_type:
                    query = query.filter(cls.chat_type == chat_type)
                
                results = query.group_by(
                    cls.user_id
                ).order_by(
                    func.sum(cls.km).desc()
                ).limit(limit).all()
                
                return [{
                    'user_id': result.user_id,
                    'total_km': float(result.total_km or 0),
                    'runs_count': result.runs_count,
                    'avg_km': float(result.avg_km or 0)
                } for result in results]
                
            except Exception as e:
                logger.error(f"Error getting chat top users: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return []

    @classmethod
    def get_chat_stats_until_date(cls, chat_id: str, year: int, month: int, day: int, chat_type: str = None) -> dict:
        """Получить статистику чата до определенной даты"""
        with Session() as session:
            try:
                query = session.query(
                    func.sum(cls.km).label('total_km'),
                    func.count().label('runs_count'),
                    func.count(func.distinct(cls.user_id)).label('users_count')
                ).filter(
                    cls.chat_id == chat_id,
                    extract('year', cls.date_added) == year,
                    (
                        (extract('month', cls.date_added) < month) |
                        (
                            (extract('month', cls.date_added) == month) &
                            (extract('day', cls.date_added) <= day)
                        )
                    )
                )
                
                if chat_type:
                    query = query.filter(cls.chat_type == chat_type)
                
                result = query.first()
                
                return {
                    'total_km': float(result.total_km or 0),
                    'runs_count': result.runs_count or 0,
                    'users_count': result.users_count or 0
                }
                
            except Exception as e:
                logger.error(f"Error getting chat stats until date: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {
                    'total_km': 0.0,
                    'runs_count': 0,
                    'users_count': 0
                }

    @classmethod
    def get_chat_stats_all(cls, year: int = None) -> list[dict]:
        """Получить статистику по всем чатам за год"""
        if year is None:
            year = datetime.now().year
            
        with Session() as session:
            try:
                results = session.query(
                    cls.chat_id,
                    func.count().label('runs_count'),
                    func.sum(cls.km).label('total_km'),
                    func.avg(cls.km).label('avg_km')
                ).filter(
                    extract('year', cls.date_added) == year,
                    cls.chat_id.isnot(None)
                ).group_by(
                    cls.chat_id
                ).order_by(
                    func.sum(cls.km).desc()
                ).all()
                
                return [{
                    'chat_id': r.chat_id,
                    'runs_count': r.runs_count,
                    'total_km': float(r.total_km or 0),
                    'avg_km': float(r.avg_km or 0)
                } for r in results]
            except Exception as e:
                logger.error(f"Error getting chat stats: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return []

    @classmethod
    def get_chat_stats_month(cls, chat_id: str, year: int = None, month: int = None) -> dict:
        """Получить статистику чата за месяц"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
            
        with Session() as session:
            try:
                result = session.query(
                    func.count().label('runs_count'),
                    func.sum(cls.km).label('total_km'),
                    func.avg(cls.km).label('avg_km'),
                    func.count(func.distinct(cls.user_id)).label('users_count')
                ).filter(
                    cls.chat_id == chat_id,
                    extract('year', cls.date_added) == year,
                    extract('month', cls.date_added) == month
                ).first()
                
                return {
                    'runs_count': result.runs_count or 0,
                    'total_km': float(result.total_km or 0),
                    'avg_km': float(result.avg_km or 0),
                    'users_count': result.users_count or 0
                }
            except Exception as e:
                logger.error(f"Error getting chat month stats: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {
                    'runs_count': 0,
                    'total_km': 0.0,
                    'avg_km': 0.0,
                    'users_count': 0
                }

    @classmethod
    def get_total_stats(cls, year: int, month: int = None) -> dict:
        """Получить общую статистику за год или месяц"""
        with Session() as session:
            try:
                query = session.query(
                    func.count().label('runs_count'),
                    func.count(func.distinct(cls.user_id)).label('users_count'),
                    func.sum(cls.km).label('total_km'),
                    func.avg(cls.km).label('avg_km')
                ).filter(
                    extract('year', cls.date_added) == year
                )
                
                if month:
                    query = query.filter(extract('month', cls.date_added) == month)
                
                result = query.first()
                
                return {
                    'runs_count': result.runs_count or 0,
                    'users_count': result.users_count or 0,
                    'total_km': float(result.total_km or 0),
                    'avg_km': float(result.avg_km or 0)
                }
            except Exception as e:
                logger.error(f"Error getting total stats: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {
                    'runs_count': 0,
                    'users_count': 0,
                    'total_km': 0.0,
                    'avg_km': 0.0
                } 