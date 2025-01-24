# RunTracker Bot - Техническая документация

## 1. Обзор проекта

### 1.1 Описание
RunTracker Bot - это Telegram бот для отслеживания беговых тренировок, который позволяет пользователям записывать свои пробежки, отслеживать прогресс и участвовать в различных челленджах.

### 1.2 Основные возможности
- Запись пробежек с указанием дистанции
- Добавление фотографий к записям
- Отслеживание статистики (дневной, месячной, годовой)
- Установка и отслеживание целей
- Участие в командных соревнованиях
- Система челленджей
- Автоматическая генерация отчетов

### 1.3 Целевая аудитория
- Бегуны любого уровня подготовки
- Спортивные команды и клубы
- Организаторы беговых мероприятий

## 2. Технический стек

### 2.1 Основные технологии
- Python 3.x (основной язык разработки)
- pyTelegramBotAPI (telebot) для взаимодействия с Telegram API
- SQLAlchemy (ORM) для работы с базой данных
- SQLite в качестве базы данных

### 2.2 Дополнительные библиотеки
- `calendar` - для работы с датами
- `datetime` - для обработки временных меток
- `re` - для парсинга сообщений
- `os`, `sys` - для работы с файловой системой
- `traceback` - для отладки

### 2.3 Требования к окружению
- Python 3.8 или выше
- Минимум 512MB RAM
- 1GB свободного места на диске
- Доступ к интернету

## 3. Архитектура проекта

### 3.1 Структура проекта
```
sl_tg_bot/
├── main.py                  # Точка входа приложения
├── bot_instance.py          # Конфигурация и инициализация бота
├── config.py               # Конфигурационные параметры (токены, настройки)
├── requirements.txt        # Зависимости проекта
├── README.md              # Общее описание проекта
├── database/              # Модуль работы с базой данных
│   ├── base.py           # Базовая конфигурация БД
│   ├── logger.py         # Настройки логирования
│   └── models/           # Модели данных
│       ├── user.py       # Модель пользователя
│       └── running_log.py # Модель записей о пробежках
└── handlers/             # Обработчики команд и сообщений
    ├── admin_handlers.py     # Административные функции
    ├── base_handler.py       # Базовый класс обработчика
    ├── challenge_handlers.py # Управление челленджами
    ├── chat_handlers.py      # Обработка чат-команд
    ├── chat_goal_handlers.py # Управление целями чата
    ├── donate_handlers.py    # Обработка донатов
    ├── goal_handlers.py      # Управление личными целями
    ├── reset_handlers.py     # Сброс данных
    ├── stats_handlers.py     # Обработка статистики
    └── team_handlers.py      # Управление командами
```

### 3.2 Компоненты системы

#### 3.2.1 MessageHandler
Основной обработчик сообщений с следующими возможностями:

**Методы:**
- `handle_message(message)`: 
  - Обработка текстовых сообщений
  - Извлечение километража
  - Валидация данных
  - Сохранение записи
  - Формирование ответа

- `handle_photo_run(message)`:
  - Обработка фотографий
  - Извлечение подписи
  - Сохранение фото и данных
  - Формирование ответа

- `handle_profile(message, user_id)`:
  - Получение данных пользователя
  - Формирование статистики
  - Создание интерактивных кнопок
  - Отображение профиля

#### 3.2.2 AdminHandler
Обработчик административных функций:
- Управление пользователями
- Модерация контента
- Управление челленджами
- Генерация отчетов

#### 3.2.3 ChallengeHandler
Управление системой челленджей:
- Создание новых челленджей
- Отслеживание прогресса
- Начисление наград
- Формирование рейтингов

### 3.3 Модели данных

#### 3.3.1 User
```python
class User:
    user_id: str        # ID пользователя в Telegram
    username: str       # Имя пользователя
    goal_km: float     # Годовая цель в километрах
    created_at: datetime # Дата регистрации
    is_active: bool    # Статус активности
    role: str          # Роль пользователя (user/admin)
    team_id: str       # ID команды (если есть)
    settings: dict     # Пользовательские настройки
```

#### 3.3.2 RunningLog
```python
class RunningLog:
    id: int           # Уникальный идентификатор записи
    user_id: str      # ID пользователя
    km: float         # Дистанция пробежки
    date_added: date  # Дата записи
    notes: str        # Заметки к пробежке
    chat_id: str      # ID чата
    photo_id: str     # ID прикрепленного фото (если есть)
    weather: dict     # Погодные условия (опционально)
    location: dict    # Геолокация (опционально)
    duration: int     # Длительность в минутах (опционально)
```

## 4. Основные процессы

### 4.1 Регистрация пользователя
1. Пользователь запускает бота командой `/start`
2. Создается запись в таблице `User`
3. Отправляется приветственное сообщение
4. Предлагается установить цель

### 4.2 Запись пробежки
1. Пользователь отправляет сообщение с дистанцией
2. Система валидирует входные данные
3. Извлекается километраж и дополнительная информация
4. Создается запись в `RunningLog`
5. Обновляется статистика пользователя
6. Формируется и отправляется ответ с:
   - Подтверждением записи
   - Текущей статистикой
   - Прогрессом к цели
   - Мотивационным сообщением

### 4.3 Обработка фотографий
1. Пользователь отправляет фото с подписью
2. Система сохраняет фото
3. Извлекает километраж из подписи
4. Создает запись в базе данных
5. Связывает фото с записью
6. Отправляет подтверждение

## 5. API Endpoints (команды бота)

### 5.1 Основные команды
- `/start` - Начало работы с ботом
- `/help` - Список всех команд
- `/stats` - Просмотр статистики
- `/profile` - Личный кабинет
- `/setgoal <км>` - Установка годовой цели
- `/history` - История пробежек
- `/edit_last` - Редактирование последней записи

### 5.2 Команды челленджей
- `/challenges` - Список активных челленджей
- `/joinchallenge <ID>` - Присоединиться к челленджу
- `/leavechallenge <ID>` - Покинуть челлендж
- `/mychallenges` - Мои челленджи
- `/challenge_stats` - Статистика челленджей

### 5.3 Команды команд
- `/createteam <название>` - Создание команды
- `/jointeam <ID>` - Присоединение к команде
- `/leaveteam` - Покинуть команду
- `/teamstats` - Статистика команды
- `/invite <username>` - Пригласить в команду

### 5.4 Административные команды
- `/admin_stats` - Общая статистика бота
- `/broadcast` - Рассылка сообщений
- `/ban <user_id>` - Блокировка пользователя
- `/unban <user_id>` - Разблокировка пользователя
- `/report` - Генерация отчета

## 6. Безопасность

### 6.1 Аутентификация и авторизация
- Проверка Telegram ID пользователя
- Система ролей (пользователь/админ)
- Проверка прав доступа к командам

### 6.2 Валидация данных
- Проверка формата входных данных
- Защита от SQL-инъекций
- Ограничение размера загружаемых файлов

### 6.3 Конфиденциальность
- Шифрование чувствительных данных
- Безопасное хранение токенов
- Ограничение доступа к личным данным

## 7. Логирование

### 7.1 Системные логи
- Запуск/остановка бота
- Ошибки и исключения
- Проблемы с подключением

### 7.2 Пользовательские логи
- Действия пользователей
- Использование команд
- Изменение настроек

### 7.3 Статистические логи
- Количество активных пользователей
- Популярные команды
- Нагрузка на систему

## 8. Масштабирование

### 8.1 Вертикальное масштабирование
- Оптимизация кода
- Улучшение производительности БД
- Кэширование данных

### 8.2 Горизонтальное масштабирование
- Распределение нагрузки
- Репликация базы данных
- Балансировка запросов

## 9. Установка и развертывание

### 9.1 Требования к системе
1. Python 3.8+
2. pip (Python package manager)
3. Git
4. SQLite3
5. Доступ к интернету

### 9.2 Установка
```bash
# Клонирование репозитория
git clone https://github.com/username/sl_tg_bot.git
cd sl_tg_bot

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка конфигурации
cp config.example.py config.py
# Отредактируйте config.py, добавив токен бота

# Инициализация базы данных
python init_db.py

# Запуск бота
python main.py
```

### 9.3 Обновление
```bash
# Получение обновлений
git pull

# Обновление зависимостей
pip install -r requirements.txt

# Миграция базы данных (если требуется)
python migrate_db.py
```

## 10. Поддержка и сопровождение

### 10.1 Мониторинг
- Отслеживание состояния бота
- Мониторинг нагрузки
- Контроль ошибок

### 10.2 Резервное копирование
- Ежедневное резервное копирование БД
- Хранение логов
- Восстановление данных

### 10.3 Обновления
- Исправление ошибок
- Добавление новых функций
- Оптимизация производительности 