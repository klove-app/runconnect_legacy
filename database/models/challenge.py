from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, ForeignKey, func, text
from sqlalchemy.orm import relationship
from database.base import Base
from database.session import Session
from datetime import datetime
from utils.formatters import round_km
import traceback
import logging

logger = logging.getLogger(__name__)

class Challenge(Base):
    __tablename__ = "challenges"

    challenge_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    goal_km = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    chat_id = Column(String, nullable=True)
    is_system = Column(Boolean, default=False)
    user_id = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_by = Column(String, nullable=True)

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

    @staticmethod
    def get_chat_participants(chat_id):
        """Получает список всех участников чата, которые когда-либо регистрировали пробежки"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT DISTINCT u.user_id, u.username
                FROM users u
                JOIN running_log r ON u.user_id = r.user_id
                WHERE r.chat_id = ?
            """, (chat_id,))
            
            return cursor.fetchall()
            
        finally:
            conn.close() 

    def save(self):
        """Сохраняет или обновляет челлендж в базе данных"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if self.challenge_id:
                # Обновляем существующий челлендж
                cursor.execute("""
                    UPDATE challenges
                    SET title = ?, goal_km = ?, start_date = ?, end_date = ?, chat_id = ?, is_system = ?
                    WHERE challenge_id = ?
                """, (
                    self.title,
                    self.goal_km,
                    self.start_date,
                    self.end_date,
                    self.chat_id,
                    1 if self.is_system else 0,
                    self.challenge_id
                ))
            else:
                # Создаем новый челлендж
                cursor.execute("""
                    INSERT INTO challenges (title, goal_km, start_date, end_date, chat_id, is_system)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.title,
                    self.goal_km,
                    self.start_date,
                    self.end_date,
                    self.chat_id,
                    1 if self.is_system else 0
                ))
                self.challenge_id = cursor.lastrowid
            
            conn.commit()
            
        finally:
            conn.close()

    @staticmethod
    def get_user_challenge(user_id, year):
        """Получает активный челлендж пользователя на указанный год"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            print(f"\n>>> Getting challenge for user {user_id} and year {year}")
            
            cursor.execute("""
                SELECT c.challenge_id, c.title, c.goal_km, c.start_date, c.end_date, c.chat_id, c.is_system
                FROM challenges c
                JOIN challenge_participants cp ON c.challenge_id = cp.challenge_id
                WHERE cp.user_id = ? 
                AND strftime('%Y', c.start_date) = ?
                AND c.is_system = 1
                ORDER BY c.start_date DESC
                LIMIT 1
            """, (user_id, str(year)))
            
            row = cursor.fetchone()
            print(f">>> Database returned: {row}")
            
            if row:
                challenge = Challenge(
                    challenge_id=row[0],
                    title=row[1],
                    goal_km=row[2],
                    start_date=row[3],
                    end_date=row[4],
                    chat_id=row[5],
                    is_system=bool(row[6])
                )
                print(f">>> Created challenge object: {challenge.__dict__}")
                return challenge
                
            print(">>> No challenge found, returning default")
            return Challenge(goal_km=0)
            
        finally:
            conn.close() 

    @staticmethod
    def get_chat_challenge(chat_id: str, year: int) -> 'Challenge':
        """Получает цель чата на указанный год"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Нормализуем chat_id (убираем префикс -100 если он есть)
            normalized_chat_id = chat_id.replace('-100', '')
            
            cursor.execute("""
                SELECT challenge_id, title, goal_km, start_date, end_date, chat_id, is_system
                FROM challenges 
                WHERE chat_id = ? 
                AND strftime('%Y', start_date) = ?
                AND is_system = 0
            """, (normalized_chat_id, str(year)))
            
            row = cursor.fetchone()
            if row:
                return Challenge(
                    challenge_id=row[0],
                    title=row[1],
                    goal_km=row[2],
                    start_date=row[3],
                    end_date=row[4],
                    chat_id=row[5],
                    is_system=bool(row[6])
                )
            return None
            
        finally:
            conn.close()

    @staticmethod
    def get_all_user_challenges(user_id):
        """Получает все активные цели пользователя"""
        with get_connection() as conn:
            cursor = conn.cursor()
            print(f">>> Getting all challenges for user {user_id}")
            
            # Добавляем отладочный запрос
            cursor.execute("SELECT * FROM challenge_participants WHERE user_id = ?", (user_id,))
            participants = cursor.fetchall()
            print(f">>> Found participants: {participants}")
            
            cursor.execute("SELECT * FROM challenges WHERE is_system = 1", ())
            challenges = cursor.fetchall()
            print(f">>> All system challenges: {challenges}")
            
            # Основной запрос
            cursor.execute("""
                SELECT c.challenge_id, c.title, c.goal_km, c.start_date, c.end_date, 
                       c.chat_id, c.is_system
                FROM challenges c
                JOIN challenge_participants cp ON c.challenge_id = cp.challenge_id
                WHERE cp.user_id = ? 
                AND c.is_system = 1
                ORDER BY c.start_date DESC
            """, (user_id,))
            
            challenges = []
            for row in cursor.fetchall():
                challenge = Challenge(
                    challenge_id=row[0],
                    title=row[1],
                    goal_km=row[2],
                    start_date=row[3],
                    end_date=row[4],
                    chat_id=row[5],
                    is_system=bool(row[6])
                )
                challenges.append(challenge)
            
            print(f">>> Found {len(challenges)} challenges")
            return challenges 

    @staticmethod
    def clear_user_challenges(user_id):
        """Очищает все личные цели пользователя"""
        with get_connection() as conn:
            cursor = conn.cursor()
            print(f">>> Clearing challenges for user {user_id}")
            
            try:
                # Сначала получаем ID всех личных целей пользователя
                cursor.execute("""
                    SELECT c.challenge_id
                    FROM challenges c
                    JOIN challenge_participants cp ON c.challenge_id = cp.challenge_id
                    WHERE cp.user_id = ? 
                    AND c.is_system = 1
                """, (user_id,))
                
                challenge_ids = [row[0] for row in cursor.fetchall()]
                print(f">>> Found {len(challenge_ids)} challenges to delete")
                
                if challenge_ids:
                    # Сначала удаляем записи из challenge_participants
                    placeholders = ','.join(['?' for _ in challenge_ids])
                    cursor.execute(f"""
                        DELETE FROM challenge_participants
                        WHERE challenge_id IN ({placeholders})
                    """, challenge_ids)
                    
                    # Затем удаляем сами челленджи
                    cursor.execute(f"""
                        DELETE FROM challenges
                        WHERE challenge_id IN ({placeholders})
                    """, challenge_ids)
                    
                    conn.commit()
                    print(f">>> Successfully deleted {len(challenge_ids)} challenges")
                    return True
                    
                return False
                
            except Exception as e:
                print(f">>> Error clearing challenges: {str(e)}")
                conn.rollback()
                raise 

    def get_year_progress(self):
        """Получает прогресс с начала года"""
        with get_connection() as conn:
            cursor = conn.cursor()
            
            if self.is_system:  # Для личной цели
                print(f">>> Getting year progress for personal challenge {self.challenge_id}")
                
                # Получаем user_id из challenge_participants
                cursor.execute("""
                    SELECT user_id 
                    FROM challenge_participants 
                    WHERE challenge_id = ?
                """, (self.challenge_id,))
                user_id = cursor.fetchone()
                
                if not user_id:
                    print(">>> No user_id found")
                    return 0.0
                    
                # Используем правильное название колонки date_added
                cursor.execute("""
                    SELECT COALESCE(SUM(km), 0)
                    FROM running_log
                    WHERE user_id = ?
                    AND strftime('%Y', date_added) = ?
                """, (user_id[0], self.start_date[:4]))
                
                result = cursor.fetchone()
                total_km = float(result[0]) if result else 0.0
                print(f">>> Year progress: {total_km} km")
                return total_km 