from app.extensions import db
from sqlalchemy import Enum

class CourseTeachers(db.Model):
    __tablename__ = 'course_teachers'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(Enum('owner', 'collaborator', name='role_enum'), nullable=False, default='collaborator')
    added_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('course_id', 'teacher_id', name='uq_course_teacher'),
    )
