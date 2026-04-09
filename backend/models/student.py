from extensions import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    roll_number = db.Column(db.String(50), unique=True)
    branch = db.Column(db.String(100))
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    phone = db.Column(db.String(20))
    skills = db.Column(db.Text)          # comma-separated
    resume_path = db.Column(db.String(300))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    is_placed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="student")
    applications = db.relationship("Application", back_populates="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "roll_number": self.roll_number,
            "branch": self.branch,
            "year": self.year,
            "cgpa": self.cgpa,
            "phone": self.phone,
            "skills": self.skills,
            "resume_path": self.resume_path,
            "linkedin": self.linkedin,
            "github": self.github,
            "is_placed": self.is_placed,
            "email": self.user.email if self.user else None,
            "is_active": self.user.is_active if self.user else True,
            "is_blacklisted": self.user.is_blacklisted if self.user else False,
            "created_at": self.created_at.isoformat(),
        }
