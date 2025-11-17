from app.extensions import db


class Feedbacks(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    ai_feedback = db.Column(db.JSON, nullable=False)
    teacher_feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
