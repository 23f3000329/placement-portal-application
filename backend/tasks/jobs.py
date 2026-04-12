import csv
import io
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from extensions import db, mail


def register_tasks(celery):
    """
    Called from celery_worker.py after the Celery app is created.
    Decorates each job function and binds it to the Celery instance.
    """

   
    @celery.task(name="tasks.jobs.send_deadline_reminders")
    def send_deadline_reminders():
        from models import Drive, Application, Student

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


    @celery.task(name="tasks.jobs.send_monthly_report")
    def send_monthly_report():
        from models import Drive, Application

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

    
    @celery.task(name="tasks.jobs.export_applications_csv", bind=True)
    def export_applications_csv(self, student_id, email):
        from models import Application

        try:
            self.update_state(state="PROGRESS", meta={"status": "Fetching applications…"})
            apps = Application.query.filter_by(student_id=student_id).all()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "Application ID", "Student ID", "Student Name",
                "Company Name", "Drive Title", "Job Type",
                "Status", "Applied At", "Interview Date", "Feedback"
            ])
            for a in apps:
                writer.writerow([
                    a.id,
                    a.student_id,
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
    rate = round(len(selected) / len(applications) * 100, 1) if applications else 0
    drive_rows = "".join(
        f'<tr><td style="padding:8px">{d.title}</td>'
        f'<td style="padding:8px">{d.company.name}</td>'
        f'<td style="padding:8px">{len(d.applications)}</td></tr>'
        for d in drives
    )
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
        <td style="padding:12px">{rate}%</td>
      </tr>
    </table>
    <h2 style="margin-top:32px">Drive Summary</h2>
    <table style="border-collapse:collapse;width:100%">
      <tr style="background:#f5f5f3">
        <th style="padding:8px;text-align:left">Drive</th>
        <th style="padding:8px;text-align:left">Company</th>
        <th style="padding:8px;text-align:left">Applications</th>
      </tr>
      {drive_rows}
    </table>
    </body></html>
    """