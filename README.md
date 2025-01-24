# RunConnect Legacy

Телеграм бот для отслеживания беговых тренировок и участия в челленджах.

## Настройка

1. Создайте файл конфигурации:
```bash
cp config/config.example.py config/config.py
```

2. Обновите значения в `config/config.py` или добавьте их в переменные окружения:
- `DATABASE_URL` - URL для подключения к PostgreSQL
- `BOT_TOKEN` - токен вашего Telegram бота
- `STABILITY_API_KEY` - ключ API Stability AI
- `ADMIN_IDS` - список ID администраторов бота (через запятую)

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

## Структура проекта

Проект разделен на два репозитория:
1. [sl_tg_bot](https://github.com/klove-app/sl_tg_bot) - содержит код бота
2. **leamony.app** (текущий) - содержит веб-сайт с документацией

## Структура сайта

- `public/` - директория с файлами сайта
  - `index.html` - главная страница
  - `css/` - стили
  - `images/` - изображения
  - `js/` - скрипты
- `docs/` - исходные файлы документации в формате Markdown

## Локальная разработка

1. Клонировать репозиторий:
```bash
git clone https://github.com/klove-app/leamony.app.git
```

2. Открыть `index.html` в браузере или использовать локальный сервер

## Обновление документации

1. Редактируйте файлы в директории `docs/`
2. Обновите HTML версии документации
3. Создайте Pull Request

## Деплой

Сайт автоматически деплоится на Netlify при пуше в main ветку.

## Версионирование

В проекте используется семантическое версионирование. Текущая стабильная версия: v1.0.0

### Работа с версиями

Чтобы работать со стабильными версиями, используйте следующие команды:

1. Просмотр списка всех версий:
```bash
git tag -l -n
```

2. Просмотр кода определенной версии:
```bash
git checkout v1.0.0
```

3. Создание новой ветки от стабильной версии:
```bash
git checkout -b stable_version v1.0.0
```

4. Полный откат к стабильной версии:
```bash
git reset --hard v1.0.0
```

### Основные версии

- v1.0.0 - Стабильная версия с поддержкой генерации изображений и градацией цветов фона в зависимости от дистанции пробежки
- v1.1.0 - Стабильная версия с улучшениями:
  - Отображение дистанции с двумя знаками после запятой для большей точности
  - Поддержка системных шрифтов на macOS
  - Оптимизация статистики для более точного отображения данных
  - Улучшенное отображение команды /top с прогресс-барами и процентами
- v1.1.1 - Улучшения в отображении статистики:
  - Добавлены прогресс-бары для визуализации достижений в команде /top
  - Оптимизирована работа с общей статистикой без фильтрации по типу чата
  - Исправлено отображение дистанции с двумя знаками после запятой во всех сообщениях
- v1.1.2 - Улучшен интерфейс команды /top:
  - Компактное отображение статистики в одну строку
  - Добавлены эмодзи для лучшей визуализации
  - Упрощен формат вывода для каждого участника
  - Удалены избыточные прогресс-бары