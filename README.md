# RunConnect Legacy

Телеграм бот для отслеживания беговых тренировок и участия в челленджах.

## Настройка

1. Создайте файл конфигурации:
```bash
cp config/config.example.py config/config.py
```

2. Обновите значения в `config/config.py`:
- `DATABASE_URL` - URL для подключения к PostgreSQL
- `BOT_TOKEN` - токен вашего Telegram бота
- `STABILITY_API_KEY` - ключ API Stability AI
- `ADMIN_IDS` - список ID администраторов бота

3. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
pip install -r requirements.txt
```

4. Запустите миграции:
```bash
alembic upgrade head
```

5. Запустите бота:
```bash
python runconnect_legacy/bot.py
``` 