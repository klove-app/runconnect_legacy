from database.db import get_connection
from utils.formatters import round_km
from datetime import datetime
from functools import lru_cache
from sqlalchemy import text
from sqlalchemy.engine import create_engine

engine = create_engine('sqlite:///database/db.sqlite')

class StatsService:
    @staticmethod
    @lru_cache(maxsize=100)
    def get_user_stats(user_id):
        """Получает статистику пользователя."""
        query = text("""
            SELECT u.goal_km,
                   COALESCE(SUM(r.km), 0) as total_km,
                   COUNT(r.log_id) as activity_count
            FROM users u
            LEFT JOIN running_log r ON u.user_id = r.user_id
            WHERE u.user_id = :user_id
            GROUP BY u.user_id, u.goal_km
        """)
        
        result = engine.execute(query, {"user_id": user_id}).fetchone()
        if not result:
            return None
        
        goal_km, total_km, activity_count = result
        
        goal_km = round_km(goal_km)
        total_km = round_km(total_km)
        
        completion_percentage = round_km((total_km / goal_km * 100) if goal_km > 0 else 0)
        
        return {
            'goal_km': goal_km,
            'total_km': total_km,
            'completion_percentage': completion_percentage,
            'activity_count': activity_count
        }

    @staticmethod
    def invalidate_cache(user_id):
        """Инвалидация кэша при обновлении данных"""
        StatsService.get_user_stats.cache_clear()

    @staticmethod
    def get_leaderboard():
        conn = get_connection()
        cursor = conn.cursor()
        current_year = datetime.now().year
        
        cursor.execute("""
            SELECT u.username, u.goal_km, COALESCE(SUM(r.km), 0) as total_km
            FROM users u
            LEFT JOIN running_log r ON u.user_id = r.user_id
            AND strftime('%Y', r.date_added) = ?
            GROUP BY u.username, u.goal_km
            HAVING u.goal_km > 0
            ORDER BY total_km DESC
        """, (str(current_year),))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'username': row[0],
                'goal_km': round_km(row[1]),
                'total_km': round_km(row[2]),
                'completion_percentage': round_km((row[2] / row[1] * 100) if row[1] > 0 else 0)
            }
            for row in results
        ]

    @staticmethod
    def get_users_with_goals():
        """Получает список пользователей с установленными целями."""
        query = text("""
            SELECT u.username, u.goal_km, COALESCE(SUM(r.km), 0) as total_km
            FROM users u
            LEFT JOIN running_log r ON u.user_id = r.user_id
            WHERE r.date_added >= date_trunc('year', CURRENT_DATE)
            GROUP BY u.username, u.goal_km
            HAVING u.goal_km > 0
            ORDER BY total_km DESC
        """)
        
        results = []
        for row in engine.execute(query):
            results.append({
                'username': row[0],
                'goal_km': round_km(row[1]),
                'total_km': round_km(row[2]),
                'completion_percentage': round_km((row[2] / row[1] * 100) if row[1] > 0 else 0)
            })
        
        return results 