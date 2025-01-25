from database.models.challenge import Challenge
from database.models.user import User
from database.models.running_log import RunningLog
from database.session import Session
from utils.formatters import round_km
from datetime import datetime, date
from sqlalchemy import func, text, extract

class ChallengeService:
    @staticmethod
    def get_active_challenges() -> list[dict]:
        """Получение списка активных челленджей"""
        with Session() as session:
            results = session.query(
                Challenge,
                func.count(text('challenge_participants.user_id')).label('participants_count')
            ).outerjoin(
                'challenge_participants'
            ).filter(
                Challenge.end_date >= func.current_date()
            ).group_by(
                Challenge.challenge_id
            ).order_by(
                Challenge.start_date
            ).all()
            
            return [
                {
                    'id': challenge.challenge_id,
                    'title': challenge.title,
                    'goal_km': round_km(challenge.goal_km),
                    'start_date': challenge.start_date,
                    'end_date': challenge.end_date,
                    'description': challenge.description,
                    'created_by': challenge.created_by,
                    'participants_count': participants_count
                }
                for challenge, participants_count in results
            ]

    @staticmethod
    def create_challenge(title: str, goal_km: float, start_date: date, 
                        end_date: date, description: str, created_by: str) -> Challenge:
        return Challenge.create(title, goal_km, start_date, end_date, description, created_by)

    @staticmethod
    def get_challenge_stats(challenge_id: int) -> list[dict]:
        with Session() as session:
            challenge = session.query(Challenge).get(challenge_id)
            if not challenge:
                return []
                
            results = session.query(
                User.username,
                func.coalesce(func.sum(RunningLog.km), 0).label('total_km'),
                func.count(func.distinct(RunningLog.date_added)).label('active_days')
            ).join(
                'challenge_participants'
            ).outerjoin(
                RunningLog,
                (User.user_id == RunningLog.user_id) &
                (RunningLog.date_added.between(challenge.start_date, challenge.end_date))
            ).filter(
                text('challenge_participants.challenge_id = :challenge_id')
            ).group_by(
                User.username
            ).order_by(
                func.sum(RunningLog.km).desc()
            ).params(
                challenge_id=challenge_id
            ).all()
            
            return [
                {
                    'username': result.username,
                    'total_km': round_km(result.total_km),
                    'active_days': result.active_days
                }
                for result in results
            ]

    @staticmethod
    def get_user_challenges(user_id: str) -> list[dict]:
        with Session() as session:
            results = session.query(
                Challenge,
                func.coalesce(func.sum(RunningLog.km), 0).label('total_km')
            ).join(
                'challenge_participants'
            ).outerjoin(
                RunningLog,
                (text('challenge_participants.user_id = running_log.user_id')) &
                (RunningLog.date_added.between(Challenge.start_date, Challenge.end_date))
            ).filter(
                text('challenge_participants.user_id = :user_id')
            ).group_by(
                Challenge.challenge_id
            ).order_by(
                Challenge.end_date.desc()
            ).params(
                user_id=user_id
            ).all()
            
            return [
                {
                    'challenge': challenge,
                    'total_km': round_km(total_km)
                }
                for challenge, total_km in results
            ]

    @staticmethod
    def ensure_yearly_challenge(chat_id: str, year: int) -> Challenge:
        """Создает или получает годовой челлендж чата"""
        # Проверяем, существует ли уже системный челлендж для этого чата и года
        challenge = Challenge.get_system_challenge(chat_id, year)
        
        if not challenge:
            # Создаем новый системный челлендж
            title = f"Годовая цель {year}"
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            challenge_id = Challenge.create(
                title=title,
                goal_km=0,  # Начальная цель
                start_date=start_date,
                end_date=end_date,
                chat_id=chat_id,
                is_system=True
            )
            
            challenge = Challenge.get_by_id(challenge_id)
            
        return challenge

    @staticmethod
    def auto_join_user(user_id: str, chat_id: str) -> None:
        """Автоматически добавляет пользователя во все системные челленджи чата"""
        current_year = datetime.now().year
        # Присоединяем к текущему и следующему году
        for year in [current_year, current_year + 1]:
            challenge = ChallengeService.ensure_yearly_challenge(chat_id, year)
            if challenge:
                challenge.add_participant(user_id)

    @staticmethod
    def update_yearly_goal(chat_id: str, year: int, goal_km: float) -> bool:
        """Обновляет цель годового челленджа"""
        challenge = ChallengeService.ensure_yearly_challenge(chat_id, year)
        if challenge:
            challenge.update_goal(goal_km)
            return True
        return False 