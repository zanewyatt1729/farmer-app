from flask import Blueprint, request, jsonify
from models import db, User, Product, Order, Message
from auth import require_login, get_current_user, register_user, login_user, logout_user

api_bp = Blueprint('api', __name__)

# Authentication routes
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if not all([username, password, role]):
        return jsonify({'error': 'Missing fields'}), 400
    return register_user(username, password, role)

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not all([username, password]):
        return jsonify({'error': 'Missing fields'}), 400
    return login_user(username, password)

@api_bp.route('/logout', methods=['POST'])
@require_login
def logout():
    return logout_user()

# Product routes
@api_bp.route('/products', methods=['GET'])
@require_login
def get_products():
    search = request.args.get('search')
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    products = query.all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'farmer_id': p.farmer_id
        })
    return jsonify(result)

@api_bp.route('/products', methods=['POST'])
@require_login
def add_product():
    user = get_current_user()
    if user.role != 'farmer':
        return jsonify({'error': 'Only farmers can add products'}), 403
    data = request.json
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    if not all([name, description, price]):
        return jsonify({'error': 'Missing fields'}), 400
    product = Product(name=name, description=description, price=price, farmer_id=user.id)
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added', 'id': product.id}), 201

# Order routes
@api_bp.route('/orders', methods=['GET'])
@require_login
def get_orders():
    user = get_current_user()
    if user.role == 'consumer':
        orders = Order.query.filter_by(consumer_id=user.id).all()
    elif user.role == 'farmer':
        # Get orders for farmer's products
        orders = Order.query.join(Product).filter(Product.farmer_id == user.id).all()
    else:
        orders = []
    result = []
    for o in orders:
        result.append({
            'id': o.id,
            'product_id': o.product_id,
            'quantity': o.quantity,
            'status': o.status,
            'created_at': o.created_at.isoformat()
        })
    return jsonify(result)

@api_bp.route('/orders', methods=['POST'])
@require_login
def place_order():
    user = get_current_user()
    if user.role != 'consumer':
        return jsonify({'error': 'Only consumers can place orders'}), 403
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    if not all([product_id, quantity]):
        return jsonify({'error': 'Missing fields'}), 400
    order = Order(consumer_id=user.id, product_id=product_id, quantity=quantity)
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order placed', 'id': order.id}), 201

# Message routes (chat)
@api_bp.route('/messages/<int:other_user_id>', methods=['GET'])
@require_login
def get_messages(other_user_id):
    user = get_current_user()
    messages = Message.query.filter(
        ((Message.sender_id == user.id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user.id))
    ).order_by(Message.timestamp.asc()).all()
    result = []
    for m in messages:
        result.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'receiver_id': m.receiver_id,
            'content': m.content,
            'timestamp': m.timestamp.isoformat()
        })
    return jsonify(result)

@api_bp.route('/messages/<int:other_user_id>', methods=['POST'])
@require_login
def send_message(other_user_id):
    user = get_current_user()
    data = request.json
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Message content required'}), 400
    message = Message(sender_id=user.id, receiver_id=other_user_id, content=content)
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Message sent', 'id': message.id}), 201
