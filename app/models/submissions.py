from app.extensions import db
from sqlalchemy import Enum

class Submissions(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(Enum('pending', 'error', 'passed', 'failed', name='status_enum'), nullable=False, default='pending')
    error_message = db.Column(db.Text)
    score = db.Column(db.Float)
    attempt_no = db.Column(db.Integer, nullable=False, default=1)
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())

    feedback = db.relationship('Feedbacks', backref='submission', uselist=False, cascade='all, delete', passive_deletes=True)
    
    def __init__(self, question_id, student_id, code, status='pending', error_message=None, score=None, attempt_no=1):
        self.question_id = question_id
        self.student_id = student_id
        self.code = code
        self.status = status
        self.error_message = error_message
        self.score = score
        self.attempt_no = attempt_no