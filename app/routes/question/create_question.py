from flask import request
from flask_jwt_extended import jwt_required
from app.routes.question import question_bp
from app.models import Questions, Rubrics, TestCases
from app.services.utils import api_response, role_required
from app.services.question_service import validate_test_cases, validate_rubric
from app.extensions import db


@question_bp.route("/create", methods=["POST"])
@jwt_required()
@role_required("teacher")
def create_question(current_user_id):
    data = request.get_json()

    # main question fields
    title = data.get('title')
    description = data.get('description')
    function_name = data.get('function_name')
    if not title or not description or not function_name:
        return api_response(False, error={"code": "INVALID_DATA", "message": "Title, description, and function name are required"}, http_code=400)

    # optional
    custom_instructions = data.get('custom_instructions')
    starter_code = data.get('starter_code')
    difficulty = data.get('difficulty', 'medium')
    visibility = data.get('visibility', 'private')
    tags = data.get('tags', [])
    
    # test_cases
    test_cases_data = data.get('test_cases', [])
    if not test_cases_data:
        return api_response(False, error={"code": "INVALID_DATA", "message": "At least one test case is required"}, http_code=400)
    
    try:
        validate_test_cases(test_cases_data)
    except ValueError as e:
        return api_response(False, error={"code": "INVALID_DATA", "message": str(e)}, http_code=400)

    # rubric
    rubric_data = data.get('rubric') 
    if not rubric_data:
        return api_response(False, error={"code": "INVALID_DATA", "message": "Rubric data is required"}, http_code=400)

    try:
        validate_rubric(rubric_data)
    except ValueError as e:
        return api_response(False, error={"code": "INVALID_DATA", "message": str(e)}, http_code=400)
    
    new_question = Questions(
        title=title,
        description=description,
        function_name=function_name,
        custom_instructions=custom_instructions,
        starter_code=starter_code,
        difficulty=difficulty,
        tags=tags,
        visibility=visibility,
        created_by=current_user_id
    )
    db.session.add(new_question)
    db.session.flush()  # to get question.id

    # add test cases
    for tc in test_cases_data:
        db.session.add(TestCases(
            question_id=new_question.id,
            input_data=tc['input_data'],
            expected_output=tc['expected_output'],
            is_hidden=tc.get('is_hidden', False)
        ))

    # add rubric
    rubric = Rubrics(
        question_id=new_question.id,
        criteria=rubric_data['criteria'],
        tone=rubric_data.get('tone', 'neutral')
    )
    db.session.add(rubric)
    db.session.commit()

    return api_response(True, data={"question_id": new_question.id}, meta={"message": "Question created successfully."}, http_code=201)