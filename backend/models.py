from werkzeug.security import generate_password_hash
from datetime import datetime,timedelta

class User:
    def __init__(self,full_name,member_id,email,password):
        self.full_name = full_name
        self.member_id = member_id
        self.email = email
        self.password = generate_password_hash(password)
        self.created_at = datetime.now()
    
    def to_dict(self):
        """Converts the object to a dictionary for MongoDB"""
        return {
            "fullName" : self.full_name,
            "memberId" : self.member_id,
            "email" : self.email,
            "password" : self.password,
            "role" : "member",
            "borrowedBooks" : [],
            "wishlist": [],
            "joinedAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
class Book:
    def __init__(self,title,author,isbn,publisher,cover,available,genre):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.cover = cover
        self.available = available
        self.genre = genre
        self.added_at = datetime.now()

    def to_dict(self):
        return {
            "title" : self.title,
            "author" : self.author,
            "isbn" : self.isbn,
            "publisher" : self.publisher,
            "cover" : self.cover,
            "available" : self.available,
            "genre" : self.genre
        }

class BorrowedBooks:
    def __init__(self, bookId, userId):
        self.bookId = bookId
        self.userId = userId
        self.borrowedDate = datetime.now()
        self.returnDate = self.borrowedDate + timedelta(days=7)
        self.status = "borrowed"

    def to_dict(self):
        return {
            "userId": self.userId,
            "bookId": self.bookId,
            "borrowDate": self.borrowedDate.strftime("%Y-%m-%d %H:%M:%S"),
            "returnDate": self.returnDate.strftime("%Y-%m-%d"),
            "actualReturnDate": None,  # ✅ empty until book is returned
            "status": self.status
        }