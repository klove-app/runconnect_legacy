from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
from database.session import Session
from datetime import datetime

class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(255))
    created_by = Column(String(255))
    created_at = Column(DateTime)

    # Отношения
    members = relationship("TeamMember", back_populates="team")

class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = Column(Integer, ForeignKey("teams.team_id"), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), primary_key=True)
    joined_at = Column(DateTime)

    # Отношения
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")

    def __init__(self, team_id, user_id, joined_at):
        self.team_id = team_id
        self.user_id = user_id
        self.joined_at = joined_at

    @classmethod
    def create(cls, team_id, user_id):
        with Session() as session:
            team_member = cls(team_id=team_id, user_id=user_id, joined_at=datetime.now())
            session.add(team_member)
            session.commit()
            session.refresh(team_member)
            return team_member

    @classmethod
    def get_user_teams(cls, user_id):
        with Session() as session:
            teams = session.query(cls).filter(cls.user_id == user_id).all()
            # Загружаем связанные команды до закрытия сессии
            return [team.team for team in teams]

    def add_member(self, user_id):
        with Session() as session:
            team_member = TeamMember(team_id=self.team_id, user_id=user_id, joined_at=datetime.now())
            session.add(team_member)
            session.commit()
            session.refresh(team_member)
            return team_member

    def __repr__(self):
        return f"<TeamMember team_id={self.team_id}, user_id={self.user_id}>" 