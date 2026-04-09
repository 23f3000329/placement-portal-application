from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("drives.id"), nullable=False)
    status = db.Column(db.String(30), default="applied")  # applied|shortlisted|interview|selected|rejected
    interview_date = db.Column(db.DateTime)
    interview_notes = db.Column(db.Text)
    company_feedback = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),)

    student = db.relationship("Student", back_populates="applications")
    drive = db.relationship("Drive", back_populates="applications")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else None,
            "student_branch": self.student.branch if self.student else None,
            "student_cgpa": self.student.cgpa if self.student else None,
            "student_email": self.student.user.email if self.student and self.student.user else None,
            "drive_id": self.drive_id,
            "drive_title": self.drive.title if self.drive else None,
            "company_name": self.drive.company.name if self.drive and self.drive.company else None,
            "status": self.status,
            "interview_date": self.interview_date.isoformat() if self.interview_date else None,
            "interview_notes": self.interview_notes,
            "company_feedback": self.company_feedback,
            "applied_at": self.applied_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
