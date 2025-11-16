import os

# Базовая конфигурация
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-for-tennis-aggregator')
DEBUG = True

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "app.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
