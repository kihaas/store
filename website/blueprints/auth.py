from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from website import db
from website.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from website.services.auth_service import AuthService
from flask_cors import CORS
from flask import Flask
from website.models import User
from website.utils.email_utils import send_password_reset_email

# Создаем Blueprint для аутентификации
auth_bp = Blueprint('auth', __name__)
app = Flask(__name__)
CORS(app)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    form = RegistrationForm(data=data)

    # Валидация данных
    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    # Регистрация пользователя через сервис
    user, error = AuthService.register_user(
        login=form.login.data,
        email=form.email.data,
        phone=form.phone.data,
        password=form.password.data
    )
    if error:
        return jsonify({"error": error}), 400

    access_token = create_access_token(identity=str(user.id))  # Преобразуем id в строку
    return jsonify({"message": "Регистрация успешна", "access_token": access_token}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    # Проверяем, что переданы обязательные данные
    if not data or not data.get('password'):
        return jsonify({"error": "Необходимо указать пароль и один из параметров: login, email или phone"}), 400

    user = None
    if data.get('login'):
        user = User.query.filter_by(login=data.get('login')).first()
    elif data.get('email'):
        user = User.query.filter_by(email=data.get('email')).first()
    elif data.get('phone'):
        user = User.query.filter_by(phone=data.get('phone')).first()
    else:
        return jsonify({"error": "Необходимо указать login, email или phone"}), 400
    if user and user.check_password(data.get('password')):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Вход успешен",
            "access_token": access_token,
            "user_id": user.id,
            "email": user.email,
            "login": user.login,
            "phone": user.phone
        }), 200
    else:
        return jsonify({"error": "Неверные данные для входа"}), 401

@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    form = ForgotPasswordForm(data=data)

    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    user = User.query.filter_by(email=form.email.data).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    send_password_reset_email(user)
    return jsonify({"message": "Код для восстановления пароля отправлен на email"}), 200

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    form = ResetPasswordForm(data=data)

    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    user = User.query.filter_by(email=form.email.data).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    if form.code.data != user.reset_code:
        return jsonify({"error": "Неверный код"}), 400

    user.set_password(form.new_password.data)
    db.session.commit()
    return jsonify({"message": "Пароль успешно изменен"}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Выход выполнен, токен больше не используйте"}), 200