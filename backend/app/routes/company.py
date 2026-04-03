from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Company, Job, Application

company_bp = Blueprint('company', __name__)

def company_required():
    claims = get_jwt()
    if claims.get("role") != "company":
        return False
    return True

@company_bp.route('/create-job', methods=['POST'])
@jwt_required()
def create_job():
    if not company_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    user_id = get_jwt_identity()

    company = Company.query.filter_by(user_id=user_id).first()

    if not company or not company.is_approved:
        return jsonify({"error": "Company not approved"}), 403

    job = Job(
        company_id=company.id,
        title=data['title'],
        description=data.get('description'),
        cgpa_required=data.get('cgpa_required'),
        status="pending"
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created, awaiting admin approval"})

@company_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_company_jobs():
    if not company_required():
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()

    jobs = Job.query.filter_by(company_id=company.id).all()

    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.title,
            "status": j.status
        })

    return jsonify(result)

@company_bp.route('/job/<int:job_id>/applications', methods=['GET'])
@jwt_required()
def get_applications(job_id):
    if not company_required():
        return jsonify({"error": "Unauthorized"}), 403

    applications = Application.query.filter_by(job_id=job_id).all()

    result = []
    for a in applications:
        result.append({
            "application_id": a.id,
            "student_id": a.student_id,
            "status": a.status
        })

    return jsonify(result)

@company_bp.route('/application/<int:id>/update', methods=['PUT'])
@jwt_required()
def update_application(id):
    if not company_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    application = Application.query.get(id)
    if not application:
        return jsonify({"error": "Not found"}), 404

    application.status = data['status']
    db.session.commit()

    return jsonify({"message": "Status updated"})

