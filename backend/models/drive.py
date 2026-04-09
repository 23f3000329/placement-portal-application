from extensions import db
from datetime import datetime

class Drive(db.Model):
    __tablename__ = "drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text)
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    location = db.Column(db.String(150))
    job_type = db.Column(db.String(50), default="Full-time")  # Full-time|Internship|Contract
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_branches = db.Column(db.Text)   # JSON array stored as string
    eligible_years = db.Column(db.Text)      # JSON array stored as string
    skills_required = db.Column(db.Text)
    interview_mode = db.Column(db.String(50), default="In-person")
    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending")  # pending|approved|closed|rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive", cascade="all, delete-orphan")

    def to_dict(self, include_applications=False):
        import json
        d = {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else None,
            "company_industry": self.company.industry if self.company else None,
            "title": self.title,
            "job_description": self.job_description,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "location": self.location,
            "job_type": self.job_type,
            "min_cgpa": self.min_cgpa,
            "eligible_branches": json.loads(self.eligible_branches) if self.eligible_branches else [],
            "eligible_years": json.loads(self.eligible_years) if self.eligible_years else [],
            "skills_required": self.skills_required,
            "interview_mode": self.interview_mode,
            "application_deadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "status": self.status,
            "applications_count": len(self.applications),
            "created_at": self.created_at.isoformat(),
        }
        if include_applications:
            d["applications"] = [a.to_dict() for a in self.applications]
        return d
