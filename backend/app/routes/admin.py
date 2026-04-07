from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db

admin_bp = Blueprint('admin', __name__)

def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return False
    return True

from app.models import Company

@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    companies = Company.query.all()

    result = []
    for c in companies:
        result.append({
            "id": c.id,
            "name": c.company_name,
            "approved": c.is_approved,
            "blacklisted": c.is_blacklisted
        })

    return jsonify(result)

@admin_bp.route('/approve-company/<int:id>', methods=['PUT'])
@jwt_required()
def approve_company(id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    company = Company.query.get(id)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    company.is_approved = True
    db.session.commit()

    return jsonify({"message": "Company approved"})

@admin_bp.route('/blacklist-company/<int:id>', methods=['PUT'])
@jwt_required()
def blacklist_company(id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    company = Company.query.get(id)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    company.is_blacklisted = True
    db.session.commit()

    return jsonify({"message": "Company blacklisted"})

from app.models import Student

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    students = Student.query.all()

    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "cgpa": s.cgpa,
            "branch": s.branch
        })

    return jsonify(result)

from app.models import Job

@admin_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    jobs = Job.query.all()

    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.title,
            "status": j.status
        })

    return jsonify(result)


@admin_bp.route('/approve-job/<int:id>', methods=['PUT'])
@jwt_required()
def approve_job(id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    job = Job.query.get(id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    job.status = "approved"
    db.session.commit()

    return jsonify({"message": "Job approved"})

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({
        "students": Student.query.count(),
        "companies": Company.query.count(),
        "jobs": Job.query.count(),
        "applications": Application.query.count()
    })