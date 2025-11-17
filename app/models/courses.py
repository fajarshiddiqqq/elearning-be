from app.extensions import db


class Courses(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    teachers = db.relationship(
        'CourseTeachers',
        backref='course',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    questions = db.relationship(
        'CourseQuestions',
        backref='course',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
