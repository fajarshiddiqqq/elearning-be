from app.routes.course import course_bp
from app.models import Courses, CourseTeachers
from app.extensions import db
from app.services.utils import api_response, role_required
from flask_jwt_extended import jwt_required
from flask import request


@course_bp.route("/create", methods=["POST"])
@jwt_required()
@role_required("teacher", "admin")
def create_course(current_user_id):
    """
    Create a new course.
    Expects JSON payload with 'title' and optional 'description'.
    :return: Standard API response with created course details.
    """
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")

    if not title:
        return api_response(
            False,
            error={"code": "TITLE_REQUIRED", "message": "Title is required"},
            http_code=400,
        )

    new_course = Courses(title=title, description=description, created_by=current_user_id)
    db.session.add(new_course)
    db.session.flush()

    new_course_teacher = CourseTeachers(course_id=new_course.id, teacher_id=current_user_id, role='owner')
    db.session.add(new_course_teacher)
    db.session.commit()

    return api_response(
        True,
        data={
            "id": new_course.id,
            "title": new_course.title,
            "description": new_course.description,
            "created_by": new_course.created_by,
            "created_at": new_course.created_at,
            "updated_at": new_course.updated_at,
        },
        http_code=201,
    )
