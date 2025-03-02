from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from website.extensions import db, login_manager, jwt, mail, limiter, cache
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_cors import CORS


load_dotenv()


def create_app(config_name='testing'):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    CORS(app)

    try:
        app.config.from_object(f'config.{config_name.capitalize()}Config')
    except ImportError:
        raise RuntimeError(f"Конфигурация '{config_name}' не найдена")

    # Проверка обязательных переменных окружения
    app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'jwtsecretkey')

    # Настройки бд
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///store.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Настройки почты
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # Кэширование
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', 6379)

    if os.getenv('USE_REDIS', 'False') == 'True':
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_HOST'] = redis_host
        app.config['CACHE_REDIS_PORT'] = redis_port
    else:
        app.config['CACHE_TYPE'] = 'SimpleCache'

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    CSRFProtect(app)

    with app.app_context():
        db.create_all()

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/flask_shop.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask Shop startup')

    from website.blueprints.auth import auth_bp
    from website.blueprints.profile import profile_bp
    from website.blueprints.admin import admin_bp
    from website.blueprints.cart import cart_bp
    from website.blueprints.order import order_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(order_bp, url_prefix='/order')

    return app