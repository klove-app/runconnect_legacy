from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Boolean, ForeignKey, func, text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base
from database.session import Session
from utils.formatters import round_km
import traceback
import logging

logger = logging.getLogger(__name__)

class Challenge(Base):
    __tablename__ = "challenges"

    challenge_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(String(1000))
    start_date = Column(Date)
    end_date = Column(Date)
    goal_km = Column(Float)
    created_by = Column(String(255))
    chat_id = Column(String(255))
    is_system = Column(Boolean, default=False)
    user_id = Column(String, nullable=True)

    # Отношения
    participants = relationship("ChallengeParticipant", back_populates="challenge")

    @classmethod
    def create_personal_challenge(cls, title: str, goal_km: float, start_date: datetime, 
                                end_date: datetime, description: str, created_by: str) -> 'Challenge':
        """Создает персональный челлендж"""
        with Session() as session:
            challenge = cls(
                title=title,
                goal_km=round_km(goal_km),
                start_date=start_date,
                end_date=end_date,
                description=description,
                created_by=created_by
            )
            session.add(challenge)
            session.commit()
            session.refresh(challenge)
            return challenge

    def add_participant(self, user_id):
        """Добавляет участника в системный челлендж"""
        # Для системного челленджа не нужно явно добавлять участников,
        # так как учитываются все пользователи чата автоматически
        pass

    @classmethod
    def get_active_challenges(cls) -> list['Challenge']:
        """Получает список активных челленджей"""
        with Session() as session:
            try:
                current_date = datetime.now()
                return session.query(cls).filter(
                    cls.start_date <= current_date,
                    cls.end_date >= current_date
                ).order_by(cls.start_date.desc()).all()
            except Exception as e:
                logger.error(f"Error getting active challenges: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return []

    @classmethod
    def get_system_challenge(cls, chat_id: str, year: int) -> 'Challenge':
        """Получает системный челлендж для чата на указанный год"""
        with Session() as session:
            try:
                normalized_chat_id = chat_id.replace('-100', '')
                logger.info(f"Looking for challenge: chat_id={normalized_chat_id}, year={year}")
                
                challenge = session.query(cls).filter(
                    cls.chat_id == normalized_chat_id,
                    func.extract('year', cls.start_date) == year,
                    cls.is_system == True
                ).first()
                
                if challenge:
                    logger.info(f"Found challenge: {challenge.challenge_id}")
                return challenge
            except Exception as e:
                logger.error(f"Error getting system challenge: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return None

    @classmethod
    def create(cls, title: str, goal_km: float, start_date: datetime, 
               end_date: datetime, chat_id: str, is_system: bool = False) -> int:
        """Создает новый челлендж"""
        with Session() as session:
            try:
                challenge = cls(
                    title=title,
                    goal_km=goal_km,
                    start_date=start_date,
                    end_date=end_date,
                    chat_id=chat_id,
                    is_system=is_system
                )
                session.add(challenge)
                session.commit()
                return challenge.challenge_id
            except Exception as e:
                logger.error(f"Error creating challenge: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                session.rollback()
                raise

    def update_goal(self, new_goal_km: float) -> None:
        """Обновляет цель челленджа"""
        with Session() as session:
            try:
                self.goal_km = new_goal_km
                session.merge(self)
                session.commit()
            except Exception as e:
                logger.error(f"Error updating challenge goal: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                session.rollback()
                raise

    @classmethod
    def get_by_id(cls, challenge_id: int) -> 'Challenge':
        """Получает челлендж по ID"""
        with Session() as session:
            try:
                return session.query(cls).filter(cls.challenge_id == challenge_id).first()
            except Exception as e:
                logger.error(f"Error getting challenge by ID: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return None

    def get_participants_count(self) -> int:
        """Получает количество участников челленджа"""
        with Session() as session:
            try:
                normalized_chat_id = str(int(float(self.chat_id))).replace('-100', '') if self.chat_id else None
                
                if self.is_system and normalized_chat_id:
                    result = session.execute(text("""
                        SELECT COUNT(DISTINCT user_id)
                        FROM running_log
                        WHERE chat_id = :chat_id
                        AND date_added BETWEEN :start_date AND :end_date
                    """), {
                        "chat_id": normalized_chat_id,
                        "start_date": self.start_date,
                        "end_date": self.end_date
                    }).scalar()
                else:
                    result = session.execute(text("""
                        SELECT COUNT(*)
                        FROM challenge_participants
                        WHERE challenge_id = :challenge_id
                    """), {
                        "challenge_id": self.challenge_id
                    }).scalar()
                
                return int(result) if result is not None else 0
            except Exception as e:
                logger.error(f"Error getting participants count: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return 0

    def get_total_progress(self) -> float:
        """Получает общий прогресс по челленджу"""
        with Session() as session:
            try:
                normalized_chat_id = str(int(float(self.chat_id))).replace('-100', '') if self.chat_id else None
                
                if self.is_system and normalized_chat_id:
                    result = session.execute(text("""
                        SELECT COALESCE(SUM(km), 0)
                        FROM running_log
                        WHERE chat_id = :chat_id
                        AND date_added BETWEEN :start_date AND :end_date
                    """), {
                        "chat_id": normalized_chat_id,
                        "start_date": self.start_date,
                        "end_date": self.end_date
                    }).scalar()
                else:
                    result = session.execute(text("""
                        SELECT COALESCE(SUM(r.km), 0)
                        FROM running_log r
                        JOIN challenge_participants cp ON r.user_id = cp.user_id
                        WHERE cp.challenge_id = :challenge_id
                        AND r.date_added BETWEEN :start_date AND :end_date
                    """), {
                        "challenge_id": self.challenge_id,
                        "start_date": self.start_date,
                        "end_date": self.end_date
                    }).scalar()
                
                return float(result) if result is not None else 0.0
            except Exception as e:
                logger.error(f"Error getting total progress: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return 0.0

    @classmethod
    def get_chat_participants(cls, chat_id: str) -> list[tuple]:
        """Получает список всех участников чата, которые когда-либо регистрировали пробежки"""
        with Session() as session:
            try:
                result = session.execute(text("""
                    SELECT DISTINCT u.user_id, u.username
                    FROM users u
                    JOIN running_log r ON u.user_id = r.user_id
                    WHERE r.chat_id = :chat_id
                """), {"chat_id": chat_id}).fetchall()
                return result
            except Exception as e:
                logger.error(f"Error getting chat participants: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return []

    def save(self) -> None:
        """Сохраняет или обновляет челлендж в базе данных"""
        with Session() as session:
            try:
                session.merge(self)
                session.commit()
            except Exception as e:
                logger.error(f"Error saving challenge: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                session.rollback()
                raise

    @classmethod
    def get_user_challenge(cls, user_id: str, year: int) -> 'Challenge':
        """Получает активный челлендж пользователя на указанный год"""
        with Session() as session:
            try:
                logger.info(f"Getting challenge for user {user_id} and year {year}")
                
                challenge = session.query(cls).join(
                    "challenge_participants"
                ).filter(
                    text("challenge_participants.user_id = :user_id"),
                    func.extract('year', cls.start_date) == year,
                    cls.is_system == True
                ).order_by(
                    cls.start_date.desc()
                ).params(
                    user_id=user_id
                ).first()
                
                logger.info(f"Found challenge: {challenge.challenge_id if challenge else None}")
                return challenge or cls(goal_km=0)
            except Exception as e:
                logger.error(f"Error getting user challenge: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return cls(goal_km=0)

    @classmethod
    def get_chat_challenge(cls, chat_id: str, year: int) -> 'Challenge':
        """Получает цель чата на указанный год"""
        with Session() as session:
            try:
                normalized_chat_id = chat_id.replace('-100', '')
                
                return session.query(cls).filter(
                    cls.chat_id == normalized_chat_id,
                    func.extract('year', cls.start_date) == year,
                    cls.is_system == False
                ).first()
            except Exception as e:
                logger.error(f"Error getting chat challenge: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return None

    @classmethod
    def get_all_user_challenges(cls, user_id: str) -> list['Challenge']:
        """Получает все активные цели пользователя"""
        with Session() as session:
            try:
                logger.info(f"Getting all challenges for user {user_id}")
                
                # Отладочные запросы через SQLAlchemy
                participants = session.query(text("*")).from_self().filter(
                    text("user_id = :user_id")
                ).params(user_id=user_id).all()
                logger.info(f"Found participants: {participants}")
                
                system_challenges = session.query(cls).filter(cls.is_system == True).all()
                logger.info(f"All system challenges: {len(system_challenges)}")
                
                # Основной запрос
                challenges = session.query(cls).join(
                    "challenge_participants"
                ).filter(
                    text("challenge_participants.user_id = :user_id"),
                    cls.is_system == True
                ).order_by(
                    cls.start_date.desc()
                ).params(
                    user_id=user_id
                ).all()
                
                logger.info(f"Found {len(challenges)} challenges")
                return challenges
            except Exception as e:
                logger.error(f"Error getting all user challenges: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return []

    @classmethod
    def clear_user_challenges(cls, user_id: str) -> bool:
        """Очищает все личные цели пользователя"""
        with Session() as session:
            try:
                logger.info(f"Clearing challenges for user {user_id}")
                
                # Получаем ID всех личных целей пользователя
                challenge_ids = session.query(cls.challenge_id).join(
                    "challenge_participants"
                ).filter(
                    text("challenge_participants.user_id = :user_id"),
                    cls.is_system == True
                ).params(
                    user_id=user_id
                ).all()
                
                challenge_ids = [c[0] for c in challenge_ids]
                logger.info(f"Found {len(challenge_ids)} challenges to delete")
                
                if challenge_ids:
                    # Удаляем записи из challenge_participants
                    session.execute(
                        text("DELETE FROM challenge_participants WHERE challenge_id IN :ids"),
                        {"ids": tuple(challenge_ids)}
                    )
                    
                    # Удаляем сами челленджи
                    session.query(cls).filter(cls.challenge_id.in_(challenge_ids)).delete(synchronize_session=False)
                    
                    session.commit()
                    logger.info(f"Successfully deleted {len(challenge_ids)} challenges")
                    return True
                
                return False
            except Exception as e:
                logger.error(f"Error clearing user challenges: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                session.rollback()
                return False

    def get_year_progress(self) -> float:
        """Получает прогресс с начала года"""
        with Session() as session:
            try:
                if not self.is_system:
                    return 0.0
                    
                logger.info(f"Getting year progress for personal challenge {self.challenge_id}")
                
                # Получаем user_id из challenge_participants
                user_id = session.execute(
                    text("SELECT user_id FROM challenge_participants WHERE challenge_id = :challenge_id"),
                    {"challenge_id": self.challenge_id}
                ).scalar()
                
                if not user_id:
                    logger.info("No user_id found")
                    return 0.0
                
                # Получаем сумму километров за год
                result = session.query(
                    func.coalesce(func.sum(RunningLog.km), 0.0)
                ).filter(
                    RunningLog.user_id == user_id,
                    func.extract('year', RunningLog.date_added) == func.extract('year', self.start_date)
                ).scalar()
                
                total_km = float(result)
                logger.info(f"Year progress: {total_km} km")
                return total_km
            except Exception as e:
                logger.error(f"Error getting year progress: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return 0.0

class ChallengeParticipant(Base):
    __tablename__ = "challenge_participants"

    challenge_id = Column(Integer, ForeignKey("challenges.challenge_id"), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), primary_key=True)
    progress = Column(Float, default=0)
    completed = Column(Boolean, default=False)

    # Отношения
    challenge = relationship("Challenge", back_populates="participants")
    user = relationship("User", back_populates="challenge_participations") 