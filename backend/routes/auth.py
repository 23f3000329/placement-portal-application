from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)
from extensions import db
from models import User, Company, Student

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
BLOCKLIST = set()


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json() or {}
    for f in ["email", "password", "name"]:
        if not data.get(f):
            return jsonify({"error": f"'{f}' is required"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=data["email"], role="student")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id, name=data["name"],
        roll_number=data.get("roll_number"), branch=data.get("branch"),
        year=data.get("year"), cgpa=data.get("cgpa"), phone=data.get("phone"),
    )
    db.session.add(student)
    db.session.commit()

    access = create_access_token(identity=str(user.id), additional_claims={"role": "student"})
    refresh = create_refresh_token(identity=str(user.id))
    return jsonify({"access_token": access, "refresh_token": refresh,
                    "user": user.to_dict(), "profile": student.to_dict()}), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json() or {}
    for f in ["email", "password", "name"]:
        if not data.get(f):
            return jsonify({"error": f"'{f}' is required"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=data["email"], role="company")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()

    company = Company(
        user_id=user.id, name=data["name"], industry=data.get("industry"),
        website=data.get("website"), hr_name=data.get("hr_name"),
        hr_contact=data.get("hr_contact"), description=data.get("description"),
        location=data.get("location"),
    )
    db.session.add(company)
    db.session.commit()
    return jsonify({"message": "Registered. Awaiting admin approval.",
                    "user": user.to_dict(), "profile": company.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    if not user.is_active:
        return jsonify({"error": "Account deactivated"}), 403
    if user.is_blacklisted:
        return jsonify({"error": "Account blacklisted"}), 403
    if user.role == "company" and user.company and user.company.approval_status != "approved":
        return jsonify({"error": "Company not yet approved", "approval_status": user.company.approval_status}), 403

    access = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh = create_refresh_token(identity=str(user.id))
    profile = user.student.to_dict() if user.role == "student" and user.student else \
              user.company.to_dict() if user.role == "company" and user.company else None
    return jsonify({"access_token": access, "refresh_token": refresh,
                    "user": user.to_dict(), "profile": profile})


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    uid = get_jwt_identity()
    user = User.query.get(int(uid))
    if not user:
        return jsonify({"error": "User not found"}), 404
    access = create_access_token(identity=uid, additional_claims={"role": user.role})
    return jsonify({"access_token": access})


@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    BLOCKLIST.add(get_jwt()["jti"])
    return jsonify({"message": "Logged out"})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Not found"}), 404
    profile = user.student.to_dict() if user.role == "student" and user.student else \
              user.company.to_dict() if user.role == "company" and user.company else None
    return jsonify({"user": user.to_dict(), "profile": profile})