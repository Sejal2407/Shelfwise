from flask import Blueprint, jsonify, request
from config import db, users_collection
from models import User

members_bp = Blueprint('members', __name__)

@members_bp.route('/api/members', methods=['GET'])
def get_all_members():
    try:
        members = list(users_collection.find({'role': 'member'}, {"_id": 0, "password": 0}))
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@members_bp.route('/api/librarian', methods=['GET'])
def get_all_librarian():
    librarians = list(users_collection.find({"role": "librarian"}, {"_id": 0, "password": 0}))
    return jsonify(librarians)

@members_bp.route('/api/librarian/add', methods=['POST'])
def add_librarian():
    try:
        data = request.json
        if db.users.find_one({"email": data.get('email')}):
            return jsonify({"error": "Email Already Exists"}), 400
        new_librarian = User(
            full_name=data.get('fullName'),
            member_id=data.get('memberId'),
            email=data.get('email'),
            password=data.get('password')
        )
        lib_dict = new_librarian.to_dict()
        lib_dict['role'] = 'librarian'
        db.users.insert_one(lib_dict)
        return jsonify({"message": "Librarian added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500