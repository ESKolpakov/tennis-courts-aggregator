from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Инициализация расширений
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Загрузка конфигурации
    app.config.from_pyfile('../instance/config.py')
    
    # Инициализация базы данных
    db.init_app(app)
    
    # Регистрация маршрутов
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Создание таблиц базы данных
    with app.app_context():
        db.create_all()
    
    return app

# Убедимся, что все подмодули импортируются правильно
# Убираем импорт подмодулей чтобы избежать циклических зависимостей