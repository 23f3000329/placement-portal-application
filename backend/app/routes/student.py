from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db, cache
from app.models import Student, Job, Application, Placement
import csv
from flask import send_file
import os

student_bp = Blueprint('student', __name__)

def student_required():
    claims = get_jwt()
    if claims.get("role") != "student":
        return False
    return True

@student_bp.route('/jobs', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def view_jobs():
    if not student_required():
        return jsonify({"error": "Unauthorized"}), 403

    jobs = Job.query.filter_by(status="approved").all()

    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.title,
            "cgpa_required": j.cgpa_required
        })

    return jsonify(result)

@student_bp.route('/apply/<int:job_id>', methods=['POST'])
@jwt_required()
def apply_job(job_id):
    if not student_required():
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    # ❗ Prevent duplicate application
    existing = Application.query.filter_by(
        student_id=student.id,
        job_id=job_id
    ).first()

    if existing:
        return jsonify({"error": "Already applied"}), 400

    # ❗ Check eligibility
    job = Job.query.get(job_id)
    if student.cgpa < job.cgpa_required:
        return jsonify({"error": "Not eligible"}), 403

    application = Application(
        student_id=student.id,
        job_id=job_id
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({"message": "Applied successfully"})

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def view_applications():
    if not student_required():
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    apps = Application.query.filter_by(student_id=student.id).all()

    result = []
    for a in apps:
        result.append({
            "job_id": a.job_id,
            "status": a.status,
            "applied_date": str(a.applied_date)
        })

    return jsonify(result)


@student_bp.route('/placements', methods=['GET'])
@jwt_required()
def view_placements():
    if not student_required():
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    placements = Placement.query.filter_by(student_id=student.id).all()

    result = []
    for p in placements:
        result.append({
            "company_id": p.company_id,
            "salary": p.salary
        })

    return jsonify(result)

@student_bp.route('/export', methods=['GET'])
@jwt_required()
def export_csv():
    if not student_required():
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    apps = Application.query.filter_by(student_id=student.id).all()

    filename = f"applications_{student.id}.csv"

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Job ID", "Status", "Date"])

        for a in apps:
            writer.writerow([a.job_id, a.status, a.applied_date])

    return send_file(filename, as_attachment=True)