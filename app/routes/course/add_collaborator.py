from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.course import course_bp
from app.models import Courses, CourseTeachers, Users
from app.extensions import db
from app.services.utils import api_response

@course_bp.route("/<int:course_id>/teachers", methods=["POST"])
@jwt_required()
def add_collaborator(course_id):
    course = Courses.query.get(course_id)
    if not course:
        return api_response(False, error={"code": "COURSE_NOT_FOUND", "message": "Course not found"}, http_code=404)

    current_user_id = get_jwt_identity()
    # Only owner can add collaborator
    owner = next((t for t in course.teachers if str(t.teacher.id) == current_user_id and t.role == "owner"), None)
    if not owner:
        return api_response(False, error={"code": "FORBIDDEN", "message": "Only owner can add collaborators"}, http_code=403)

    data = request.json
    if not data:
        return api_response(False, error={"code": "NO_DATA", "message": "No data provided"}, http_code=400)

    teacher_id = data.get("teacher_id")
    if not teacher_id:
        return api_response(False, error={"code": "NO_TEACHER_ID", "message": "teacher_id is required"}, http_code=400)

    # Check if user exists and is a teacher
    user = Users.query.get(teacher_id)
    if not user or user.role != "teacher":
        return api_response(False, error={"code": "INVALID_TEACHER", "message": "Teacher not found or invalid"}, http_code=400)

    # Check if already added
    exists = CourseTeachers.query.filter_by(course_id=course_id, teacher_id=teacher_id).first()
    if exists:
        return api_response(False, error={"code": "ALREADY_EXISTS", "message": "Teacher already a collaborator"}, http_code=400)

    new_collab = CourseTeachers(course_id=course_id, teacher_id=teacher_id)
    db.session.add(new_collab)
    db.session.commit()

    return api_response(True, data={"message": f"{user.name} added as collaborator successfully"})