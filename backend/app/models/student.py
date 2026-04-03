from app.extensions import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float)
    branch = db.Column(db.String(50))
    resume = db.Column(db.String(200))

    # relationship with applications
    applications = db.relationship('Application', backref='student', lazy=True)