from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import User, Company, Student, Drive, Application

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


# ── Dashboard stats ───────────────────────────────────────────────────────────
@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    err = admin_required()
    if err: return err

    from sqlalchemy import func
    total_students = Student.query.count()
    total_companies = Company.query.filter_by(approval_status="approved").count()
    pending_companies = Company.query.filter_by(approval_status="pending").count()
    active_drives = Drive.query.filter_by(status="approved").count()
    pending_drives = Drive.query.filter_by(status="pending").count()
    total_applications = Application.query.count()
    selected = Application.query.filter_by(status="selected").count()
    placement_rate = round(selected / total_students * 100, 1) if total_students else 0

    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "pending_companies": pending_companies,
        "active_drives": active_drives,
        "pending_drives": pending_drives,
        "total_applications": total_applications,
        "selected_students": selected,
        "placement_rate": placement_rate,
    })


# ── Chart data ────────────────────────────────────────────────────────────────
@admin_bp.route("/charts", methods=["GET"])
@jwt_required()
def charts():
    err = admin_required()
    if err: return err

    from sqlalchemy import func
    # Applications by status
    status_rows = db.session.query(
        Application.status, func.count(Application.id)
    ).group_by(Application.status).all()
    by_status = {r[0]: r[1] for r in status_rows}

    # Drives by company (top 5)
    drive_rows = db.session.query(
        Company.name, func.count(Drive.id)
    ).join(Drive, Drive.company_id == Company.id).group_by(Company.id).order_by(
        func.count(Drive.id).desc()
    ).limit(5).all()
    by_company = [{"company": r[0], "drives": r[1]} for r in drive_rows]

    # Branch-wise applications
    branch_rows = db.session.query(
        Student.branch, func.count(Application.id)
    ).join(Application, Application.student_id == Student.id).group_by(Student.branch).all()
    by_branch = [{"branch": r[0] or "Unknown", "applications": r[1]} for r in branch_rows]

    return jsonify({"by_status": by_status, "by_company": by_company, "by_branch": by_branch})


# ── Companies ─────────────────────────────────────────────────────────────────
@admin_bp.route("/companies", methods=["GET"])
@jwt_required()
def list_companies():
    err = admin_required()
    if err: return err

    q = request.args.get("q", "").strip()
    status = request.args.get("status", "all")
    query = Company.query
    if q:
        query = query.filter(Company.name.ilike(f"%{q}%"))
    if status != "all":
        query = query.filter_by(approval_status=status)
    return jsonify([c.to_dict() for c in query.order_by(Company.created_at.desc()).all()])


@admin_bp.route("/companies/<int:cid>/approve", methods=["PATCH"])
@jwt_required()
def approve_company(cid):
    err = admin_required()
    if err: return err
    company = Company.query.get_or_404(cid)
    company.approval_status = "approved"
    db.session.commit()
    return jsonify({"message": "Approved", "company": company.to_dict()})


@admin_bp.route("/companies/<int:cid>/reject", methods=["PATCH"])
@jwt_required()
def reject_company(cid):
    err = admin_required()
    if err: return err
    company = Company.query.get_or_404(cid)
    company.approval_status = "rejected"
    db.session.commit()
    return jsonify({"message": "Rejected"})


@admin_bp.route("/companies/<int:cid>/blacklist", methods=["PATCH"])
@jwt_required()
def blacklist_company(cid):
    err = admin_required()
    if err: return err
    company = Company.query.get_or_404(cid)
    company.user.is_blacklisted = True
    # Close all drives
    for drive in company.drives:
        drive.status = "closed"
    db.session.commit()
    return jsonify({"message": "Blacklisted and drives closed"})


@admin_bp.route("/companies/<int:cid>/activate", methods=["PATCH"])
@jwt_required()
def activate_company(cid):
    err = admin_required()
    if err: return err
    company = Company.query.get_or_404(cid)
    company.user.is_blacklisted = False
    company.user.is_active = True
    db.session.commit()
    return jsonify({"message": "Activated"})


# ── Students ──────────────────────────────────────────────────────────────────
@admin_bp.route("/students", methods=["GET"])
@jwt_required()
def list_students():
    err = admin_required()
    if err: return err

    q = request.args.get("q", "").strip()
    query = Student.query
    if q:
        query = query.filter(
            (Student.name.ilike(f"%{q}%")) |
            (Student.roll_number.ilike(f"%{q}%"))
        )
    return jsonify([s.to_dict() for s in query.order_by(Student.created_at.desc()).all()])


@admin_bp.route("/students/<int:sid>/blacklist", methods=["PATCH"])
@jwt_required()
def blacklist_student(sid):
    err = admin_required()
    if err: return err
    student = Student.query.get_or_404(sid)
    student.user.is_blacklisted = True
    db.session.commit()
    return jsonify({"message": "Blacklisted"})


@admin_bp.route("/students/<int:sid>/activate", methods=["PATCH"])
@jwt_required()
def activate_student(sid):
    err = admin_required()
    if err: return err
    student = Student.query.get_or_404(sid)
    student.user.is_blacklisted = False
    student.user.is_active = True
    db.session.commit()
    return jsonify({"message": "Activated"})


# ── Drives ────────────────────────────────────────────────────────────────────
@admin_bp.route("/drives", methods=["GET"])
@jwt_required()
def list_drives():
    err = admin_required()
    if err: return err
    status = request.args.get("status", "all")
    query = Drive.query
    if status != "all":
        query = query.filter_by(status=status)
    return jsonify([d.to_dict() for d in query.order_by(Drive.created_at.desc()).all()])


@admin_bp.route("/drives/<int:did>/approve", methods=["PATCH"])
@jwt_required()
def approve_drive(did):
    err = admin_required()
    if err: return err
    drive = Drive.query.get_or_404(did)
    drive.status = "approved"
    db.session.commit()
    return jsonify({"message": "Drive approved", "drive": drive.to_dict()})


@admin_bp.route("/drives/<int:did>/reject", methods=["PATCH"])
@jwt_required()
def reject_drive(did):
    err = admin_required()
    if err: return err
    drive = Drive.query.get_or_404(did)
    drive.status = "rejected"
    db.session.commit()
    return jsonify({"message": "Drive rejected"})


# ── All applications ──────────────────────────────────────────────────────────
@admin_bp.route("/applications", methods=["GET"])
@jwt_required()
def list_applications():
    err = admin_required()
    if err: return err
    apps = Application.query.order_by(Application.applied_at.desc()).all()
    return jsonify([a.to_dict() for a in apps])