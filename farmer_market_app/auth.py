from flask import session, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(username, password, role):
    if User.query.filter_by(username=username).first():
        return {'error': 'User already exists'}, 400
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return {'message': 'User registered successfully'}, 201

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['role'] = user.role
        return {'message': 'Login successful', 'role': user.role}, 200
    return {'error': 'Invalid credentials'}, 401

def logout_user():
    session.pop('user_id', None)
    session.pop('role', None)
    return {'message': 'Logout successful'}, 200

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def require_login(f):
    def wrapper(*args, **kwargs):
        if not get_current_user():
            return {'error': 'Authentication required'}, 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper
