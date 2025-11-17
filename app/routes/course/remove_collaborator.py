from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.course import course_bp
from app.models import Courses, CourseTeachers, Questions, Users
from app.extensions import db
from app.services.utils import api_response

@course_bp.route("/<int:course_id>/teachers/<int:teacher_id>", methods=["DELETE"])
@jwt_required()
def remove_collaborator(course_id, teacher_id):
    course = Courses.query.get(course_id)
    if not course:
        return api_response(False, error={"code": "COURSE_NOT_FOUND", "message": "Course not found"}, http_code=404)

    current_user_id = get_jwt_identity()
    # Only owner can remove collaborator
    owner = next((t for t in course.teachers if str(t.teacher.id) == current_user_id and t.role == "owner"), None)
    if not owner:
        return api_response(False, error={"code": "FORBIDDEN", "message": "Only owner can remove collaborators"}, http_code=403)

    # Prevent owner from removing themselves
    if str(teacher_id) == current_user_id:
        return api_response(False, error={"code": "FORBIDDEN", "message": "Owner cannot remove themselves"}, http_code=403)

    collab = CourseTeachers.query.filter_by(course_id=course_id, teacher_id=teacher_id).first()
    if not collab:
        return api_response(False, error={"code": "NOT_FOUND", "message": "Collaborator not found"}, http_code=404)

    # reassign questions created by this teacher to owner
    Questions.query.filter_by(course_id=course_id, created_by=teacher_id).update({"created_by": owner.teacher.id})

    db.session.delete(collab)
    db.session.commit()

    return api_response(True, data={"message": f"Collaborator removed from course successfully"})

