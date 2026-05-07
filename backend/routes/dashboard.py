from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime, timedelta
from config import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        user_email = request.args.get('userId')
        user = db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = str(user['_id'])
        today = datetime.now().date()
        seven_days_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S") 

        # Fetch records for this specific user
        records = list(db.borrowedBooks.find({"userId": user_id}))

        total_borrowed = len(records)
        returned_this_month = 0
        total_fine = 0
        alerts = []
        recent_activity = []

        for record in records:
            book = db.books.find_one({"_id": ObjectId(record['bookId'])})
            if not book: continue
            
            book_name = book.get('title', 'Unknown')
            status = record.get('status')

            # Calculate returns for current month
            if status == 'returned':
                actual = record.get('actualReturnDate')
                if actual:
                    actual_date = datetime.strptime(actual[:10], "%Y-%m-%d").date()
                    if actual_date.month == today.month and actual_date.year == today.year:
                        returned_this_month += 1

            # Check for overdue books and fines[cite: 1]
            if status == 'borrowed':
                return_date_str = record.get('returnDate')
                if return_date_str:
                    return_date = datetime.strptime(return_date_str[:10], "%Y-%m-%d").date()
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
                            "message": f'"{book_name}" is due in {days_left} day(s).'
                        })

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


@dashboard_bp.route('/api/librarian-dashboard', methods=['GET'])
def librarian_dashboard():
    try:
        today = datetime.now().date()
        seven_days_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")

        all_records = list(db.borrowedBooks.find())
        
        # NEW: Added these to match your dashboard UI cards
        total_books_count = db.books.count_documents({})
        total_members_count = db.users.count_documents({"role": "member"})

        # Count borrowed and returned items[cite: 1]
        total_borrowed = sum(1 for r in all_records if r.get('status') == 'borrowed')
        total_returned = sum(1 for r in all_records if r.get('status') == 'returned')

        recent_activity = []
        for record in all_records:
            user = db.users.find_one({"_id": ObjectId(record['userId'])})
            book = db.books.find_one({"_id": ObjectId(record['bookId'])})
            if not book: continue
            
            # Formatting activity for the table in your screenshot[cite: 1]
            borrow_date = record.get('borrowDate', '')
            if borrow_date[:10] >= seven_days_ago:
                recent_activity.append({
                    "type": "Borrow",
                    "memberName": user.get('fullName', 'Unknown') if user else 'Unknown',
                    "bookName": book.get('title'),
                    "author": book.get('author'),
                    "publisher": book.get('publisher'),
                    "date": borrow_date
                })
            
            if record.get('status') == 'returned':
                actual_return = record.get('actualReturnDate', '')
                if actual_return and actual_return[:10] >= seven_days_ago:
                    recent_activity.append({
                        "type": "Return",
                        "memberName": user.get('fullName', 'Unknown') if user else 'Unknown',
                        "bookName": book.get('title'),
                        "author": book.get('author'),
                        "publisher": book.get('publisher'),
                        "date": actual_return
                    })

        recent_activity.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            "totalBooks": total_books_count,     # Matches card 1
            "totalMembers": total_members_count, # Matches card 2
            "totalBorrowed": total_borrowed,     # Matches card 3 (Fixed spelling)
            "totalBorrwed": total_borrowed,      # Keep typo key just in case frontend needs it[cite: 1]
            "totalReturned": total_returned,     # Matches card 4
            "recentActivity": recent_activity[:20]
        }), 200
    except Exception as e:
        print("Librarian Dashboard error:", e)
        return jsonify({"error": str(e)}), 500