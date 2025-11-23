from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.submission import submission_bp
from app.services.utils import api_response
from app.models import Submissions, Feedbacks
from app.extensions import db

@submission_bp.route('/<int:submission_id>', methods=['PATCH'])
@jwt_required()
def edit_feedback(submission_id):
    current_user_id = get_jwt_identity()
    submission = Submissions.query.get(submission_id)

    if not submission:
        return api_response(False, error={"code": "NOT_FOUND", "message": "Submission not found"}, http_code=404)

    # Check if current user is a teacher for this course
    course = submission.question.course
    teacher_ids = [str(t.teacher.id) for t in course.teachers]

    if str(current_user_id) not in teacher_ids:
        return api_response(False, error={"code": "FORBIDDEN", "message": "Not authorized"}, http_code=403)

    data = request.get_json()
    teacher_feedback = data.get("teacher_feedback")
    final_score = data.get("final_score")

    # Ensure feedback exists
    feedback = submission.feedback
    if not feedback:
        from app.models import Feedbacks
        feedback = Feedbacks(submission_id=submission.id, ai_feedback={})
        db.session.add(feedback)

    if teacher_feedback is not None:
        feedback.teacher_feedback = teacher_feedback

    if final_score is not None:
        feedback.final_score = final_score

    db.session.commit()

    return api_response(True, data={
        "submission_id": submission.id,
        "teacher_feedback": feedback.teacher_feedback,
        "final_score": feedback.final_score
    })
