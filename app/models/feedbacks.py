from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB

class Feedbacks(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    ai_feedback = db.Column(JSONB, nullable=False)
    teacher_feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, submission_id, ai_feedback, teacher_feedback=None):
        self.submission_id = submission_id
        self.ai_feedback = ai_feedback
        self.teacher_feedback = teacher_feedback