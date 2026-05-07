from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import User
from config import users_collection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        if not data.get('email') or "@" not in data.get('email'):
            return jsonify({"error": "A valid email is required"}), 400
        if len(data.get('password', '')) < 6:
            return jsonify({"error": "Password is too weak"}), 400
        if users_collection.find_one({"email": data.get('email')}):
            return jsonify({"error": "User with this email already registered"}), 400
        
        new_user_obj = User(
            full_name=data.get('fullName'),
            member_id=data.get('memberId'),
            email=data.get('email'),
            password=data.get('password')
        )
        users_collection.insert_one(new_user_obj.to_dict())
        return jsonify({"message": "Registration Successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user_data = users_collection.find_one({"email": email})
    if user_data and check_password_hash(user_data['password'], password):
        return jsonify({
            "message": "Login Successful",
            "user": {
                "fullName": user_data['fullName'],
                "email": user_data['email'],
                "role": user_data.get('role', 'member')
            }
        }), 200
    return jsonify({"error": "Invalid email or password"}), 401