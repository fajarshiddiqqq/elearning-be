from flask import Blueprint
from app.services.utils import api_response

apis_bp = Blueprint("apis", __name__)

@apis_bp.route("")
def index():
    return api_response(
        True,
        meta={
            "environment": "development",
            "version": "1.0.0",
            "message": "API is running",
        },
    )

from .auth import auth_bp
apis_bp.register_blueprint(auth_bp, url_prefix="/auth")

# from .course import course_bp
# apis_bp.register_blueprint(course_bp, url_prefix="/courses")

from .question import question_bp
apis_bp.register_blueprint(question_bp, url_prefix="/questions")

from .submission import submission_bp
apis_bp.register_blueprint(submission_bp, url_prefix="/submissions")