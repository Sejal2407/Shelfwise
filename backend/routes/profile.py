from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from config import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile_details():
    try:
        user_email = request.args.get('userId')
        if not user_email:
            return jsonify({"error": "User email is required"}), 400
        user = db.users.find_one({"email": user_email}, {"password": 0})
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = str(user['_id'])
        records = list(db.borrowedBooks.find({"userId": user_id}))
        today = datetime.now().date()
        active_borrows, returned_books, total_fine = 0, 0, 0

        for record in records:
            if record.get("status") == "borrowed":
                active_borrows += 1
                return_date = record.get("returnDate")
                if return_date:
                    due_date = datetime.strptime(return_date[:10], "%Y-%m-%d").date()
                    overdue_days = (today - due_date).days
                    if overdue_days > 0: total_fine += overdue_days * 2
            elif record.get("status") == "returned":
                returned_books += 1

        joined_at = user.get("joinedAt", "")
        if joined_at:
            try: joined_display = datetime.strptime(joined_at, "%Y-%m-%d %H:%M:%S").strftime("%B %Y")
            except ValueError: joined_display = joined_at
        else: joined_display = "N/A"

        return jsonify({
            "fullName": user.get("fullName", ""),
            "memberId": user.get("memberId", ""),
            "email": user.get("email", ""),
            "role": user.get("role", "member").capitalize(),
            "joined": joined_display,
            "stats": {"borrowed": active_borrows, "returned": returned_books, "wishlist": len(user.get("wishlist", [])), "fines": f"Rs. {total_fine:.2f}"}
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@profile_bp.route('/api/profile', methods=['DELETE'])
def delete_profile():
    try:
        data = request.json or {}
        user_email = data.get('userId')
        user = db.users.find_one({"email": user_email})
        if not user: return jsonify({"error": "User not found"}), 404
        user_id = str(user["_id"])
        active_records = list(db.borrowedBooks.find({"userId": user_id, "status": "borrowed"}))
        for record in active_records:
            if record.get("bookId"): db.books.update_one({"_id": ObjectId(record.get("bookId"))}, {"$inc": {"available": 1}})
        db.borrowedBooks.delete_many({"userId": user_id})
        db.users.delete_one({"_id": user["_id"]})
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500