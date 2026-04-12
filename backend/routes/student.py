import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db, cache
from models import Student, Drive, Application, User
from flask import send_from_directory

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



@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    err = student_required()
    if err:
        return err
    student = get_student()
    if not student:
        return jsonify({"error": "Not found"}), 404
    return jsonify(student.to_dict())


@student_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    err = student_required()
    if err:
        return err
    student = get_student()
    if not student:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json() or {}
    for f in ["name", "roll_number", "branch", "year", "cgpa", "phone", "skills", "linkedin", "github"]:
        if f in data:
            setattr(student, f, data[f])
    db.session.commit()
    # Eligibility depends on CGPA/branch/year — clear drives cache
    cache.delete("student_drives_")
    return jsonify(student.to_dict())


@student_bp.route("/profile/resume", methods=["POST"])
@jwt_required()
def upload_resume():
    err = student_required()
    if err:
        return err
    student = get_student()
    if "resume" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["resume"]
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Only PDF, DOC, DOCX allowed"}), 400

    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    filename = secure_filename(f"student_{student.id}_resume.{ext}")
    path     = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    student.resume_path = filename
    db.session.commit()
    return jsonify({"message": "Uploaded", "resume_path": filename, "filename": filename})


@student_bp.route("/drives", methods=["GET"])
@jwt_required()
def list_drives():
    err = student_required()
    if err:
        return err
    student = get_student()

    q = request.args.get("q", "").strip()

    cache_key = f"student_drives_{q}"
    cached = cache.get(cache_key)
    if cached is None:
        query = Drive.query.filter_by(status="approved")
        if q:
            query = query.filter(
                Drive.title.ilike(f"%{q}%") |
                Drive.skills_required.ilike(f"%{q}%")
            )
        drives = query.order_by(Drive.created_at.desc()).all()
        base_list = [d.to_dict() for d in drives]
        cache.set(cache_key, base_list, timeout=30 if q else 60)
    else:
        base_list = cached

    applied_ids = {a.drive_id for a in student.applications} if student else set()
    result = []
    for data in base_list:
        entry = dict(data)
        entry["already_applied"] = data["id"] in applied_ids
        entry["is_eligible"] = _check_eligibility_from_dict(student, data)
        result.append(entry)

    return jsonify(result)


@student_bp.route("/drives/<int:did>", methods=["GET"])
@jwt_required()
def drive_detail(did):
    err = student_required()
    if err:
        return err
    student = get_student()


    drive = Drive.query.get_or_404(did)

    data = drive.to_dict()
    if student:
        app = Application.query.filter_by(student_id=student.id, drive_id=did).first()
        data["already_applied"] = app is not None
        data["application"]     = app.to_dict() if app else None
        data["is_eligible"]     = _check_eligibility(student, drive)
    return jsonify(data)


@student_bp.route("/apply/<int:did>", methods=["POST"])
@jwt_required()
def apply(did):
    err = student_required()
    if err:
        return err
    student = get_student()
    if not student:
        return jsonify({"error": "Profile not found"}), 404

    
    drive = Drive.query.filter_by(id=did, status="approved").first_or_404()

    existing = Application.query.filter_by(student_id=student.id, drive_id=did).first()
    if existing:
        return jsonify({"error": "Already applied"}), 409

    if not _check_eligibility(student, drive):
        return jsonify({"error": "You do not meet the eligibility criteria"}), 400

    from datetime import datetime
    if drive.application_deadline and drive.application_deadline < datetime.utcnow():
        return jsonify({"error": "Application deadline has passed"}), 400

    app_obj = Application(student_id=student.id, drive_id=did)
    db.session.add(app_obj)
    db.session.commit()

    cache.delete("admin_stats")
    cache.delete("admin_applications")
    cache.delete("admin_charts")

    return jsonify(app_obj.to_dict()), 201


@student_bp.route("/applications", methods=["GET"])
@jwt_required()
def my_applications():
    err = student_required()
    if err:
        return err
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
    if err:
        return err
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


@student_bp.route("/resume/<filename>", methods=["GET"])
def serve_resume(filename):
   
    from flask_jwt_extended import decode_token
    from flask_jwt_extended.exceptions import JWTDecodeError
    from jwt.exceptions import InvalidTokenError

    token = request.args.get("token", "")
    if not token:
        return jsonify({"error": "Authorization required"}), 401

    try:
        decoded = decode_token(token)
    except (JWTDecodeError, InvalidTokenError, Exception):
        return jsonify({"error": "Invalid or expired token"}), 401

    role = decoded.get("role") or decoded.get("sub", {})
    
    if decoded.get("role") not in ["company", "admin"]:
        return jsonify({"error": "Only companies and admins can view resumes"}), 403

    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


def _check_eligibility(student, drive):
    """Check eligibility using SQLAlchemy model objects."""
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


def _check_eligibility_from_dict(student, drive_dict):
    if not student:
        return False
    min_cgpa = drive_dict.get("min_cgpa") or 0
    if min_cgpa and student.cgpa and student.cgpa < min_cgpa:
        return False
    branches = drive_dict.get("eligible_branches") or []
    if branches and student.branch and student.branch not in branches:
        return False
    years = drive_dict.get("eligible_years") or []
    if years and student.year and student.year not in years:
        return False
    return True