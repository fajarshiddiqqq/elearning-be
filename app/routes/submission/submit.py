from flask import request
from app.routes.submission import submission_bp
from app.services.utils import api_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Users, Questions, Submissions
from app.services.submission_service import evaluate_python_code
from app.extensions import db
import json

@submission_bp.route('/', methods=['POST'])
@jwt_required()
def submit_code():
    user_id = get_jwt_identity()
    user = Users.query.get(user_id)
    if not user:
        return api_response(False,
            error={"code": "USER_NOT_FOUND", "message": "User not found."},
            http_code=404
        )

    data = request.get_json()
    question_id = data.get("question_id")
    code = data.get("code")
    language = data.get("language", "python")

    if not question_id or not code:
        return api_response(False,
            error={"code": "INVALID_INPUT", "message": "Question ID and code are required."},
            http_code=400
        )

    question = Questions.query.get(question_id)
    if not question:
        return api_response(False,
            error={"code": "QUESTION_NOT_FOUND", "message": "Question not found."},
            http_code=404
        )

    # MVP: only python
    if language != "python":
        return api_response(False,
            error={"code": "LANG_NOT_SUPPORTED", "message": "Only Python supported for MVP."},
            http_code=400
        )

    # Build TEST_CASES from DB
    TEST_CASES = []
    for tc in question.test_cases:
        raw_input = json.loads(tc.input_data)

        if isinstance(raw_input, (list, tuple)):
            args = tuple(raw_input)
        else:
            args = (raw_input,)

        expected = json.loads(tc.expected_output)
        TEST_CASES.append((args, expected))

    # ========= Attempt number logic =========
    last_submission = (
        Submissions.query
        .filter_by(question_id=question_id, student_id=user_id)
        .order_by(Submissions.attempt_no.desc()) # type: ignore
        .first()
    )

    if last_submission:
        next_attempt = last_submission.attempt_no + 1
    else:
        next_attempt = 1
    # ========================================

    # Create submission record
    submission = Submissions(
        question_id=question_id,
        student_id=user_id,
        code=code,
        status="pending",
        error_message=None,
        score=None,
        attempt_no=next_attempt
    )
    db.session.add(submission)
    db.session.commit()   # must commit to get submission.id

    # Execute the code
    result = evaluate_python_code(code, TEST_CASES, question.function_name)

    # Update submission with results
    submission.status = result["status"]
    submission.error_message = result.get("error_message")
    submission.score = result.get("score")

    result["submission_id"] = submission.id

    db.session.commit()

    return api_response(True, data=result)
