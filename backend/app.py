import os
from flask import Flask, jsonify
from config import config
from extensions import db, jwt, cors, mail, cache


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    mail.init_app(app)
    cache.init_app(app) 

    from routes.auth    import auth_bp
    from routes.admin   import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    from routes.auth import BLOCKLIST

    @jwt.token_in_blocklist_loader
    def check_blocklist(jwt_header, jwt_data):
        return jwt_data["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_data):
        return jsonify({"error": "Token expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "Invalid token", "reason": reason}), 422

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Authorization required"}), 401

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    from models import User
    email = app.config.get("ADMIN_EMAIL", "admin@institute.edu")
    if not User.query.filter_by(role="admin").first():
        admin = User(email=email, role="admin", is_active=True)
        admin.set_password(os.getenv("ADMIN_PASSWORD", "admin@123"))
        db.session.add(admin)
        db.session.commit()
        print(f"[seed] Admin created → {email} / admin@123")


app    = create_app(os.getenv("FLASK_ENV", "development"))

from celery_worker import make_celery, register_tasks
celery = make_celery(app)
register_tasks(celery)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
