from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB

class Rubrics(db.Model):
    __tablename__ = 'rubrics'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    criteria = db.Column(JSONB, nullable=False)
    tone = db.Column(db.String(100), nullable=False, default='constructive')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, question_id, criteria, tone='constructive'):
        self.question_id = question_id
        self.criteria = criteria
        self.tone = tone