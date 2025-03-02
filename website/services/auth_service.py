from werkzeug.security import generate_password_hash, check_password_hash
from website.models import User
from website.extensions import db
import re


class AuthService:
    @staticmethod
    def validate_phone(phone):
        pattern = re.compile(r'^\+\d{1,3}\d{7,14}$')
        return bool(pattern.match(phone))

    @staticmethod
    def validate_email(email):
        pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        return bool(pattern.match(email))

    @staticmethod
    def register_user(login, email, phone, password):
        if User.query.filter_by(login=login).first():
            return None, "Логин уже занят"
        if User.query.filter_by(email=email).first():
            return None, "Email уже зарегистрирован"
        if User.query.filter_by(phone=phone).first():
            return None, "Телефон уже зарегистрирован"

        hashed_password = generate_password_hash(password)
        user = User(login=login, email=email, phone=phone, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def login_user(login=None, email=None, phone=None, password=None):
        if login:
            user = User.query.filter_by(login=login).first()
        elif email:
            user = User.query.filter_by(email=email).first()
        elif phone:
            user = User.query.filter_by(phone=phone).first()
        else:
            return None, "Необходимо указать логин, email или телефон"

        # Проверка пароля
        if user and check_password_hash(user.password_hash, password):
            return user, None
        return None, "Неверные данные для входа"