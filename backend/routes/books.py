from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
import cloudinary.uploader
from config import db
from models import Book, BorrowedBooks

books_bp = Blueprint('books', __name__)

@books_bp.route('/api/books', methods=['GET'])
def get_books():
    try:
        books = list(db.books.find())
        for book in books:
            book['_id'] = str(book['_id'])
        return jsonify(books), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route('/api/books/add', methods=['POST'])
def add_book():
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        genre = request.form.get('genre')
        publisher = request.form.get('publisher')
        quantity = request.form.get('available')
        file_to_upload = request.files.get('cover')
        
        if not file_to_upload:
            return jsonify({"error": "Book cover image is required"}), 400
            
        upload_result = cloudinary.uploader.upload(file_to_upload, folder="selfwise_books")
        image_url = upload_result.get('secure_url')
        
        if db.books.find_one({"isbn": isbn}):
            return jsonify({"error": "Book with this ISBN already exists"}), 400
            
        new_book = Book(
            title=title, author=author, isbn=isbn,
            publisher=publisher, cover=image_url,
            available=int(quantity), genre=genre
        )
        db.books.insert_one(new_book.to_dict())
        return jsonify({"message": "Book Added Successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route("/api/books/<id>", methods=['DELETE'])
def delete_book(id):
    try:
        result = db.books.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({"message": "Book deleted successfully"}), 200
        return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid ID format or server error"}), 500

@books_bp.route('/api/books/<id>', methods=['PUT'])
def update_book(id):
    try:
        existing_book = db.books.find_one({"_id": ObjectId(id)})
        if not existing_book:
            return jsonify({"error": "Book not found"}), 404
        update_data = {
            "title": request.form.get('title'),
            "author": request.form.get('author'),
            "isbn": request.form.get('isbn'),
            "publisher": request.form.get('publisher'),
            "genre": request.form.get('genre'),
            "available": int(request.form.get('available'))
        }
        file_to_upload = request.files.get('cover')
        if file_to_upload and file_to_upload.filename != '':
            upload_result = cloudinary.uploader.upload(file_to_upload, folder="selfwise_books")
            update_data["cover"] = upload_result.get('secure_url')
        else:
            update_data["cover"] = existing_book.get('cover')
        db.books.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route('/api/books/borrow-status', methods=['GET'])
def borrow_status():
    try:
        user_email = request.args.get('userId')
        book_id = request.args.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"isBorrowed": False}), 200
        record = db.borrowedBooks.find_one({
            "userId": str(user['_id']),
            "bookId": book_id,
            "status": "borrowed"
        })
        return jsonify({"isBorrowed": bool(record)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route('/api/books/borrow', methods=['POST'])
def borrow_book():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        book = db.books.find_one({"_id": ObjectId(book_id)})
        if not book or book.get('available', 0) <= 0:
            return jsonify({"error": "Book is currently out of stock"}), 400
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_id = str(user['_id'])
        if db.borrowedBooks.find_one({"userId": user_id, "bookId": book_id, "status": "borrowed"}):
            return jsonify({"error": "You have already borrowed this book"}), 400
        borrow_record = BorrowedBooks(bookId=book_id, userId=user_id)
        record_dict = borrow_record.to_dict()
        db.borrowedBooks.insert_one(record_dict)
        record_dict.pop('_id', None)
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"available": -1}})
        return jsonify(record_dict), 201
    except Exception as e:
        return jsonify({"error": "Some issue in borrowing"}), 500

@books_bp.route('/api/books/return', methods=['POST'])
def return_book():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_id = str(user['_id'])
        borrow_record = db.borrowedBooks.find_one({"userId": user_id, "bookId": book_id, "status": "borrowed"})
        if not borrow_record:
            return jsonify({"error": "No active borrow record found"}), 404
        db.borrowedBooks.update_one(
            {"_id": borrow_record["_id"]},
            {"$set": {"status": "returned", "actualReturnDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        )
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"available": 1}})
        return jsonify({"message": "Book returned successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Some issue in returning"}), 500

@books_bp.route('/api/books/return-by-record', methods=['POST'])
def return_by_record():
    try:
        data = request.json
        borrow_id = data.get('borrowId')
        borrow_record = db.borrowedBooks.find_one({"_id": ObjectId(borrow_id)})
        if not borrow_record or borrow_record.get("status") == "returned":
            return jsonify({"error": "Record not found or already returned"}), 400
        db.borrowedBooks.update_one(
            {"_id": ObjectId(borrow_id)},
            {"$set": {"status": "returned", "actualReturnDate": datetime.now().strftime("%Y-%m-%d")}}
        )
        db.books.update_one({"_id": ObjectId(borrow_record["bookId"])}, {"$inc": {"available": 1}})
        return jsonify({"message": "Book returned successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route('/api/borrowed', methods=['GET'])
def get_borrowedBooks():
    try:
        user_email = request.args.get('userId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_id = str(user['_id'])
        records = list(db.borrowedBooks.find({"userId": user_id}))
        result = []
        for record in records:
            book = db.books.find_one({"_id": ObjectId(record['bookId'])})
            if book:
                result.append({
                    "isbn": book.get("isbn"),
                    "bookName": book.get("title"),
                    "author": book.get("author"),
                    "dateBorrowed": record.get("borrowDate")[:10],
                    "returnDate": record.get("returnDate"),
                    "status": record.get("status"),
                    "borrowId": str(record["_id"])
                })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500