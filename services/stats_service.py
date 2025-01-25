from database.db import get_connection
from utils.formatters import round_km
from datetime import datetime
from functools import lru_cache
from sqlalchemy.sql import text
from database.session import Session

class StatsService:
    @staticmethod
    @lru_cache(maxsize=100)
    def get_user_stats(user_id):
        with Session() as session:
            # Получаем данные пользователя
            query = text("""
                SELECT u.yearly_goal,
                       COALESCE(SUM(r.km), 0) as total_km,
                       COUNT(DISTINCT r.date_added) as activity_count
                FROM users u
                LEFT JOIN running_log r ON u.user_id = r.user_id
                AND EXTRACT(YEAR FROM r.date_added) = :year
                WHERE u.user_id = :user_id
                GROUP BY u.user_id, u.yearly_goal
            """)
            
            result = session.execute(query, {
                'year': datetime.now().year,
                'user_id': user_id
            }).fetchone()
            
            if not result:
                return None
                
            yearly_goal, total_km, activity_count = result
            total_km = round_km(total_km)
            yearly_goal = round_km(yearly_goal)
            
            # Расчет процента выполнения
            completion_percentage = round_km((total_km / yearly_goal * 100) if yearly_goal > 0 else 0)
            
            return {
                'yearly_goal': yearly_goal,
                'total_km': total_km,
                'activity_count': activity_count,
                'completion_percentage': completion_percentage
            }

    @staticmethod
    def invalidate_cache(user_id):
        """Инвалидация кэша при обновлении данных"""
        StatsService.get_user_stats.cache_clear()

    @staticmethod
    def get_leaderboard():
        with Session() as session:
            current_year = datetime.now().year
            
            query = text("""
                SELECT u.username, u.yearly_goal, COALESCE(SUM(r.km), 0) as total_km
                FROM users u
                LEFT JOIN running_log r ON u.user_id = r.user_id
                AND EXTRACT(YEAR FROM r.date_added) = :year
                GROUP BY u.username, u.yearly_goal
                HAVING u.yearly_goal > 0
                ORDER BY total_km DESC
            """)
            
            results = session.execute(query, {'year': current_year}).fetchall()
            
            return [
                {
                    'username': row[0],
                    'yearly_goal': round_km(row[1]),
                    'total_km': round_km(row[2])
                }
                for row in results
            ] 