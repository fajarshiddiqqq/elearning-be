from flask import Blueprint
from app.services.utils import api_response

question_bp = Blueprint("question", __name__)

@question_bp.route("")
def question_index():
    return api_response(
        True,
        meta={
            "environment": "development",
            "version": "1.0.0",
            "message": "Question API is running",
        },
    )


from . import (
    collaboration,
    create_question, 
    get_questions, 
    update_question,
    delete_question
)