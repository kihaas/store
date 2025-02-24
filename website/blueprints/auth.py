from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import User
from website.extensions import db
from website.forms import RegistrationForm, LoginForm
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            return jsonify({"error": "Email уже зарегистрирован"}), 400

        hashed_password = generate_password_hash(form.password.data)
        confirmation_token = secrets.token_urlsafe(32)

        new_user = User(
            email=form.email.data,
            phone=form.phone.data,
            password_hash=hashed_password,
            confirmation_token=confirmation_token
        )
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id)
        return jsonify({"message": "Регистрация успешна", "access_token": access_token}), 201
    return jsonify(form.errors), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            access_token = create_access_token(identity=user.id)
            return jsonify({"message": "Вход успешен", "access_token": access_token}), 200
        return jsonify({"error": "Неверные учетные данные"}), 401
    return jsonify(form.errors), 400