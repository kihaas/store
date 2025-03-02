from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache


db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")  # Ограничение запросов
cache = Cache()