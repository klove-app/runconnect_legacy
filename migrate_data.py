import sqlite3
import os
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

# Настраиваем логирование
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Импортируем Base перед моделями
from runconnect_legacy.database.base import Base

# Импортируем модели в правильном порядке
from runconnect_legacy.database.models.user import User
from runconnect_legacy.database.models.running_log import RunningLog
from runconnect_legacy.database.models.team import Team, TeamMember
from runconnect_legacy.database.models.challenge import Challenge, ChallengeParticipant
from runconnect_legacy.database.models.goals import GroupGoal, YearlyArchive
from runconnect_legacy.database.models.training import TrainingTemplate, TrainingPlan, ScheduledTraining

# Импортируем engine
from runconnect_legacy.database.session import engine

def create_tables():
    """Создает все таблицы в PostgreSQL."""
    logger.info("Создание таблиц в PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    logger.info("Таблицы созданы успешно")

def clear_postgresql_tables(pg_session: Session):
    """Очищает все таблицы в PostgreSQL перед миграцией."""
    logger.info("Очистка таблиц в PostgreSQL...")
    
    # Отключаем внешние ключи на время очистки
    pg_session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
    
    # Очищаем таблицы в правильном порядке
    tables = [
        YearlyArchive,
        GroupGoal,
        ChallengeParticipant,
        Challenge,
        TeamMember,
        Team,
        RunningLog,
        User,
        ScheduledTraining,
        TrainingPlan,
        TrainingTemplate
    ]
    
    for table in tables:
        logger.info(f"Очистка таблицы {table.__tablename__}")
        pg_session.query(table).delete()
    
    pg_session.commit()
    logger.info("Очистка таблиц завершена")

def migrate_data():
    """Мигрирует данные из SQLite в PostgreSQL."""
    # Путь к файлу SQLite относительно текущего скрипта
    sqlite_path = os.path.join(os.path.dirname(__file__), 'running_bot.db')
    logger.info(f"Using SQLite database at: {sqlite_path}")
    
    # Создаем таблицы если они не существуют
    create_tables()
    
    # Создаем подключение к SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Создаем сессию PostgreSQL
    pg_session = Session(engine)
    
    try:
        # Очищаем таблицы перед миграцией
        clear_postgresql_tables(pg_session)
        
        # Собираем всех уникальных пользователей
        logger.info("Collecting all unique users...")
        users_set = set()
        
        # Получаем пользователей из таблицы users
        sqlite_cursor.execute("SELECT user_id, username FROM users")
        for user_id, username in sqlite_cursor.fetchall():
            users_set.add((str(user_id), username))
        
        # Получаем пользователей из running_log
        sqlite_cursor.execute("SELECT DISTINCT user_id FROM running_log")
        for (user_id,) in sqlite_cursor.fetchall():
            if not any(u[0] == str(user_id) for u in users_set):
                users_set.add((str(user_id), f"User {user_id}"))
        
        # Получаем пользователей из team_members
        sqlite_cursor.execute("SELECT DISTINCT user_id FROM team_members")
        for (user_id,) in sqlite_cursor.fetchall():
            if not any(u[0] == str(user_id) for u in users_set):
                users_set.add((str(user_id), f"User {user_id}"))
        
        # Получаем пользователей из challenge_participants
        sqlite_cursor.execute("SELECT DISTINCT user_id FROM challenge_participants")
        for (user_id,) in sqlite_cursor.fetchall():
            if not any(u[0] == str(user_id) for u in users_set):
                users_set.add((str(user_id), f"User {user_id}"))
        
        # Мигрируем пользователей
        logger.info(f"Migrating {len(users_set)} users...")
        for user_id, username in users_set:
            # Получаем цели пользователя из SQLite
            sqlite_cursor.execute("""
                SELECT yearly_goal, goal_km 
                FROM users 
                WHERE user_id = ?
            """, (user_id,))
            user_goals = sqlite_cursor.fetchone()
            
            # Если у пользователя есть цель в yearly_goal, используем её
            # Если нет, проверяем goal_km
            # Если нигде нет цели, ставим 0
            goal = 0
            if user_goals:
                yearly_goal = user_goals[0] if user_goals[0] is not None else 0
                goal_km = user_goals[1] if user_goals[1] is not None else 0
                goal = yearly_goal if yearly_goal > 0 else goal_km
            
            user = User(
                user_id=user_id,
                username=username,
                yearly_goal=0,  # Не используем это поле больше
                yearly_progress=0,  # Прогресс будет пересчитан после миграции логов
                goal_km=goal,  # Используем значение из yearly_goal или goal_km
                is_active=True,
                chat_type='group'
            )
            pg_session.add(user)
        
        pg_session.commit()
        
        # После миграции логов обновляем yearly_progress
        logger.info("Updating yearly progress for users...")
        current_year = datetime.now().year
        for user_id, _ in users_set:
            # Считаем сумму километров за текущий год
            sqlite_cursor.execute("""
                SELECT COALESCE(SUM(km), 0)
                FROM running_log
                WHERE user_id = ?
                AND strftime('%Y', date_added) = ?
            """, (user_id, str(current_year)))
            
            yearly_progress = sqlite_cursor.fetchone()[0] or 0
            
            # Обновляем прогресс в PostgreSQL
            pg_session.execute(
                text("UPDATE users SET yearly_progress = :progress WHERE user_id = :user_id"),
                {"progress": yearly_progress, "user_id": user_id}
            )
        
        pg_session.commit()
        
        # Мигрируем running_log
        logger.info("Migrating running logs...")
        sqlite_cursor.execute("SELECT * FROM running_log")
        for row in sqlite_cursor.fetchall():
            # Преобразуем старую структуру в новую
            log = RunningLog(
                log_id=row[0],
                user_id=str(row[1]),
                km=row[2],
                date_added=datetime.strptime(row[3], '%Y-%m-%d').date() if row[3] else None,
                notes=row[4],
                chat_id=row[5],
                chat_type=row[6],
                # Новые поля устанавливаем в None или значения по умолчанию
                external_id=None,
                external_source=None,
                detailed_metrics=None,
                splits=None,
                elevation_data=None,
                average_heartrate=None,
                max_heartrate=None,
                perceived_effort=None,
                training_load=None,
                recovery_time=None
            )
            pg_session.add(log)
        
        pg_session.commit()
        
        # Мигрируем teams
        logger.info("Migrating teams...")
        sqlite_cursor.execute("SELECT * FROM teams")
        for row in sqlite_cursor.fetchall():
            team = Team(
                team_id=row[0],
                name=row[1],
                owner_id=str(row[2])
            )
            pg_session.add(team)
        
        pg_session.commit()
        
        # Мигрируем team_members
        logger.info("Migrating team members...")
        sqlite_cursor.execute("SELECT * FROM team_members")
        for row in sqlite_cursor.fetchall():
            member = TeamMember(
                team_id=row[0],
                user_id=str(row[1])
            )
            pg_session.add(member)
        
        pg_session.commit()
        
        # Мигрируем challenges
        logger.info("Migrating challenges...")
        sqlite_cursor.execute("SELECT * FROM challenges")
        for row in sqlite_cursor.fetchall():
            challenge = Challenge(
                challenge_id=row[0],
                title=row[1],
                description=row[2],
                start_date=datetime.strptime(row[3], '%Y-%m-%d').date() if row[3] else None,
                end_date=datetime.strptime(row[4], '%Y-%m-%d').date() if row[4] else None,
                goal_km=row[5],
                created_by=str(row[6]) if row[6] else None,
                chat_id=row[7],
                is_system=bool(row[8]) if row[8] is not None else False
            )
            pg_session.add(challenge)
        
        pg_session.commit()
        
        # Мигрируем challenge_participants
        logger.info("Migrating challenge participants...")
        sqlite_cursor.execute("SELECT * FROM challenge_participants")
        for row in sqlite_cursor.fetchall():
            participant = ChallengeParticipant(
                challenge_id=row[0],
                user_id=str(row[1]),
                progress=row[2] if row[2] is not None else 0.0,
                completed=False  # Новое поле в PostgreSQL
            )
            pg_session.add(participant)
        
        pg_session.commit()
        
        # Мигрируем group_goals
        logger.info("Migrating group goals...")
        sqlite_cursor.execute("SELECT * FROM group_goals")
        for row in sqlite_cursor.fetchall():
            goal = GroupGoal(
                goal_id=row[0],
                team_id=row[1],
                distance=row[2],
                start_date=datetime.strptime(row[3], '%Y-%m-%d').date() if row[3] else None,
                end_date=datetime.strptime(row[4], '%Y-%m-%d').date() if row[4] else None
            )
            pg_session.add(goal)
        
        pg_session.commit()
        
        # Мигрируем yearly_archive
        logger.info("Migrating yearly archives...")
        sqlite_cursor.execute("SELECT * FROM yearly_archive")
        for row in sqlite_cursor.fetchall():
            archive = YearlyArchive(
                user_id=str(row[0]),
                year=row[1],
                total_distance=row[2] if row[2] is not None else 0.0,
                total_time=row[3] if row[3] is not None else 0,
                total_runs=row[4] if row[4] is not None else 0
            )
            pg_session.add(archive)
        
        pg_session.commit()
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        pg_session.rollback()
        raise
    
    finally:
        sqlite_cursor.close()
        sqlite_conn.close()
        pg_session.close()

if __name__ == '__main__':
    migrate_data() 