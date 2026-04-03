from app.extensions import db
from datetime import datetime

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)

    status = db.Column(db.String(20), default="applied")
    # applied / shortlisted / selected / rejected

    applied_date = db.Column(db.DateTime, default=datetime.utcnow)