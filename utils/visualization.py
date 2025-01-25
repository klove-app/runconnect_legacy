import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from database.session import Session
from database.models.user import User
from database.models.running_log import RunningLog
from utils.formatters import round_km
from datetime import datetime
from sqlalchemy import func, extract

def create_leaderboard_chart():
    with Session() as session:
        current_year = datetime.now().year

        results = session.query(
            User.username,
            func.coalesce(func.sum(RunningLog.km), 0).label('total_km')
        ).outerjoin(
            RunningLog,
            (User.user_id == RunningLog.user_id) &
            (extract('year', RunningLog.date_added) == current_year)
        ).group_by(
            User.username
        ).having(
            func.coalesce(func.sum(RunningLog.km), 0) > 0
        ).order_by(
            func.sum(RunningLog.km).desc()
        ).limit(10).all()

        if not results:
            return None

        # Создаем график
        plt.figure(figsize=(10, 6))
        plt.barh(
            [result.username for result in results],
            [result.total_km for result in results]
        )
        plt.xlabel('Километры')
        plt.ylabel('Участники')
        plt.title(f'Топ-10 бегунов {current_year}')

        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf 