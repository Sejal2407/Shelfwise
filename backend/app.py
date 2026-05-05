import os 
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from models import User,Book,BorrowedBooks
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from bson import ObjectId
from datetime import datetime, timedelta
import certifi

# Load secret variable like DB password
load_dotenv()

app = Flask(__name__)

# Enable CORS so React can talk to Flask 
CORS(app)

#Connect to MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = client.Shelfwise
    users_collection = db.users
    print("Connect to Database")
except Exception as e:
    print(f"Error connecting to Database . {e}")

#cloudinary setup
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

#basic Route to test if server is alive
@app.route('/')
def home():
    return jsonify({"status": "Online", "message": "Backend is running"})

#Signup Route
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        if not data.get('email') or "@" not in data.get('email'):
            return jsonify({"error": "A valid email is required"}), 400
        if len(data.get('password', '')) < 6:
            return jsonify({"error": "Password is too weak"}), 400
        print(f"Signup Data Received : {data}")
        if users_collection.find_one({"email": data.get('email')}):
            return jsonify({"error": "User with this email already registered"}), 400
        new_user_obj = User(
            full_name=data.get('fullName'),
            member_id=data.get('memberId'),
            email=data.get('email'),
            password=data.get('password')
        )
        users_collection.insert_one(new_user_obj.to_dict())
        return jsonify({
            "message": "Registration Successful",
            "user": {
                "fullName": data.get('fullName'),
                "email": data.get('email'),
                "role": data.get('role', 'member')
            }}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email') # React sends 'email'
    password = data.get('password') # React sends 'password'
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

# Fetching Members detail 
@app.route('/api/members', methods=['GET'])
def get_all_members():
    try:
        members = list(users_collection.find({'role': 'member'}, {"_id": 0, "password": 0}))
        return jsonify(members)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

#fetching Librarians Detail
@app.route('/api/librarian', methods=['GET'])
def get_all_librarian():
    librarians = list(users_collection.find({"role": "librarian"}, {"_id": 0, "password": 0}))
    return jsonify(librarians)

#Inserting new Librarian
@app.route('/api/librarian/add', methods=['POST'])
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

#Fetching Books Details
@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        books = list(db.books.find())
        for book in books:
            book['_id'] = str(book['_id'])
        return jsonify(books), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Inserting book data
@app.route('/api/books/add', methods=['POST'])
def add_book():
    try:
        #we are sending a file,that's why we use request.form instead of request.json
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

#deleting books
@app.route("/api/books/<id>", methods=['DELETE'])
def delete_book(id):
    try:
        result = db.books.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({"message": "Book deleted successfully"}), 200
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        print("Delete Error", e)
        return jsonify({"error": "Invalid ID format or server error"}), 500

#editing a book
@app.route('/api/books/<id>', methods=['PUT'])
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

#borrowing a book
@app.route('/api/books/borrow-status', methods=['GET'])
def borrow_status():
    try:
        user_email = request.args.get('userId')
        book_id = request.args.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"isBorrowed": False}), 200
        user_id = str(user['_id'])
        record = db.borrowedBooks.find_one({
            "userId": user_id,
            "bookId": book_id,
            "status": "borrowed"
        })
        return jsonify({"isBorrowed": bool(record)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/borrow', methods=['POST'])
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
        already_borrowed = db.borrowedBooks.find_one({
            "userId": user_id,
            "bookId": book_id,
            "status": "borrowed"
        })
        if already_borrowed:
            return jsonify({"error": "You have already borrowed this book"}), 400
        borrow_record = BorrowedBooks(bookId=book_id, userId=user_id)
        record_dict = borrow_record.to_dict()
        db.borrowedBooks.insert_one(record_dict)
        record_dict.pop('_id', None)
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"available": -1}})
        return jsonify(record_dict), 201
    except Exception as e:
        print("Borrow Error:", e)
        return jsonify({"error": "Some issue in borrowing"}), 500

#returning a book
@app.route('/api/books/return', methods=['POST'])
def return_book():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_id = str(user['_id'])
        borrow_record = db.borrowedBooks.find_one({
            "userId": user_id,
            "bookId": book_id,
            "status": "borrowed"
        })
        if not borrow_record:
            return jsonify({"error": "No active borrow record found"}), 404
        db.borrowedBooks.update_one(
            {"_id": borrow_record["_id"]},
            {"$set": {
                "status": "returned",
                "actualReturnDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            }}
        )
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"available": 1}})
        return jsonify({"message": "Book returned successfully"}), 200
    except Exception as e:
        print("Return Error:", e)
        return jsonify({"error": "Some issue in returning"}), 500

@app.route('/api/books/return-by-record', methods=['POST'])
def return_by_record():
    try:
        data = request.json
        borrow_id = data.get('borrowId')
        borrow_record = db.borrowedBooks.find_one({"_id": ObjectId(borrow_id)})
        if not borrow_record:
            return jsonify({"error": "Borrow record not found"}), 404
        if borrow_record.get("status") == "returned":
            return jsonify({"error": "Book already returned"}), 400
        db.borrowedBooks.update_one(
            {"_id": ObjectId(borrow_id)},
            {"$set": {
                "status": "returned",
                "actualReturnDate": datetime.now().strftime("%Y-%m-%d")
            }}
        )
        db.books.update_one(
            {"_id": ObjectId(borrow_record["bookId"])},
            {"$inc": {"available": 1}}
        )
        return jsonify({"message": "Book returned successfully"}), 200
    except Exception as e:
        print("Return by record error:", e)
        return jsonify({"error": str(e)}), 500

#fetching Borrowed Books details
@app.route('/api/borrowed', methods=['GET'])
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
        print("Error fetching borrowed books:", e)
        return jsonify({"error": str(e)}), 500

#wishlisting
@app.route('/api/wishlist/add', methods=['POST'])
def add_to_wishlist():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        wishlist = user.get('wishlist', [])
        already = any(
            item.get('bookId') == book_id if isinstance(item, dict) else item == book_id
            for item in wishlist
        )
        if already:
            return jsonify({"error": "Already in wishlist"}), 400
        # Store as object with bookId and date
        db.users.update_one(
            {"email": user_email},
            {"$push": {"wishlist": {
                "bookId": book_id,
                "wishlistedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }}}
        )
        return jsonify({"message": "Added to wishlist"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#removing from wishlist
@app.route('/api/wishlist/remove', methods=['POST'])
def remove_from_wishlist():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        db.users.update_one(
            {"email": user_email},
            {"$pull": {"wishlist": book_id}}
        )
        return jsonify({"message": "Removed from wishlist"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#fetching user's wishlist
@app.route('/api/wishlist', methods=['GET'])
def get_wishlist():
    try:
        user_email = request.args.get('userId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        wishlist = user.get('wishlist', [])
        result = []
        for item in wishlist:
            # Handle both old format (string) and new format (object)
            book_id = item.get('bookId') if isinstance(item, dict) else item
            book = db.books.find_one({"_id": ObjectId(book_id)})
            if book:
                book['_id'] = str(book['_id'])
                result.append(book)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wishlist/status', methods=['GET'])
def wishlist_status():
    try:
        user_email = request.args.get('userId')
        book_id = request.args.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"isWishlisted": False}), 200
        wishlist = user.get('wishlist', [])
        # Check inside object, handle both old and new format
        is_wishlisted = any(
            item.get('bookId') == book_id if isinstance(item, dict) else item == book_id
            for item in wishlist
        )
        return jsonify({"isWishlisted": is_wishlisted}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os 
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from models import User,Book,BorrowedBooks
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from bson import ObjectId
from datetime import datetime, timedelta
import certifi

# Load secret variable like DB password
load_dotenv()

app = Flask(__name__)

# Enable CORS so React can talk to Flask 
CORS(app)

#Connect to MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = client.Shelfwise
    users_collection = db.users
    print("Connect to Database")
except Exception as e:
    print(f"Error connecting to Database . {e}")

#cloudinary setup
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

#basic Route to test if server is alive
@app.route('/')
def home():
    return jsonify({"status": "Online", "message": "Backend is running"})

#Signup Route
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        if not data.get('email') or "@" not in data.get('email'):
            return jsonify({"error": "A valid email is required"}), 400
        if len(data.get('password', '')) < 6:
            return jsonify({"error": "Password is too weak"}), 400
        print(f"Signup Data Received : {data}")
        if users_collection.find_one({"email": data.get('email')}):
            return jsonify({"error": "User with this email already registered"}), 400
        new_user_obj = User(
            full_name=data.get('fullName'),
            member_id=data.get('memberId'),
            email=data.get('email'),
            password=data.get('password')
        )
        users_collection.insert_one(new_user_obj.to_dict())
        return jsonify({
            "message": "Registration Successful",
            "user": {
                "fullName": data.get('fullName'),
                "email": data.get('email'),
                "role": data.get('role', 'member')
            }}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email') # React sends 'email'
    password = data.get('password') # React sends 'password'
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

# Fetching Members detail 
@app.route('/api/members', methods=['GET'])
def get_all_members():
    try:
        members = list(users_collection.find({'role': 'member'}, {"_id": 0, "password": 0}))
        return jsonify(members)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

#fetching Librarians Detail
@app.route('/api/librarian', methods=['GET'])
def get_all_librarian():
    librarians = list(users_collection.find({"role": "librarian"}, {"_id": 0, "password": 0}))
    return jsonify(librarians)

#Inserting new Librarian
@app.route('/api/librarian/add', methods=['POST'])
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

#Fetching Books Details
@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        books = list(db.books.find())
        for book in books:
            book['_id'] = str(book['_id'])
        return jsonify(books), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Inserting book data
@app.route('/api/books/add', methods=['POST'])
def add_book():
    try:
        #we are sending a file,that's why we use request.form instead of request.json
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

#deleting books
@app.route("/api/books/<id>", methods=['DELETE'])
def delete_book(id):
    try:
        result = db.books.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({"message": "Book deleted successfully"}), 200
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        print("Delete Error", e)
        return jsonify({"error": "Invalid ID format or server error"}), 500

#editing a book
@app.route('/api/books/<id>', methods=['PUT'])
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

#borrowing a book
@app.route('/api/books/borrow-status', methods=['GET'])
def borrow_status():
    try:
        user_email = request.args.get('userId')
        book_id = request.args.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"isBorrowed": False}), 200
        user_id = str(user['_id'])
        record = db.borrowedBooks.find_one({
            "userId": user_id,
            "bookId": book_id,
            "status": "borrowed"
        })
        return jsonify({"isBorrowed": bool(record)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/borrow', methods=['POST'])
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
        already_borrowed = db.borrowedBooks.find_one({
            "userId": user_id,
            "bookId": book_id,
            "status": "borrowed"
        })
        if already_borrowed:
            return jsonify({"error": "You have already borrowed this book"}), 400
        borrow_record = BorrowedBooks(bookId=book_id, userId=user_id)
        record_dict = borrow_record.to_dict()
        db.borrowedBooks.insert_one(record_dict)
        record_dict.pop('_id', None)
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"available": -1}})
        return jsonify(record_dict), 201
    except Exception as e:
        print("Borrow Error:", e)
        return jsonify({"error": "Some issue in borrowing"}), 500

#returning a book
@app.route('/api/books/return', methods=['POST'])
def return_book():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_id = str(user['_id'])
        borrow_record = db.borrowedBooks.find_one({
            "userId": user_id,
            "bookId": book_id,
            "status": "borrowed"
        })
        if not borrow_record:
            return jsonify({"error": "No active borrow record found"}), 404
        db.borrowedBooks.update_one(
            {"_id": borrow_record["_id"]},
            {"$set": {
                "status": "returned",
                "actualReturnDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            }}
        )
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"available": 1}})
        return jsonify({"message": "Book returned successfully"}), 200
    except Exception as e:
        print("Return Error:", e)
        return jsonify({"error": "Some issue in returning"}), 500

@app.route('/api/books/return-by-record', methods=['POST'])
def return_by_record():
    try:
        data = request.json
        borrow_id = data.get('borrowId')
        borrow_record = db.borrowedBooks.find_one({"_id": ObjectId(borrow_id)})
        if not borrow_record:
            return jsonify({"error": "Borrow record not found"}), 404
        if borrow_record.get("status") == "returned":
            return jsonify({"error": "Book already returned"}), 400
        db.borrowedBooks.update_one(
            {"_id": ObjectId(borrow_id)},
            {"$set": {
                "status": "returned",
                "actualReturnDate": datetime.now().strftime("%Y-%m-%d")
            }}
        )
        db.books.update_one(
            {"_id": ObjectId(borrow_record["bookId"])},
            {"$inc": {"available": 1}}
        )
        return jsonify({"message": "Book returned successfully"}), 200
    except Exception as e:
        print("Return by record error:", e)
        return jsonify({"error": str(e)}), 500

#fetching Borrowed Books details
@app.route('/api/borrowed', methods=['GET'])
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
        print("Error fetching borrowed books:", e)
        return jsonify({"error": str(e)}), 500

#wishlisting
@app.route('/api/wishlist/add', methods=['POST'])
def add_to_wishlist():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        wishlist = user.get('wishlist', [])
        already = any(
            item.get('bookId') == book_id if isinstance(item, dict) else item == book_id
            for item in wishlist
        )
        if already:
            return jsonify({"error": "Already in wishlist"}), 400
        # Store as object with bookId and date
        db.users.update_one(
            {"email": user_email},
            {"$push": {"wishlist": {
                "bookId": book_id,
                "wishlistedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }}}
        )
        return jsonify({"message": "Added to wishlist"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#removing from wishlist
@app.route('/api/wishlist/remove', methods=['POST'])
def remove_from_wishlist():
    try:
        data = request.json
        user_email = data.get('userId')
        book_id = data.get('bookId')
        db.users.update_one(
            {"email": user_email},
            {"$pull": {"wishlist": book_id}}
        )
        return jsonify({"message": "Removed from wishlist"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#fetching user's wishlist
@app.route('/api/wishlist', methods=['GET'])
def get_wishlist():
    try:
        user_email = request.args.get('userId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        wishlist = user.get('wishlist', [])
        result = []
        for item in wishlist:
            # Handle both old format (string) and new format (object)
            book_id = item.get('bookId') if isinstance(item, dict) else item
            book = db.books.find_one({"_id": ObjectId(book_id)})
            if book:
                book['_id'] = str(book['_id'])
                result.append(book)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wishlist/status', methods=['GET'])
def wishlist_status():
    try:
        user_email = request.args.get('userId')
        book_id = request.args.get('bookId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"isWishlisted": False}), 200
        wishlist = user.get('wishlist', [])
        # Check inside object, handle both old and new format
        is_wishlisted = any(
            item.get('bookId') == book_id if isinstance(item, dict) else item == book_id
            for item in wishlist
        )
        return jsonify({"isWishlisted": is_wishlisted}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile', methods=['GET'])
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

        active_borrows = 0
        returned_books = 0
        total_fine = 0

        for record in records:
            status = record.get("status")
            if status == "borrowed":
                active_borrows += 1
                return_date = record.get("returnDate")
                if return_date:
                    due_date = datetime.strptime(return_date[:10], "%Y-%m-%d").date()
                    overdue_days = (today - due_date).days
                    if overdue_days > 0:
                        total_fine += overdue_days * 2
            elif status == "returned":
                returned_books += 1

        wishlist = user.get("wishlist", [])
        joined_at = user.get("joinedAt", "")
        joined_display = joined_at
        if joined_at:
            try:
                joined_display = datetime.strptime(joined_at, "%Y-%m-%d %H:%M:%S").strftime("%B %Y")
            except ValueError:
                joined_display = joined_at

        return jsonify({
            "fullName": user.get("fullName", ""),
            "memberId": user.get("memberId", ""),
            "email": user.get("email", ""),
            "role": user.get("role", "member").capitalize(),
            "joined": joined_display,
            "stats": {
                "borrowed": active_borrows,
                "returned": returned_books,
                "wishlist": len(wishlist),
                "fines": f"Rs. {total_fine:.2f}"
            }
        }), 200
    except Exception as e:
        print("Profile fetch error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile', methods=['DELETE'])
def delete_profile():
    try:
        data = request.json or {}
        user_email = data.get('userId')
        if not user_email:
            return jsonify({"error": "User email is required"}), 400

        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = str(user["_id"])
        active_records = list(db.borrowedBooks.find({
            "userId": user_id,
            "status": "borrowed"
        }))

        for record in active_records:
            book_id = record.get("bookId")
            if book_id:
                db.books.update_one(
                    {"_id": ObjectId(book_id)},
                    {"$inc": {"available": 1}}
                )

        db.borrowedBooks.delete_many({"userId": user_id})
        db.users.delete_one({"_id": user["_id"]})

        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        print("Profile delete error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        user_email = request.args.get('userId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = str(user['_id'])
        today = datetime.now().date()
        seven_days_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S") 

        # All borrow records for this user
        records = list(db.borrowedBooks.find({"userId": user_id}))

        total_borrowed = len(records)
        returned_this_month = 0
        total_fine = 0
        alerts = []
        recent_activity = []

        for record in records:
            book = db.books.find_one({"_id": ObjectId(record['bookId'])})
            book_name = book.get('title', 'Unknown') if book else 'Unknown'
            author = book.get('author', '') if book else ''
            publisher = book.get('publisher', '') if book else ''
            return_date = datetime.strptime(record['returnDate'][:10], "%Y-%m-%d").date()
            status = record.get('status')

            # Returned this month
            if status == 'returned':
                actual = record.get('actualReturnDate')
                if actual:
                    actual_date = datetime.strptime(actual[:10], "%Y-%m-%d").date()
                    if actual_date.month == today.month and actual_date.year == today.year:
                        returned_this_month += 1

            # Alerts and fines
            if status == 'borrowed':
                days_left = (return_date - today).days
                if days_left < 0:
                    overdue_days = abs(days_left)
                    fine = overdue_days * 2
                    total_fine += fine
                    alerts.append({
                        "type": "overdue",
                        "message": f'"{book_name}" is {overdue_days} day(s) overdue. Fine: ₹{fine}'
                    })
                elif days_left <= 2:
                    alerts.append({
                        "type": "due_soon",
                        "message": f'"{book_name}" is due in {days_left} day(s). Please return it soon!'
                    })

            # Only include in recent activity if within last 7 days
            borrow_date = record.get('borrowDate', '')
            if borrow_date >= seven_days_ago:
                recent_activity.append({
                    "type": "Borrow",
                    "bookName": book_name,
                    "author": author,
                    "publisher": publisher,
                    "date": borrow_date
                })

            # Only include return activity if within last 7 days
            if status == 'returned':
                actual_return = record.get('actualReturnDate') or record.get('returnDate', '')
                if actual_return >= seven_days_ago:
                    recent_activity.append({
                        "type": "Return",
                        "bookName": book_name,
                        "author": author,
                        "publisher": publisher,
                        "date": actual_return
                    })

        # Wishlist recent activity — outside the records loop
        wishlist = user.get('wishlist', [])
        for item in wishlist:
            if not isinstance(item, dict):
                continue  # skip old format entries without date
            wishlisted_at = item.get('wishlistedAt', '')
            if wishlisted_at >= seven_days_ago:
                book = db.books.find_one({"_id": ObjectId(item['bookId'])})
                if book:
                    recent_activity.append({
                        "type": "Wishlist",
                        "bookName": book.get('title'),
                        "author": book.get('author'),
                        "publisher": book.get('publisher'),
                        "date": wishlisted_at
                    })

        # Sort most recent first
        recent_activity.sort(key=lambda x: x['date'], reverse=True)

        return jsonify({
            "totalBorrowed": total_borrowed,
            "returnedThisMonth": returned_this_month,
            "totalFine": total_fine,
            "alerts": alerts,
            "recentActivity": recent_activity
        }), 200

    except Exception as e:
        print("Dashboard error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/librarian-dashboard',methods=['GET'])
def librarian_dashboard():
    try:
        today = datetime.now().date()
        seven_days_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")

        all_records = list(db.borrowedBooks.find())

        total_borrowed = sum(1 for r in all_records if r.get('status') == 'borrowed')
        total_returned = sum(1 for r in all_records if r.get('status') == 'returned')


        recent_activity = []
        for record in all_records:
            user = db.users.find_one({"_id":ObjectId(record['userId'])})
            book = db.books.find_one({"_id":ObjectId(record['bookId'])})
            if not book:
                continue
            borrow_date = record.get('borrowDate','')
            if borrow_date[:10] >= seven_days_ago:
                recent_activity.append({
                    "type":"Borrow",
                    "memberName": user.get('fullName', 'Unknown') if user else 'Unknown',
                    "bookName": book.get('title'),
                    "author": book.get('author'),
                    "publisher": book.get('publisher'),
                    "date": borrow_date
                })
            
            if record.get('status') == 'returned':
                actual_return = record.get('actualReturnDate','')
                if actual_return and actual_return[:10] >= seven_days_ago:
                    recent_activity.append({
                        "type": "Return",
                        "memberName": user.get('fullName', 'Unknown') if user else 'Unknown',
                        "bookName": book.get('title'),
                        "author": book.get('author'),
                        "publisher": book.get('publisher'),
                        "date": actual_return
                    })
        recent_activity.sort(key=lambda x:x['date'],reverse=True)
        return jsonify({
            "totalBorrwed" : total_borrowed,
            "totalReturned" : total_returned,
            "recentActivity":recent_activity[:20]
        }),200
    except Exception as e:
        print("Librarian Dashboard error : ",e)
        return jsonify({"error":str(e)}),500  

if __name__ == "__main__":
    app.run(debug=True, port=5000)
