import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db, cache
from models import Company, Drive, Application, Student

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


def company_required():
    claims = get_jwt()
    if claims.get("role") != "company":
        return jsonify({"error": "Company access required"}), 403
    return None


def get_company():
    uid = int(get_jwt_identity())
    return Company.query.filter_by(user_id=uid).first()



@company_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    err = company_required()
    if err: return err
    company = get_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404
    return jsonify(company.to_dict())


@company_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    err = company_required()
    if err: return err
    company = get_company()
    if not company:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json() or {}
    for field in ["name", "industry", "website", "hr_name", "hr_contact", "description", "location"]:
        if field in data:
            setattr(company, field, data[field])
    db.session.commit()
    return jsonify(company.to_dict())



@company_bp.route("/drives", methods=["GET"])
@jwt_required()
def list_drives():
    err = company_required()
    if err: return err
    company = get_company()
    if not company:
        return jsonify({"error": "Not found"}), 404
    drives = Drive.query.filter_by(company_id=company.id).order_by(Drive.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drives])


@company_bp.route("/drives", methods=["POST"])
@jwt_required()
def create_drive():
    err = company_required()
    if err: return err
    company = get_company()
    if not company:
        return jsonify({"error": "Not found"}), 404
    if company.approval_status != "approved":
        return jsonify({"error": "Company not approved yet"}), 403

    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    from datetime import datetime
    deadline = None
    if data.get("application_deadline"):
        deadline = datetime.fromisoformat(data["application_deadline"])

    drive = Drive(
        company_id=company.id,
        title=data["title"],
        job_description=data.get("job_description"),
        salary_min=data.get("salary_min"),
        salary_max=data.get("salary_max"),
        location=data.get("location"),
        job_type=data.get("job_type", "Full-time"),
        min_cgpa=data.get("min_cgpa", 0.0),
        eligible_branches=json.dumps(data.get("eligible_branches", [])),
        eligible_years=json.dumps(data.get("eligible_years", [])),
        skills_required=data.get("skills_required"),
        interview_mode=data.get("interview_mode", "In-person"),
        application_deadline=deadline,
        status="pending",
    )
    db.session.add(drive)
    db.session.commit()

   
    cache.delete("admin_stats")

    return jsonify(drive.to_dict()), 201


@company_bp.route("/drives/<int:did>", methods=["PUT"])
@jwt_required()
def update_drive(did):
    err = company_required()
    if err: return err
    company = get_company()
    drive   = Drive.query.filter_by(id=did, company_id=company.id).first_or_404()
    data    = request.get_json() or {}

    from datetime import datetime
    updatable = ["title", "job_description", "salary_min", "salary_max",
                 "location", "job_type", "min_cgpa", "skills_required", "interview_mode"]
    for f in updatable:
        if f in data:
            setattr(drive, f, data[f])
    if "eligible_branches" in data:
        drive.eligible_branches = json.dumps(data["eligible_branches"])
    if "eligible_years" in data:
        drive.eligible_years = json.dumps(data["eligible_years"])
    if "application_deadline" in data and data["application_deadline"]:
        drive.application_deadline = datetime.fromisoformat(data["application_deadline"])
    if "status" in data and data["status"] in ["closed"]:
        drive.status = data["status"]

    db.session.commit()
    cache.delete("student_drives")   # drive details changed — students must see fresh data
    return jsonify(drive.to_dict())


@company_bp.route("/drives/<int:did>/applications", methods=["GET"])
@jwt_required()
def drive_applications(did):
    err = company_required()
    if err: return err
    company = get_company()
    drive   = Drive.query.filter_by(id=did, company_id=company.id).first_or_404()
    return jsonify([a.to_dict() for a in drive.applications])


@company_bp.route("/applications/<int:aid>", methods=["PATCH"])
@jwt_required()
def update_application(aid):
    err = company_required()
    if err: return err
    company = get_company()
    app     = Application.query.get_or_404(aid)

    if app.drive.company_id != company.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    valid_statuses = ["applied", "shortlisted", "interview", "selected", "rejected"]
    if "status" in data:
        if data["status"] not in valid_statuses:
            return jsonify({"error": "Invalid status"}), 400
        app.status = data["status"]
        if data["status"] == "selected":
            app.student.is_placed = True

    if "interview_date" in data and data["interview_date"]:
        from datetime import datetime
        app.interview_date = datetime.fromisoformat(data["interview_date"])
    if "interview_notes" in data:
        app.interview_notes = data["interview_notes"]
    if "company_feedback" in data:
        app.company_feedback = data["company_feedback"]

    db.session.commit()

    
    cache.delete("admin_stats")
    cache.delete("admin_charts")
    cache.delete("admin_applications")

    return jsonify(app.to_dict())



@company_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    err = company_required()
    if err: return err
    company = get_company()
    if not company:
        return jsonify({}), 404

    drives    = Drive.query.filter_by(company_id=company.id).all()
    all_apps  = Application.query.join(Drive).filter(Drive.company_id == company.id).all()
    shortlisted = [a for a in all_apps if a.status in ["shortlisted", "interview"]]
    selected    = [a for a in all_apps if a.status == "selected"]

    return jsonify({
        "total_drives":    len(drives),
        "active_drives":   len([d for d in drives if d.status == "approved"]),
        "total_applicants": len(all_apps),
        "shortlisted":     len(shortlisted),
        "selected":        len(selected),
    })
