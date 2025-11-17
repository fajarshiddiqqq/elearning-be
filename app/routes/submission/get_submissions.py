from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.submission import submission_bp
from app.services.utils import api_response
from app.models import Submissions, Courses
from app.extensions import db

@submission_bp.route('/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission(submission_id):
    current_user_id = get_jwt_identity()
    submission = Submissions.query.get(submission_id)

    if not submission:
        return api_response(False, error={"code": "NOT_FOUND", "message": "Submission not found"}, http_code=404)

    # Check role: student can only access their own submission
    # Teacher can access if they belong to the course
    course = submission.question.course
    teacher_ids = [str(t.teacher.id) for t in course.teachers]  # assumes course.teachers relationship

    if str(submission.student_id) != current_user_id and current_user_id not in teacher_ids:
        return api_response(False, error={"code": "FORBIDDEN", "message": "Not authorized"}, http_code=403)

    test_results = []
    for tc in submission.question.test_cases:
        test_results.append({
            "test_case_id": tc.id,
            "input": tc.input_data,
            "expected": tc.expected_output
        })

    return api_response(True, data={
        "submission_id": submission.id,
        "question_id": submission.question_id,
        "student_id": submission.student_id,
        "attempt_no": submission.attempt_no,
        "status": submission.status,
        "error_message": submission.error_message,
        "code": submission.code,
        "test_results": test_results,
        "ai_feedback": submission.feedback.ai_feedback if submission.feedback else None,
        "teacher_feedback": submission.feedback.teacher_feedback if submission.feedback else None,
        "final_score": submission.feedback.final_score if submission.feedback else None
    })
