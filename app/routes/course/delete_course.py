from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.course import course_bp
from app.models import Courses
from app.extensions import db
from app.services.utils import api_response

@course_bp.route("/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    course = Courses.query.get(course_id)
    if not course:
        return api_response(
            False,
            error={"code": "COURSE_NOT_FOUND", "message": "Course not found"},
            http_code=404
        )

    current_user_id = get_jwt_identity()

    owner = next((t for t in course.teachers if str(t.teacher.id) == current_user_id and t.role == "owner"), None)
    if not owner:
        return api_response(
            False,
            error={"code": "FORBIDDEN", "message": "Only owner can delete course"},
            http_code=403
        )

    db.session.delete(course)
    db.session.commit()

    return api_response(True, data={"message": "Course deleted successfully"})
