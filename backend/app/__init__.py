from flask import Flask
from .config import Config
from .extensions import db, jwt, bcrypt, cors, cache


def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    cache.init_app(app)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    from .routes.company import company_bp
    app.register_blueprint(company_bp, url_prefix="/api/company")

    from .routes.student import student_bp
    app.register_blueprint(student_bp, url_prefix="/api/student")

    from .models import User, Company, Student, Job, Application, Placement

    with app.app_context():
        db.create_all()
        create_admin()

    return app

from .models.user import User
from .extensions import db, bcrypt, cache

def create_admin():
    if not User.query.filter_by(role="admin").first():
        hashed_pw=bcrypt.generate_password_hash("admin123").decode('utf-8')
        admin=User(email="admin@ppa.com", password=hashed_pw, role="admin", is_active=True)
        db.session.add(admin)
        db.session.commit()
        print("admin created")
    
