from flask import Blueprint
from app.services.utils import api_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("")
def auth_index():
    return api_response(
        True,
        meta={
            "environment": "development",
            "version": "1.0.0",
            "message": "Auth API is running",
        },
    )


from . import (
    me,
    register,
    login,
    google_oauth,
)
