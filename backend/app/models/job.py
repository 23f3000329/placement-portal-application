from app.extensions import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cgpa_required = db.Column(db.Float)

    deadline = db.Column(db.DateTime)

    status = db.Column(db.String(20), default="pending")  
    # pending / approved / closed

    # relationship with applications
    applications = db.relationship('Application', backref='job', lazy=True)