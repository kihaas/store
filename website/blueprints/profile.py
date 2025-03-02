from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from itsdangerous import URLSafeTimedSerializer
from website.models import User, Order
from website import db
from website.forms import UpdateProfileForm
from website.utils.email_utils import send_password_reset_email

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404

    return jsonify({
        "user_id": user.id,
        "email": user.email,
        "login": user.login,
        "phone": user.phone,
        "bonus_balance": user.bonus_balance,
        "referral_link": user.get_referral_link()
    }), 200


@profile_bp.route('/profile/update', methods=['POST'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404

    data = request.json
    form = UpdateProfileForm(data=data)

    if not form.validate():
        return jsonify({'errors': form.errors}), 400

    if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
        return jsonify({'error': 'Email уже используется'}), 400

    if form.login.data != user.login and User.query.filter_by(login=form.login.data).first():
        return jsonify({'error': 'Логин уже используется'}), 400

    user.email = form.email.data
    user.login = form.login.data
    user.phone = form.phone.data

    if form.password.data:
        user.set_password(form.password.data)

    db.session.commit()
    new_token = create_access_token(identity=user.id)

    return jsonify({'message': 'Профиль успешно обновлён', 'new_token': new_token})


@profile_bp.route('/profile/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"error": "Укажите email"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Пользователь с таким email не найден"}), 404

    # Отправка письма с ссылкой для восстановления
    send_password_reset_email(user)
    return jsonify({"message": "Ссылка для восстановления пароля отправлена на email"}), 200


@profile_bp.route('/profile/reset_password/confirm', methods=['POST'])
def reset_password_confirm():

    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not token or not new_password or not confirm_password:
        return jsonify({"error": "Необходимо указать токен, новый пароль и подтверждение пароля"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Пароли не совпадают"}), 400

    # Проверка токена
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)  # Токен действителен 1 час
    except:
        return jsonify({"error": "Неверный или просроченный токен"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    # Установка нового пароля
    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Пароль успешно изменен"}), 200


@profile_bp.route('/profile/orders', methods=['GET'])
@jwt_required()
def order_history():
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_id).all()

    orders_data = [
        {
            'order_id': order.id,
            'product_name': order.product_name,
            'quantity': order.quantity,
            'total_price': order.total_price,
            'status': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for order in orders
    ]

    return jsonify({'orders': orders_data})