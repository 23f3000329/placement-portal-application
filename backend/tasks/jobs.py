import csv
import io
import json
from datetime import datetime, timedelta
from flask import current_app, render_template_string
from flask_mail import Message
from extensions import db, mail

# Import celery lazily to avoid circular imports
def get_celery():
    from app import celery
    return celery

# ── Daily deadline reminders ─────────────────────────────────────────────────
def send_deadline_reminders():
    from models import Drive, Application, Student
    celery = get_celery()

    @celery.task(name="tasks.jobs.send_deadline_reminders")
    def _task():
        cutoff = datetime.utcnow() + timedelta(days=3)
        upcoming = Drive.query.filter(
            Drive.status == "approved",
            Drive.application_deadline <= cutoff,
            Drive.application_deadline >= datetime.utcnow(),
        ).all()

        count = 0
        for drive in upcoming:
            students = Student.query.filter_by(is_placed=False).all()
            for student in students:
                already_applied = Application.query.filter_by(
                    student_id=student.id, drive_id=drive.id
                ).first()
                if not already_applied and student.user and student.user.is_active:
                    days_left = (drive.application_deadline - datetime.utcnow()).days
                    _send_reminder_email(student, drive, days_left)
                    count += 1
        return {"reminders_sent": count}

    return _task

# ── Monthly report ────────────────────────────────────────────────────────────
def send_monthly_report():
    from models import Drive, Application, Student, Company
    celery = get_celery()

    @celery.task(name="tasks.jobs.send_monthly_report")
    def _task():
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0)
        last_month_start = (first_of_month - timedelta(days=1)).replace(day=1)

        drives = Drive.query.filter(
            Drive.created_at >= last_month_start,
            Drive.created_at < first_of_month,
        ).all()
        applications = Application.query.filter(
            Application.applied_at >= last_month_start,
            Application.applied_at < first_of_month,
        ).all()
        selected = [a for a in applications if a.status == "selected"]

        html = _build_report_html(
            month=last_month_start.strftime("%B %Y"),
            drives=drives,
            applications=applications,
            selected=selected,
        )
        msg = Message(
            subject=f"Monthly Placement Report — {last_month_start.strftime('%B %Y')}",
            recipients=[current_app.config["ADMIN_EMAIL"]],
            html=html,
        )
        mail.send(msg)
        return {"report_sent": True, "month": last_month_start.strftime("%B %Y")}

    return _task

# ── CSV export (user-triggered) ───────────────────────────────────────────────
def export_applications_csv():
    from models import Application
    celery = get_celery()

    @celery.task(name="tasks.jobs.export_applications_csv", bind=True)
    def _task(self, student_id, email):
        try:
            self.update_state(state="PROGRESS", meta={"status": "Fetching applications…"})
            apps = Application.query.filter_by(student_id=student_id).all()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Application ID","Student Name","Company","Drive Title",
                             "Job Type","Status","Applied At","Interview Date","Feedback"])
            for a in apps:
                writer.writerow([
                    a.id,
                    a.student.name if a.student else "",
                    a.drive.company.name if a.drive and a.drive.company else "",
                    a.drive.title if a.drive else "",
                    a.drive.job_type if a.drive else "",
                    a.status,
                    a.applied_at.strftime("%Y-%m-%d") if a.applied_at else "",
                    a.interview_date.strftime("%Y-%m-%d") if a.interview_date else "",
                    a.company_feedback or "",
                ])

            csv_data = output.getvalue()
            msg = Message(
                subject="Your Application History Export",
                recipients=[email],
                body="Your placement application history CSV is attached.",
            )
            msg.attach("applications.csv", "text/csv", csv_data)
            mail.send(msg)
            return {"status": "done", "rows": len(apps)}
        except Exception as exc:
            self.update_state(state="FAILURE", meta={"error": str(exc)})
            raise

    return _task

# ── Helpers ───────────────────────────────────────────────────────────────────
def _send_reminder_email(student, drive, days_left):
    try:
        msg = Message(
            subject=f"Reminder: {drive.title} at {drive.company.name} closes in {days_left} day(s)",
            recipients=[student.user.email],
            html=f"""
            <p>Hi {student.name},</p>
            <p>This is a reminder that the placement drive
            <strong>{drive.title}</strong> at <strong>{drive.company.name}</strong>
            closes in <strong>{days_left} day(s)</strong>
            ({drive.application_deadline.strftime("%d %b %Y")}).</p>
            <p>Log in to the Placement Portal to apply.</p>
            """,
        )
        mail.send(msg)
    except Exception:
        pass

def _build_report_html(month, drives, applications, selected):
    return f"""
    <html><body style="font-family:sans-serif;color:#1a1a18;padding:32px">
    <h1 style="color:#1D9E75">Monthly Placement Report — {month}</h1>
    <table style="border-collapse:collapse;width:100%;margin-top:24px">
      <tr style="background:#E1F5EE">
        <td style="padding:12px;font-weight:600">Drives conducted</td>
        <td style="padding:12px">{len(drives)}</td>
      </tr>
      <tr>
        <td style="padding:12px;font-weight:600">Total applications</td>
        <td style="padding:12px">{len(applications)}</td>
      </tr>
      <tr style="background:#E1F5EE">
        <td style="padding:12px;font-weight:600">Students selected</td>
        <td style="padding:12px">{len(selected)}</td>
      </tr>
      <tr>
        <td style="padding:12px;font-weight:600">Selection rate</td>
        <td style="padding:12px">{round(len(selected)/len(applications)*100, 1) if applications else 0}%</td>
      </tr>
    </table>
    <h2 style="margin-top:32px">Drive Summary</h2>
    <table style="border-collapse:collapse;width:100%">
      <tr style="background:#f5f5f3"><th style="padding:8px;text-align:left">Drive</th>
        <th style="padding:8px;text-align:left">Company</th>
        <th style="padding:8px;text-align:left">Applications</th></tr>
      {"".join(f'<tr><td style="padding:8px">{d.title}</td><td style="padding:8px">{d.company.name}</td><td style="padding:8px">{len(d.applications)}</td></tr>' for d in drives)}
    </table>
    </body></html>
    """
def register_tasks(celery):
    """
    Registers the jobs into the Celery instance. 
    This is what celery_worker.py calls during startup.
    """
    # We call the functions to define the tasks inside Celery's scope
    send_deadline_reminders()
    send_monthly_report()
    export_applications_csv()