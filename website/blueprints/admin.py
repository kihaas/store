from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from website.models import User, Product, Order
from website.extensions import db

# Создаем Blueprint для административной панели
admin_bp = Blueprint('admin', __name__)

# 1. Добавление товара
@admin_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    """
    Добавление нового товара в базу данных.
    Доступно только для администраторов.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    # Получаем данные из запроса
    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Необходимо указать название и цену товара"}), 400

    # Создаем новый товар
    product = Product(
        name=data['name'],
        price=data['price'],
        description=data.get('description', ''),
        stock=data.get('stock', 0),
        image_url=data.get('image_url', '')
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Товар успешно добавлен", "product_id": product.id}), 201

# 2. Редактирование товара
@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def edit_product(product_id):
    """
    Редактирование товара по его ID.
    Доступно только для администраторов.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    # Получаем товар из базы данных
    product = Product.query.get_or_404(product_id)

    # Получаем данные для обновления
    data = request.json
    if not data:
        return jsonify({"error": "Нет данных для обновления"}), 400

    # Обновляем данные товара
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

    return jsonify({"message": "Товар успешно обновлён", "product_id": product.id})

# 3. Удаление товара
@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Удаление товара по его ID.
    Доступно только для администраторов.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    # Получаем товар из базы данных
    product = Product.query.get_or_404(product_id)

    # Удаляем товар
    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Товар успешно удалён", "product_id": product.id})

# 4. Просмотр всех заказов
@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def view_orders():
    """
    Просмотр всех заказов.
    Доступно только для администраторов.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    # Получаем все заказы
    orders = Order.query.all()

    # Формируем список заказов для ответа
    order_list = []
    for order in orders:
        order_list.append({
            "order_id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at.isoformat()
        })

    return jsonify({"orders": order_list})

# 5. Обновление статуса заказа
@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """
    Обновление статуса заказа по его ID.
    Доступно только для администраторов.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"error": "Недостаточно прав"}), 403

    # Получаем заказ из базы данных
    order = Order.query.get_or_404(order_id)

    # Получаем новый статус из запроса
    data = request.json
    if not data or 'status' not in data:
        return jsonify({"error": "Необходимо указать новый статус"}), 400

    new_status = data['status']
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        return jsonify({"error": f"Недопустимый статус. Допустимые статусы: {', '.join(valid_statuses)}"}), 400

    # Обновляем статус заказа
    order.status = new_status
    db.session.commit()

    return jsonify({"message": "Статус заказа успешно обновлён", "order_id": order.id, "new_status": new_status})