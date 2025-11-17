from app.extensions import db


class Questions(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    custom_instructions = db.Column(db.Text, nullable=True)
    starter_code = db.Column(db.Text)
    difficulty = db.Column(db.Enum('easy', 'medium', 'hard'), nullable=False, default='medium')
    tags = db.Column(db.JSON)
    visibility = db.Column(db.Enum('public', 'private'), nullable=False, default='private')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # relationships
    test_cases = db.relationship('TestCases', backref='question', cascade='all, delete-orphan', passive_deletes=True)
    submissions = db.relationship('Submissions', backref='question', cascade='all, delete-orphan', passive_deletes=True)
    rubric = db.relationship('Rubrics', backref='question', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    collaborators = db.relationship('QuestionCollaborators', backref='question', cascade='all, delete-orphan', passive_deletes=True)
    courses = db.relationship('CourseQuestions', backref='question', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, title, description, custom_instructions=None, starter_code=None, difficulty='medium', tags=None, visibility='private', created_by=None):
        self.title = title
        self.description = description
        self.custom_instructions = custom_instructions
        self.starter_code = starter_code
        self.difficulty = difficulty
        self.tags = tags or []
        self.visibility = visibility
        self.created_by = created_by