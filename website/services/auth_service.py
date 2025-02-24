from werkzeug.security import generate_password_hash, check_password_hash
from website.models import User
from website.extensions import db
import re

class AuthService:
    @staticmethod
    def validate_phone(phone):
        # Валидация телефона для многонациональности (пример: +7, +380, +1 и т.д.)
        pattern = re.compile(r'^\+\d{1,3}\d{7,14}$')
        return bool(pattern.match(phone))

    @staticmethod
    def validate_email(email):
        # Простая валидация email
        pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        return bool(pattern.match(email))

    @staticmethod
    def register_user(email, phone, password, referral_code=None):
        if not AuthService.validate_phone(phone):
            return None, "Некорректный формат телефона"
        if not AuthService.validate_email(email):
            return None, "Некорректный формат email"
        if User.query.filter_by(email=email).first():
            return None, "Email уже зарегистрирован"
        if User.query.filter_by(phone=phone).first():
            return None, "Телефон уже зарегистрирован"
        user = User(email=email, phone=phone)
        user.set_password(password)
        if referral_code:
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer:
                user.referrer_id = referrer.id
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user, None
        return None, "Неверные данные для входа"