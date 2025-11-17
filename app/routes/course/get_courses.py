from app.routes.course import course_bp
from app.models import Courses
from app.services.utils import api_response
from flask_jwt_extended import jwt_required

@course_bp.route("/list", methods=["GET"])
@jwt_required()
def get_courses():
    """
    Retrieve a list of courses.

    :return: Standard API response with a list of courses.
    """
    courses = Courses.query.all()

    course_list = [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "created_by": course.created_by,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
        }
        for course in courses
    ]

    return api_response(True, data={"courses": course_list})