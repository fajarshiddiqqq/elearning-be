from flask import request
from flask_jwt_extended import jwt_required
from app.routes.question import question_bp
from app.models import Questions, QuestionCollaborators, Rubrics, TestCases
from app.services.utils import api_response, role_required
from app.services.question_service import validate_test_cases, validate_rubric
from app.extensions import db

# Helper to verify if user can edit the question
def user_can_edit(question, user_id):
    if question.created_by == user_id:
        return True
    return QuestionCollaborators.query.filter_by(
        question_id=question.id,
        user_id=user_id,
        permission='editor'
    ).first() is not None

@question_bp.route("/<int:question_id>/rubric", methods=["PUT"])
@jwt_required()
@role_required("teacher")
def update_question_rubric(current_user_id, question_id):
    data = request.get_json()

    question = Questions.query.get(question_id)
    if not question:
        return api_response(False, error={"code": "NOT_FOUND", "message": "Question not found."}, http_code=404)
    
    if not user_can_edit(question, current_user_id):
        return api_response(False, error={"code": "FORBIDDEN", "message": "You do not have permission to update this question's rubric."}, http_code=403)

    rubric_data = data.get("rubric")
    if not rubric_data:
        return api_response(False, error={"code": "INVALID_DATA", "message": "Rubric data is required."}, http_code=400)
    
    try:
        validate_rubric(rubric_data)
    except ValueError as e:
        return api_response(False, error={"code": "INVALID_DATA", "message": str(e)}, http_code=400)

    # Delete old rubric
    if question.rubric:
        db.session.delete(question.rubric)
    
    # Create new rubric
    new_rubric = Rubrics(
        question_id=question_id,
        criteria=rubric_data['criteria'],
        tone=rubric_data.get('tone', 'neutral')
    )
    db.session.add(new_rubric)
    db.session.commit()

    return api_response(True, meta={"message": "Rubric updated successfully."})


@question_bp.route("/<int:question_id>/test-cases", methods=["PUT"])
@jwt_required()
@role_required("teacher")
def update_question_test_cases(current_user_id, question_id):
    data = request.get_json()

    question = Questions.query.get(question_id)
    if not question:
        return api_response(False, error={"code": "NOT_FOUND", "message": "Question not found."}, http_code=404)

    if not user_can_edit(question, current_user_id):
        return api_response(False, error={"code": "FORBIDDEN", "message": "You do not have permission to update this question's test cases."}, http_code=403)

    test_cases_data = data.get("test_cases")
    if not test_cases_data:
        return api_response(False, error={"code": "INVALID_DATA", "message": "Test case data is required and must not be empty."}, http_code=400)

    try:
        validate_test_cases(test_cases_data)
    except ValueError as e:
        return api_response(False, error={"code": "INVALID_DATA", "message": str(e)}, http_code=400)

    # Delete old test cases
    TestCases.query.filter_by(question_id=question_id).delete()

    # Add new test cases
    for tc in test_cases_data:
        new_tc = TestCases(
            question_id=question_id,
            input_data=tc['input_data'],
            expected_output=tc['expected_output'],
            is_hidden=tc.get('is_hidden', False)
        )
        db.session.add(new_tc)

    db.session.commit()

    return api_response(True, meta={"message": "Test cases updated successfully."})
