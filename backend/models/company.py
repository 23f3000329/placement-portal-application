from extensions import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    hr_name = db.Column(db.String(100))
    hr_contact = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    approval_status = db.Column(db.String(20), default="pending")  # pending|approved|rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="company")
    drives = db.relationship("Drive", back_populates="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "industry": self.industry,
            "website": self.website,
            "hr_name": self.hr_name,
            "hr_contact": self.hr_contact,
            "description": self.description,
            "location": self.location,
            "approval_status": self.approval_status,
            "created_at": self.created_at.isoformat(),
            "email": self.user.email if self.user else None,
            "is_active": self.user.is_active if self.user else True,
            "is_blacklisted": self.user.is_blacklisted if self.user else False,
            "drives_count": len(self.drives),
        }
