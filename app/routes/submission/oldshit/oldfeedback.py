from flask import request
from app.routes.submission import submission_bp
from app.services.utils import api_response
from app.services.submission_service import run_submission
from flask_jwt_extended import jwt_required, get_jwt_identity


@submission_bp.route('/feedback', methods=['POST'])
@jwt_required()
def create_submission():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    question_id = data.get("question_id")
    code = data.get("code")

    if not question_id or not code:
        return api_response(
            False,
            error={"code": "INVALID_INPUT", "message": "Question ID and code are required."},
            http_code=400
        )

    try:
        submission = run_submission(
            student_id=current_user_id,
            question_id=question_id,
            code=code
        )
    except Exception as e:
        return api_response(
            False,
            error={"code": "SUBMISSION_ERROR", "message": str(e)},
            http_code=500
        )

    return api_response(True, data={
        "submission_id": submission.id,
        "status": submission.status,
        "attempt_no": submission.attempt_no,
        "ai_feedback": submission.feedback.ai_feedback if submission.feedback else None
    })
