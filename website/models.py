from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from website.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='user')
    referral_code = db.Column(db.String(20), unique=True, nullable=True)
    bonus_balance = db.Column(db.Float, default=0.0)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    bonus_transactions = db.relationship('BonusTransaction', backref='user', lazy=True, cascade='all, delete-orphan')

    referred_users = db.relationship('Referral', foreign_keys='Referral.referrer_id', backref='referring_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_referral_code(self):
        import secrets
        if not self.referral_code:
            self.referral_code = secrets.token_urlsafe(16)
        return self.referral_code

    def get_referral_link(self):
        return f"http://127.0.0.1:5000/register?ref={self.referral_code}"


class Referral(db.Model):
    __tablename__ = 'referrals'
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bonus_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='given_referrals')
    referred_user = db.relationship('User', foreign_keys=[referred_user_id], backref='received_referrals')


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_id = db.Column(db.String(50), nullable=True)
    payment_link = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BonusTransaction(db.Model):
    __tablename__ = 'bonus_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'credit' или 'debit'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ID администратора
    action = db.Column(db.String(500), nullable=False)  # Описание действия
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Время действия

    admin = db.relationship('User', backref='logs')  # Связь с пользователем