"""
Run once to populate the DB with sample data for development.
Usage: python seed.py
"""
import json
from datetime import datetime, timedelta
from app import app
from extensions import db
from models import User, Company, Student, Drive, Application


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ── Admin ─────────────────────────────────────────────────────────────
        admin = User(email="admin@institute.edu", role="admin")
        admin.set_password("admin@123")
        db.session.add(admin)
        db.session.flush()
        print(" Admin: admin@institute.edu / admin@123")

        # ── Companies ─────────────────────────────────────────────────────────
        companies_data = [
            dict(email="hr@razorpay.com", password="company@123",
                 name="Razorpay", industry="Fintech", website="razorpay.com",
                 hr_name="Ananya Sharma", location="Bangalore", approval_status="approved",
                 description="Leading payment gateway in India."),
            dict(email="hr@juspay.com", password="company@123",
                 name="Juspay", industry="Payments", website="juspay.in",
                 hr_name="Rajan Mehta", location="Bangalore", approval_status="approved",
                 description="Payment orchestration platform."),
            dict(email="hr@freshworks.com", password="company@123",
                 name="Freshworks", industry="SaaS", website="freshworks.com",
                 hr_name="Priti Das", location="Chennai", approval_status="approved",
                 description="Customer engagement software company."),
            dict(email="hr@zoho.com", password="company@123",
                 name="Zoho Corp", industry="SaaS", website="zoho.com",
                 hr_name="Vignesh Kumar", location="Chennai", approval_status="pending",
                 description="Business software suite."),
        ]

        company_objs = []
        for cd in companies_data:
            u = User(email=cd["email"], role="company")
            u.set_password(cd["password"])
            db.session.add(u)
            db.session.flush()
            c = Company(
                user_id=u.id, name=cd["name"], industry=cd["industry"],
                website=cd["website"], hr_name=cd["hr_name"], location=cd["location"],
                approval_status=cd["approval_status"], description=cd["description"],
            )
            db.session.add(c)
            db.session.flush()
            company_objs.append(c)
            print(f" Company: {cd['email']} / company@123  [{cd['approval_status']}]")

        razorpay, juspay, freshworks, zoho = company_objs

        # ── Drives ────────────────────────────────────────────────────────────
        drives_data = [
            dict(company=razorpay, title="SDE Intern 2025", job_type="Internship",
                 job_description="Build scalable payment infrastructure. Work with senior engineers on high-impact projects.",
                 salary_min=40000, salary_max=60000, location="Bangalore",
                 min_cgpa=7.0, eligible_branches=["CSE", "ECE", "IT"],
                 eligible_years=[4], skills_required="Python, REST APIs, SQL",
                 interview_mode="In-person",
                 deadline=datetime.utcnow() + timedelta(days=30), status="approved"),
            dict(company=razorpay, title="ML Engineer", job_type="Full-time",
                 job_description="Design ML models for fraud detection and risk scoring.",
                 salary_min=1800000, salary_max=2400000, location="Bangalore",
                 min_cgpa=8.0, eligible_branches=["CSE", "DS"],
                 eligible_years=[4], skills_required="Python, TensorFlow, PyTorch, SQL",
                 interview_mode="Virtual",
                 deadline=datetime.utcnow() + timedelta(days=45), status="approved"),
            dict(company=juspay, title="Backend Engineer", job_type="Full-time",
                 job_description="Build high-throughput transaction processing systems in Haskell/Java.",
                 salary_min=1500000, salary_max=2000000, location="Bangalore",
                 min_cgpa=7.5, eligible_branches=["CSE", "IT"],
                 eligible_years=[4], skills_required="Java, Distributed Systems, Kafka",
                 interview_mode="In-person",
                 deadline=datetime.utcnow() + timedelta(days=20), status="approved"),
            dict(company=freshworks, title="Product Manager", job_type="Full-time",
                 job_description="Drive product strategy for CRM suite. Work cross-functionally.",
                 salary_min=2000000, salary_max=2800000, location="Chennai",
                 min_cgpa=7.0, eligible_branches=["CSE", "ECE", "ME", "EEE", "IT", "DS"],
                 eligible_years=[4], skills_required="Product thinking, Analytics, Communication",
                 interview_mode="Virtual",
                 deadline=datetime.utcnow() + timedelta(days=60), status="approved"),
            dict(company=freshworks, title="QA Engineer", job_type="Full-time",
                 job_description="Ensure product quality through automated and manual testing.",
                 salary_min=800000, salary_max=1200000, location="Chennai",
                 min_cgpa=6.5, eligible_branches=["CSE", "IT", "ECE"],
                 eligible_years=[4], skills_required="Selenium, Python, JIRA",
                 interview_mode="Virtual",
                 deadline=datetime.utcnow() + timedelta(days=15), status="approved"),
            dict(company=zoho, title="Software Developer", job_type="Full-time",
                 job_description="Develop features for Zoho CRM using Java and React.",
                 salary_min=700000, salary_max=900000, location="Chennai",
                 min_cgpa=6.0, eligible_branches=["CSE", "IT"],
                 eligible_years=[4], skills_required="Java, React, MySQL",
                 interview_mode="In-person",
                 deadline=datetime.utcnow() + timedelta(days=40), status="pending"),
        ]

        drive_objs = []
        for dd in drives_data:
            dr = Drive(
                company_id=dd["company"].id,
                title=dd["title"], job_type=dd["job_type"],
                job_description=dd["job_description"],
                salary_min=dd["salary_min"], salary_max=dd["salary_max"],
                location=dd["location"], min_cgpa=dd["min_cgpa"],
                eligible_branches=json.dumps(dd["eligible_branches"]),
                eligible_years=json.dumps(dd["eligible_years"]),
                skills_required=dd["skills_required"],
                interview_mode=dd["interview_mode"],
                application_deadline=dd["deadline"],
                status=dd["status"],
            )
            db.session.add(dr)
            db.session.flush()
            drive_objs.append(dr)
            print(f" Drive: {dd['title']} @ {dd['company'].name}  [{dd['status']}]")

        # ── Students ──────────────────────────────────────────────────────────
        students_data = [
            dict(email="arjun@student.edu", password="student@123",
                 name="Arjun", roll="CS21001", branch="CSE", year=4, cgpa=8.7,
                 phone="9876543210", skills="Python,Java,React,SQL"),
            dict(email="priya@student.edu", password="student@123",
                 name="Priya ", roll="CS21002", branch="CSE", year=4, cgpa=9.1,
                 phone="9876543211", skills="Python,ML,TensorFlow,SQL"),
            dict(email="rohit@student.edu", password="student@123",
                 name="Rohit ", roll="EC21003", branch="ECE", year=4, cgpa=7.8,
                 phone="9876543212", skills="Embedded C,Python,VLSI"),
            dict(email="sneha@student.edu", password="student@123",
                 name="Sneha ", roll="CS21004", branch="CSE", year=4, cgpa=9.4,
                 phone="9876543213", skills="Java,Spring Boot,Kubernetes,Docker"),
            dict(email="vikram@student.edu", password="student@123",
                 name="Vikram ", roll="CS21005", branch="CSE", year=4, cgpa=7.2,
                 phone="9876543214", skills="JavaScript,React,Node.js"),
            dict(email="meera@student.edu", password="student@123",
                 name="Meera ", roll="DS21006", branch="DS", year=4, cgpa=8.5,
                 phone="9876543215", skills="Python,R,ML,Statistics"),
        ]

        student_objs = []
        for sd in students_data:
            u = User(email=sd["email"], role="student")
            u.set_password(sd["password"])
            db.session.add(u)
            db.session.flush()
            s = Student(
                user_id=u.id, name=sd["name"], roll_number=sd["roll"],
                branch=sd["branch"], year=sd["year"], cgpa=sd["cgpa"],
                phone=sd["phone"], skills=sd["skills"],
            )
            db.session.add(s)
            db.session.flush()
            student_objs.append(s)
            print(f"✓ Student: {sd['email']} / student@123")

        arjun, priya, rohit, sneha, vikram, meera = student_objs
        sde_drive, ml_drive, backend_drive, pm_drive, qa_drive, zoho_drive = drive_objs

        # ── Applications ──────────────────────────────────────────────────────
        app_data = [
            dict(student=arjun,  drive=sde_drive,     status="applied"),
            dict(student=arjun,  drive=backend_drive, status="shortlisted"),
            dict(student=priya,  drive=ml_drive,      status="shortlisted"),
            dict(student=priya,  drive=sde_drive,     status="selected"),
            dict(student=rohit,  drive=sde_drive,     status="applied"),
            dict(student=rohit,  drive=qa_drive,      status="applied"),
            dict(student=sneha,  drive=ml_drive,      status="selected"),
            dict(student=sneha,  drive=backend_drive, status="interview"),
            dict(student=vikram, drive=pm_drive,      status="applied"),
            dict(student=vikram, drive=qa_drive,      status="rejected"),
            dict(student=meera,  drive=ml_drive,      status="applied"),
            dict(student=meera,  drive=pm_drive,      status="shortlisted"),
        ]

        for ad in app_data:
            a = Application(
                student_id=ad["student"].id,
                drive_id=ad["drive"].id,
                status=ad["status"],
            )
            if ad["status"] == "interview":
                a.interview_date = datetime.utcnow() + timedelta(days=7)
            if ad["status"] == "selected":
                ad["student"].is_placed = True
            db.session.add(a)

        db.session.commit()
        print("\n Seed complete!")
        print("─" * 40)
        print("Admin    → admin@institute.edu / admin@123")
        print("Company  → hr@razorpay.com    / company@123")
        print("Student  → arjun@student.edu  / student@123")


if __name__ == "__main__":
    seed()