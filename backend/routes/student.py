import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import Student, Drive, Application, User

student_bp = Blueprint("student", __name__, url_prefix="/api/student")

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def student_required():
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"error": "Student access required"}), 403
    return None


def get_student():
    uid = int(get_jwt_identity())
    return Student.query.filter_by(user_id=uid).first()


# ── Profile ───────────────────────────────────────────────────────────────────
@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    err = student_required()
    if err: return err
    student = get_student()
    if not student:
        return jsonify({"error": "Not found"}), 404
    return jsonify(student.to_dict())


@student_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    err = student_required()
    if err: return err
    student = get_student()
    if not student:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json() or {}
    for f in ["name", "roll_number", "branch", "year", "cgpa", "phone", "skills", "linkedin", "github"]:
        if f in data:
            setattr(student, f, data[f])
    db.session.commit()
    return jsonify(student.to_dict())


@student_bp.route("/profile/resume", methods=["POST"])
@jwt_required()
def upload_resume():
    err = student_required()
    if err: return err
    student = get_student()
    if "resume" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["resume"]
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Only PDF, DOC, DOCX allowed"}), 400

    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    filename = secure_filename(f"student_{student.id}_resume.{ext}")
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    student.resume_path = filename
    db.session.commit()
    return jsonify({"message": "Uploaded", "resume_path": filename})


# ── Drives ────────────────────────────────────────────────────────────────────
@student_bp.route("/drives", methods=["GET"])
@jwt_required()
def list_drives():
    err = student_required()
    if err: return err
    student = get_student()

    q = request.args.get("q", "").strip()
    query = Drive.query.filter_by(status="approved")
    if q:
        query = query.filter(
            Drive.title.ilike(f"%{q}%") |
            Drive.skills_required.ilike(f"%{q}%")
        )

    drives = query.order_by(Drive.created_at.desc()).all()
    result = []
    applied_ids = {a.drive_id for a in student.applications} if student else set()

    for d in drives:
        data = d.to_dict()
        data["already_applied"] = d.id in applied_ids
        data["is_eligible"] = _check_eligibility(student, d) if student else False
        result.append(data)

    return jsonify(result)


@student_bp.route("/drives/<int:did>", methods=["GET"])
@jwt_required()
def drive_detail(did):
    err = student_required()
    if err: return err
    student = get_student()
    drive = Drive.query.filter_by(id=did, status="approved").first_or_404()
    data = drive.to_dict()
    if student:
        app = Application.query.filter_by(student_id=student.id, drive_id=did).first()
        data["already_applied"] = app is not None
        data["application"] = app.to_dict() if app else None
        data["is_eligible"] = _check_eligibility(student, drive)
    return jsonify(data)


# ── Applications ──────────────────────────────────────────────────────────────
@student_bp.route("/apply/<int:did>", methods=["POST"])
@jwt_required()
def apply(did):
    err = student_required()
    if err: return err
    student = get_student()
    if not student:
        return jsonify({"error": "Profile not found"}), 404

    drive = Drive.query.filter_by(id=did, status="approved").first_or_404()

    # Duplicate check
    existing = Application.query.filter_by(student_id=student.id, drive_id=did).first()
    if existing:
        return jsonify({"error": "Already applied"}), 409

    # Eligibility check
    if not _check_eligibility(student, drive):
        return jsonify({"error": "You do not meet the eligibility criteria"}), 400

    # Deadline check
    from datetime import datetime
    if drive.application_deadline and drive.application_deadline < datetime.utcnow():
        return jsonify({"error": "Application deadline has passed"}), 400

    app = Application(student_id=student.id, drive_id=did)
    db.session.add(app)
    db.session.commit()
    return jsonify(app.to_dict()), 201


@student_bp.route("/applications", methods=["GET"])
@jwt_required()
def my_applications():
    err = student_required()
    if err: return err
    student = get_student()
    if not student:
        return jsonify([])
    apps = Application.query.filter_by(student_id=student.id).order_by(
        Application.applied_at.desc()
    ).all()
    return jsonify([a.to_dict() for a in apps])


@student_bp.route("/export-csv", methods=["POST"])
@jwt_required()
def export_csv():
    err = student_required()
    if err: return err
    student = get_student()
    if not student:
        return jsonify({"error": "Not found"}), 404

    from app import celery
    task = celery.send_task(
        "tasks.jobs.export_applications_csv",
        args=[student.id, student.user.email],
    )
    return jsonify({"task_id": task.id, "message": "Export started. You'll receive an email when ready."})


@student_bp.route("/export-status/<task_id>", methods=["GET"])
@jwt_required()
def export_status(task_id):
    from app import celery
    result = celery.AsyncResult(task_id)
    return jsonify({"state": result.state, "info": result.info})


# ── Helpers ───────────────────────────────────────────────────────────────────
def _check_eligibility(student, drive):
    import json
    if not student:
        return False
    if drive.min_cgpa and student.cgpa and student.cgpa < drive.min_cgpa:
        return False
    branches = json.loads(drive.eligible_branches) if drive.eligible_branches else []
    if branches and student.branch and student.branch not in branches:
        return False
    years = json.loads(drive.eligible_years) if drive.eligible_years else []
    if years and student.year and student.year not in years:
        return False
    return True