from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
from routes import auth_bp, book_bp, cart_bp, admin_bp
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "change-this-secret"
    CORS(app)
    JWTManager(app)
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        # Default admin
        if not User.query.filter_by(email="admin@bookstore.com").first():
            admin = User(
                username="Admin",
                email="admin@bookstore.com",
                password=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
