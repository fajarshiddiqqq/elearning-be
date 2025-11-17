from app.extensions import db


class TestCases(db.Model):
    __tablename__ = 'test_cases'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, question_id, input_data, expected_output, is_hidden=False):
        self.question_id = question_id
        self.input_data = input_data
        self.expected_output = expected_output
        self.is_hidden = is_hidden