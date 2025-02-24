from flask import Flask, jsonify
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from website.extensions import db, login_manager, jwt, mail, limiter, cache
import logging
from logging.handlers import RotatingFileHandler
import os



# Загрузка переменных окружения
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object('store.config.DevelopmentConfig')

    # Дополнительные настройки из переменных окружения
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    CSRFProtect(app)  # Включение CSRF-защиты

    # Логирование
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

    # Регистрация Blueprint'ов
    from .blueprints.auth import auth_bp
    from .blueprints.profile import profile_bp
    from .blueprints.admin import admin_bp
    from .blueprints.cart import cart_bp
    from .blueprints.order import order_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(order_bp, url_prefix='/order')

    return app