from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
from database.session import Session
from datetime import datetime

class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    @classmethod
    def create(cls, team_name: str, created_by: str) -> 'Team':
        with Session() as session:
            team = cls(
                team_name=team_name,
                created_by=created_by
            )
            session.add(team)
            session.commit()
            session.refresh(team)
            return team

    def add_member(self, user_id: str) -> None:
        with Session() as session:
            # Здесь нужно будет создать модель TeamMember
            session.execute(
                """
                INSERT INTO team_members (team_id, user_id, joined_at)
                VALUES (:team_id, :user_id, :joined_at)
                """,
                {
                    "team_id": self.team_id,
                    "user_id": user_id,
                    "joined_at": datetime.now()
                }
            )
            session.commit()

    @classmethod
    def get_user_teams(cls, user_id: str) -> list['Team']:
        with Session() as session:
            teams = session.execute(
                """
                SELECT t.* FROM teams t
                JOIN team_members tm ON t.team_id = tm.team_id
                WHERE tm.user_id = :user_id
                """,
                {"user_id": user_id}
            ).all()
            return [cls(
                team_id=t.team_id,
                team_name=t.team_name,
                created_by=t.created_by,
                created_at=t.created_at
            ) for t in teams] 