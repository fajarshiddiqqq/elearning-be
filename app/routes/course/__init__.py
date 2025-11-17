from flask import Blueprint
from app.services.utils import api_response

course_bp = Blueprint("course", __name__)


@course_bp.route("")
def course_index():
    return api_response(
        True,
        meta={
            "environment": "development",
            "version": "1.0.0",
            "message": "Course API is running",
        },
    )


from . import (
    add_collaborator,
    create_course,
    delete_course,
    edit_course,
    get_course_details,
    get_courses,
    remove_collaborator,
)
