from sqlalchemy import Column, String, Float, Boolean, REAL
from sqlalchemy.orm import relationship
from database.base import Base
from database.session import Session

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String)
    yearly_goal = Column(REAL, nullable=True)
    yearly_progress = Column(REAL, nullable=True)
    goal_km = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    chat_type = Column(String, default='group')  # 'private' или 'group'

    # Отношение к пробежкам
    runs = relationship("RunningLog", back_populates="user")

    @classmethod
    def get_by_id(cls, user_id: str) -> 'User':
        """Получить пользователя по ID"""
        with Session() as session:
            return session.query(cls).filter(cls.user_id == user_id).first()

    @classmethod
    def create(cls, user_id: str, username: str, chat_type: str = 'group') -> 'User':
        """Создать нового пользователя"""
        with Session() as session:
            user = cls(user_id=user_id, username=username, chat_type=chat_type)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def save(self):
        """Сохранить изменения пользователя"""
        with Session() as session:
            session.merge(self)
            session.commit()

    def update(self, **kwargs):
        """Обновить атрибуты пользователя"""
        with Session() as session:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            session.merge(self)
            session.commit()

    def is_private(self) -> bool:
        """Проверить, является ли пользователь индивидуальным"""
        return self.chat_type == 'private' 