from app.routes.submission import submission_bp
from app.services.utils import api_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Questions, Submissions, Feedbacks
from app.extensions import db
from app.services.ai_feedback import generate_feedback

@submission_bp.route('/<int:submission_id>/feedback', methods=['GET'])
@jwt_required()
def get_feedback(submission_id):
    submission = Submissions.query.get(submission_id)
    if not submission:
        return api_response(False,
            error={"code": "SUBMISSION_NOT_FOUND", "message": "Submission not found."},
            http_code=404
        )
    
    user_id = int(get_jwt_identity())
    if submission.student_id != user_id:
        return api_response(False,
            error={"code": "UNAUTHORIZED", "message": "You do not have access to this submission."},
            http_code=403
        )
    
    if submission.status not in ['failed', 'passed']:
        return api_response(False,
            error={"code": "INVALID_SUBMISSION_STATUS", "message": "Feedback can only be generated for completed submissions."},
            http_code=400
        )
    
    old_feedback = Feedbacks.query.filter_by(submission_id=submission.id).first()
    if old_feedback:
        return api_response(True, data={"feedback": old_feedback.ai_feedback})
    
    question = Questions.query.get(submission.question_id)
    if not question:
        return api_response(False,
            error={"code": "QUESTION_NOT_FOUND", "message": "Question not found."},
            http_code=404
        )
    
    feedback = generate_feedback(
        status=submission.status,
        code=submission.code,
        rubric=question.rubric,
        score=submission.score,
        custom_instructions=question.custom_instructions
    )

    new_feedback = Feedbacks(
        submission_id=submission.id,
        ai_feedback=feedback
    )
    db.session.add(new_feedback)
    db.session.commit()

    return api_response(True, data={"feedback": feedback})