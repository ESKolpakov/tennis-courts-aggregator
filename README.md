# Агрегатор свободных теннисных кортов Москвы

## Описание
Веб-сервис, который в реальном времени собирает информацию о свободных временных слотах на теннисных кортах из разных клубов Москвы и отображает её в едином интерфейсе.

## Технологии
- Backend: Python (Flask)
- База данных: SQLite
- Frontend: HTML, CSS (Bootstrap), JavaScript
- Парсинг: Selenium/Playwright (будет добавлено позже)

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your_github_username/tennis-courts-aggregator.git
cd tennis-courts-aggregator
```
2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```
3. Установите зависимости:
```bash
pip install -r requirements.txt
```
4. Запустите приложение:
```bash
python run.py
```
5. Откройте в браузере: http://127.0.0.1:5000

## Структура проекта
app/ - основное приложение Flask
app/templates/ - HTML шаблоны
instance/ - конфигурационные файлы и база данных
tests/ - тесты (будут добавлены позже)
