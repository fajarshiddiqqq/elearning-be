from app.routes.course import course_bp
from app.models import Courses
from app.services.utils import api_response
from flask_jwt_extended import jwt_required

@course_bp.route("/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course_details(course_id):
    course = Courses.query.get(course_id)
    if not course:
        return api_response(
            False,
            error={"code": "COURSE_NOT_FOUND", "message": "Course not found"},
            http_code=404,
        )

    course_data = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "created_by": course.created_by,
        "created_at": course.created_at,
        "updated_at": course.updated_at,
        "teachers": [
            {
                "teacher_id": ct.teacher_id,
                "name": ct.teacher.name,
                "role": ct.role
            }
            for ct in course.teachers
        ],
    }

    return api_response(True, data={"course": course_data})