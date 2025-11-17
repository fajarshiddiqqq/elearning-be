from app.extensions import db


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.Enum('student', 'teacher', 'admin'), nullable=False, default='student')
    is_active = db.Column(db.Boolean, default=True)
    google_id = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    courses_created = db.relationship('Courses', backref='creator', passive_deletes=True)
    submissions = db.relationship('Submissions', backref='student', passive_deletes=True)
    teaching_roles = db.relationship('CourseTeachers', backref='teacher', passive_deletes=True)
    question_collabs = db.relationship('QuestionCollaborators', backref='user', passive_deletes=True)
