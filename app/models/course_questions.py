from app.extensions import db


class CourseQuestions(db.Model):
    __tablename__ = 'course_questions'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    added_at = db.Column(db.DateTime, server_default=db.func.now())
