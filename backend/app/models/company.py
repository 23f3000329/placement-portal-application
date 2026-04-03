from app.extensions import db

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    company_name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(100))

    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)

    # relationship with jobs
    jobs = db.relationship('Job', backref='company', lazy=True)