from sqlalchemy import func, or_, extract, distinct
from sqlalchemy.orm import Session

class RunningLog:
    @classmethod
    def get_chat_stats(cls, chat_id: str, year: int = None, month: int = None, db = None):
        """Получает статистику чата с учетом всех пробежек участников"""
        if db is None:
            db = SessionLocal()
        
        try:
            query = db.query(
                cls.user_id,
                func.sum(cls.km).label('total_km'),
                func.count().label('runs_count'),
                func.avg(cls.km).label('avg_km'),
                func.max(cls.km).label('best_run')
            )
            
            # Фильтруем по году и месяцу
            if year:
                query = query.filter(extract('year', cls.date_added) == year)
            if month:
                query = query.filter(extract('month', cls.date_added) == month)
                
            # Включаем пробежки участников чата
            query = query.filter(
                or_(
                    cls.chat_id == chat_id,  # Пробежки в чате
                    cls.user_id.in_(  # Пробежки участников чата
                        db.query(cls.user_id)
                        .filter(cls.chat_id == chat_id)
                        .distinct()
                        .subquery()
                    )
                )
            )
            
            result = query.first()
            
            if not result:
                return {
                    'total_km': 0,
                    'runs_count': 0,
                    'avg_km': 0,
                    'best_run': 0,
                    'users_count': 0
                }
                
            # Получаем количество уникальных пользователей
            users_count = db.query(func.count(distinct(cls.user_id))).filter(
                or_(
                    cls.chat_id == chat_id,
                    cls.user_id.in_(
                        db.query(cls.user_id)
                        .filter(cls.chat_id == chat_id)
                        .distinct()
                        .subquery()
                    )
                )
            ).scalar()
            
            return {
                'total_km': float(result.total_km or 0),
                'runs_count': result.runs_count or 0,
                'avg_km': float(result.avg_km or 0),
                'best_run': float(result.best_run or 0),
                'users_count': users_count
            }
        finally:
            if db:
                db.close() 