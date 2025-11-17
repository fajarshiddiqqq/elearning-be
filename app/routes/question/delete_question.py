from flask import request
from flask_jwt_extended import jwt_required
from app.routes.question import question_bp
from app.models import Questions
from app.services.utils import api_response, role_required
from app.extensions import db

@question_bp.route("/<int:question_id>", methods=["DELETE"])
@jwt_required()
@role_required("teacher")
def delete_question(current_user_id, question_id):
    question = Questions.query.get(question_id)
    
    if not question:
        return api_response(False, error={"code": "NOT_FOUND", "message": "Question not found."}, http_code=404)
    
    if question.created_by != current_user_id:
        return api_response(False, error={"code": "FORBIDDEN", "message": "Only the owner can delete this question."}, http_code=403)
    
    db.session.delete(question)
    db.session.commit()

    return api_response(True, meta={"message": "Question and its related data deleted successfully."})
