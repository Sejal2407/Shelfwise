from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from config import db

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/api/wishlist/add', methods=['POST'])
def add_to_wishlist():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        wishlist = user.get('wishlist', [])
        already = any(item.get('bookId') == book_id if isinstance(item, dict) else item == book_id for item in wishlist)
        if already:
            return jsonify({"error": "Already in wishlist"}), 400
        db.users.update_one(
            {"email": user_email},
            {"$push": {"wishlist": {"bookId": book_id, "wishlistedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}}
        )
        return jsonify({"message": "Added to wishlist"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wishlist_bp.route('/api/wishlist/remove', methods=['POST'])
def remove_from_wishlist():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        db.users.update_one({"email": user_email}, {"$pull": {"wishlist": book_id}})
        return jsonify({"message": "Removed from wishlist"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wishlist_bp.route('/api/wishlist', methods=['GET'])
def get_wishlist():
    try:
        user_email = request.args.get('userId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        wishlist = user.get('wishlist', [])
        result = []
        for item in wishlist:
            book_id = item.get('bookId') if isinstance(item, dict) else item
            book = db.books.find_one({"_id": ObjectId(book_id)})
            if book:
                book['_id'] = str(book['_id'])
                result.append(book)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wishlist_bp.route('/api/wishlist/status', methods=['GET'])
def wishlist_status():
    try:
        user_email = request.args.get('userId')
        book_id = request.args.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"isWishlisted": False}), 200
        is_wishlisted = any(item.get('bookId') == book_id if isinstance(item, dict) else item == book_id for item in user.get('wishlist', []))
        return jsonify({"isWishlisted": is_wishlisted}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500