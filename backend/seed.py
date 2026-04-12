import json
from datetime import datetime, timedelta
from app import app
from extensions import db
from models import User, Company, Student, Drive, Application


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

      
        admin = User(email="admin@institute.edu", role="admin")
        admin.set_password("admin@123")
        db.session.add(admin)
        db.session.flush()
        print(" Admin: admin@institute.edu / admin@123")

        db.session.commit()
        print("\n Seed complete")
        print("Admin: admin@institute.edu / admin@123")



if __name__ == "__main__":
    seed()