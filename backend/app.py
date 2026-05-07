from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
from routes.books import books_bp
from routes.members import members_bp
from routes.wishlist import wishlist_bp
from routes.profile import profile_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
CORS(app)

# Register All Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(members_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return jsonify({"status": "Online", "message": "Backend is running"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)