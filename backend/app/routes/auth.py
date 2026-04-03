from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models import User, Student, Company
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

# ---------------- REGISTER STUDENT ----------------
@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        email=data['email'],
        password=hashed_pw,
        role="student"
    )

    db.session.add(user)
    db.session.commit()

    student = Student(
        user_id=user.id,
        name=data.get('name'),
        cgpa=data.get('cgpa'),
        branch=data.get('branch')
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"})


# ---------------- REGISTER COMPANY ----------------
@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        email=data['email'],
        password=hashed_pw,
        role="company"
    )

    db.session.add(user)
    db.session.commit()

    company = Company(
        user_id=user.id,
        company_name=data.get('company_name'),
        website=data.get('website'),
        hr_contact=data.get('hr_contact')
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company registered. Await admin approval."})


# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(
    identity=str(user.id),   
    additional_claims={"role": user.role}
    )

    return jsonify({
        "token": access_token,
        "role": user.role
    })