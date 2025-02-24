from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Инициализация расширений
db = SQLAlchemy()  # ORM для работы с базой данных
login_manager = LoginManager()  # Управление сессиями пользователей
jwt = JWTManager()  # Работа с JWT-токенами
mail = Mail()  # Отправка писем
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")  # Ограничение запросов
cache = Cache()  # Кэширование данных