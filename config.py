import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    WTF_CSRF_ENABLED = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getcwd(), 'instance', os.getenv('DB_NAME', 'dev_db.sqlite'))}"
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Почтовый логин
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Почтовый пароль
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')  # Почтовый сервер
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))  # Почтовый порт (например, 587 для Gmail)
    MAIL_USE_TLS = True  # Использовать TLS для почты

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Почтовый логин
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Почтовый пароль
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')  # Почтовый сервер
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))  # Почтовый порт
    MAIL_USE_TLS = True  # Использовать TLS для почты

class TestingConfig(Config):
    #Конфигурация для тестирования
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Используется in-memory база данных для тестов
    TESTING = True  # Включение тестового режима
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SUPPRESS_SEND = True  # Отключает отправку почты во время тестирования
