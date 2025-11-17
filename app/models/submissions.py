from app.extensions import db


class Submissions(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'error', 'passed', 'failed'), nullable=False, default='pending')
    error_message = db.Column(db.Text)
    score = db.Column(db.Float)
    attempt_no = db.Column(db.Integer, nullable=False, default=1)
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())

    feedback = db.relationship('Feedbacks', backref='submission', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
