from flask import Blueprint
from app.services.utils import api_response

submission_bp = Blueprint("submission", __name__)

@submission_bp.route("")
def submission_index():
    return api_response(
        True,
        meta={
            "environment": "development",
            "version": "1.0.0",
            "message": "Submission API is running",
        },
    )


from . import patch_feedback, feedback, get_submissions 
