from database.models.team import Team
from database.session import Session
from utils.formatters import round_km
from datetime import datetime
from sqlalchemy import text, func
from database.models.user import User
from database.models.running_log import RunningLog

class TeamService:
    @staticmethod
    def create_team(team_name: str, created_by: str) -> Team:
        return Team.create(team_name, created_by)

    @staticmethod
    def get_team_stats(team_id: int) -> list[dict]:
        with Session() as session:
            result = session.execute(text("""
                SELECT u.username,
                       COALESCE(SUM(r.km), 0) as total_km
                FROM users u
                JOIN team_members tm ON u.user_id = tm.user_id
                LEFT JOIN running_log r ON u.user_id = r.user_id
                WHERE tm.team_id = :team_id
                AND r.date_added >= date('now', '-30 days')
                GROUP BY u.username
                ORDER BY total_km DESC
            """), {"team_id": team_id}).fetchall()
            
            return [
                {'username': row.username, 'total_km': round_km(row.total_km)}
                for row in result
            ]

    @staticmethod
    def get_user_teams_stats(user_id: str) -> list[dict]:
        teams = Team.get_user_teams(user_id)
        return [
            {
                'team': team,
                'stats': TeamService.get_team_stats(team.team_id)
            }
            for team in teams
        ] 