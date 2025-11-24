from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.question import question_bp
from app.models import Questions, QuestionCollaborators, Users
from app.services.utils import api_response


@question_bp.route('/mine', methods=['GET'])
@jwt_required()
def get_private_questions():
    current_user_id = int(get_jwt_identity())

    questions = Questions.query.filter(
        (Questions.created_by == current_user_id) |
        (Questions.collaborators.any(QuestionCollaborators.user_id == current_user_id))  # type: ignore
    ).all()

    result = []
    for q in questions:
        role = "owner" if q.created_by == current_user_id else next(
            (collab.permission for collab in q.collaborators if collab.user_id == current_user_id),
            None
        )
        result.append({
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "function_name": q.function_name,
            "difficulty": q.difficulty,
            "language": "python",
            "tags": q.tags,
            "role": role,
            "updated_at": q.updated_at,
        })

    return api_response(True, data={"questions": result})



@question_bp.route('/public', methods=['GET'])
def get_public_questions():
    questions = Questions.query.filter_by(visibility='public').all()
    return api_response(True, data={"questions": [
        {
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "function_name": q.function_name,
            "language": "python",
            "difficulty": q.difficulty,
            "tags": q.tags,
            "created_by": q.created_by
        }
        for q in questions
    ]})


@question_bp.route('/<int:question_id>', methods=['GET'])
@jwt_required(optional=True)
def get_question_by_id(question_id):
    current_user_id = get_jwt_identity()  # None if unauthenticated
    current_user_id = int(current_user_id) if current_user_id else None

    question = Questions.query.get_or_404(question_id)

    # Check access
    if question.visibility == 'private':
        if not current_user_id or (
            question.created_by != current_user_id and
            not any(collab.user_id == current_user_id for collab in question.collaborators)
        ):
            return api_response(False, error={"code": "FORBIDDEN", "message": "Access forbidden"}, http_code=403)

    # Determine role
    if current_user_id == question.created_by:
        role = "owner"
    else:
        collab = next((c for c in question.collaborators if c.user_id == current_user_id), None)
        role = collab.permission if collab else "viewer"

    # Prepare test cases
    is_student = Users.query.get(current_user_id).role == 'student' if current_user_id else False # type: ignore
    test_cases_data = [
        {
            "id": tc.id,
            "input_data": tc.input_data,
            "expected_output": tc.expected_output,
            **({} if is_student else {"is_hidden": tc.is_hidden})
        }
        for tc in question.test_cases
        if not (is_student and tc.is_hidden)
    ]

    question_data = {
        "id": question.id,
        "title": question.title,
        "description": question.description,
        "function_name": question.function_name,
        "starter_code": question.starter_code,
        "difficulty": question.difficulty,
        "language": "python",
        "tags": question.tags,
        "test_cases": test_cases_data,
        "role": role,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }

    if not is_student:
        question_data["custom_instructions"] = question.custom_instructions
        question_data["rubric"] = {"criteria": question.rubric.criteria, "tone": question.rubric.tone} if question.rubric else None
        question_data['visibility'] = question.visibility


    return api_response(True, data={"question": question_data})


@question_bp.route('/<int:question_id>/preview', methods=['GET'])
@jwt_required(optional=True)
def preview_question(question_id):
    question = Questions.query.get_or_404(question_id)

    if question.visibility == 'private':
        current_user_id = get_jwt_identity()  # None if unauthenticated
        current_user_id = int(current_user_id) if current_user_id else None
        if not current_user_id or (
            question.created_by != current_user_id and
            not any(collab.user_id == current_user_id for collab in question.collaborators)
        ):
            return api_response(False, error={"code": "FORBIDDEN", "message": "Access forbidden"}, http_code=403)
    
    question_data = {
        "id": question.id,
        "title": question.title,
        "description": question.description,
        "function_name": question.function_name,
        "difficulty": question.difficulty,
        "language": "python",
        "tags": question.tags,
        "created_at": question.created_at,
    }

    return api_response(True, data={"question": question_data})