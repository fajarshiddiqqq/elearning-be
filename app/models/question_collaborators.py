from app.extensions import db


class QuestionCollaborators(db.Model):
    __tablename__ = 'question_collaborators'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    permission = db.Column(db.Enum('viewer', 'editor'), nullable=False, default='viewer')
    added_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, question_id, user_id, permission='viewer'):
        self.question_id = question_id
        self.user_id = user_id
        self.permission = permission