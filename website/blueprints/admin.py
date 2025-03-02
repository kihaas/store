from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from website.models import User, Product, Order, Log
from website.extensions import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    admin = User.query.get(user_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    users = User.query.all()
    users_list = [{
        "id": user.id,
        "login": user.login,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "is_blocked": user.is_blocked
    } for user in users]

    return jsonify({"users": users_list}), 200


@admin_bp.route('/users/<int:user_id>/block', methods=['POST'])
@jwt_required()
def block_user(user_id):
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    user = User.query.get_or_404(user_id)
    user.is_blocked = True
    db.session.commit()

    log_action(admin_id, f"Заблокирован пользователь {user.id} ({user.login})")
    return jsonify({"message": f"Пользователь {user.login} заблокирован"}), 200


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def change_user_role(user_id):

    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    user = User.query.get_or_404(user_id)
    data = request.json
    if 'role' not in data:
        return jsonify({"error": "Необходимо указать роль"}), 400

    user.role = data['role']
    db.session.commit()
    log_action(admin_id, f"Изменена роль пользователя {user.id} ({user.login}) на {user.role}")
    return jsonify({"message": f"Роль пользователя {user.login} изменена на {user.role}"}), 200


@admin_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    products = Product.query.all()
    products_list = [{
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "stock": product.stock,
        "image_url": product.image_url
    } for product in products]

    return jsonify({"products": products_list}), 200

@admin_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():

    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Необходимо указать название и цену товара"}), 400

    product = Product(
        name=data['name'],
        price=data['price'],
        description=data.get('description', ''),
        stock=data.get('stock', 0),
        image_url=data.get('image_url', '')
    )
    db.session.add(product)
    db.session.commit()

    # Логируем действие
    log_action(admin_id, f"Добавлен товар {product.id} ({product.name})")

    return jsonify({"message": "Товар успешно добавлен", "product_id": product.id}), 201

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):

    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    product = Product.query.get_or_404(product_id)
    data = request.json

    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']
    if 'stock' in data:
        product.stock = data['stock']
    if 'image_url' in data:
        product.image_url = data['image_url']

    db.session.commit()
    log_action(admin_id, f"Обновлен товар {product.id} ({product.name})")

    return jsonify({"message": "Товар успешно обновлён", "product_id": product.id}), 200

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    # Логируем действие
    log_action(admin_id, f"Удален товар {product.id} ({product.name})")

    return jsonify({"message": "Товар успешно удалён", "product_id": product.id}), 200


@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    orders = Order.query.all()
    orders_list = [{
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at.isoformat()
    } for order in orders]

    return jsonify({"orders": orders_list}), 200


@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    order = Order.query.get_or_404(order_id)
    data = request.json
    if 'status' not in data:
        return jsonify({"error": "Необходимо указать статус"}), 400

    order.status = data['status']
    db.session.commit()

    # Логируем действие
    log_action(admin_id, f"Обновлен статус заказа {order.id} на {order.status}")

    return jsonify({"message": f"Статус заказа {order.id} обновлен на {order.status}"}), 200


def log_action(admin_id, action):
    log = Log(admin_id=admin_id, action=action, timestamp=datetime.utcnow())
    db.session.add(log)
    db.session.commit()


@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    logs = Log.query.all()
    logs_list = [{
        "id": log.id,
        "admin_id": log.admin_id,
        "action": log.action,
        "timestamp": log.timestamp.isoformat()
    } for log in logs]

    return jsonify({"logs": logs_list}), 200
