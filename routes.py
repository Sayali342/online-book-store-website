from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Book, CartItem

# ---------------- BLUEPRINTS ----------------
auth_bp = Blueprint("auth_bp", __name__)
book_bp = Blueprint("book_bp", __name__)
cart_bp = Blueprint("cart_bp", __name__)
admin_bp = Blueprint("admin_bp", __name__)

# ---------------- AUTH ROUTES ----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = generate_password_hash(data["password"])
    user = User(
        username=data["username"],
        email=data["email"],
        password=hashed_pw,
        role="user"
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "role": user.role})


# ---------------- BOOK ROUTES ----------------
@book_bp.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([{
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "price": b.price
    } for b in books])


# ---------------- CART ROUTES ----------------
@cart_bp.route("/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()

    existing_item = CartItem.query.filter_by(user_id=user_id, book_id=data["book_id"]).first()
    if existing_item:
        existing_item.quantity += data.get("quantity", 1)
    else:
        item = CartItem(user_id=user_id, book_id=data["book_id"], quantity=data.get("quantity", 1))
        db.session.add(item)

    db.session.commit()
    return jsonify({"message": "Book added to cart"})


@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": c.id,
        "book": {
            "id": c.book.id,
            "title": c.book.title,
            "author": c.book.author,
            "price": c.book.price
        },
        "quantity": c.quantity
    } for c in items])


# ---------------- ADMIN ROUTES ----------------
@admin_bp.route("/admin/books", methods=["POST"])
@jwt_required()
def add_book():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data.get("title") or not data.get("author") or not data.get("price"):
        return jsonify({"error": "Missing book details"}), 400

    book = Book(
        title=data["title"],
        author=data["author"],
        price=float(data["price"])
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({"message": "Book added successfully"})


# Export blueprints
__all__ = ["auth_bp", "book_bp", "cart_bp", "admin_bp"]
