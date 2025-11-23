from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.question import question_bp
from app.models import Questions, QuestionCollaborators, Users
from app.services.utils import api_response, role_required
from app.extensions import db


# Helper to fetch question and check owner
def get_question_if_owner(question_id, user_id):
    question = Questions.query.get(question_id)
    if not question:
        return None, api_response(
            False,
            error={"code": "QUESTION_NOT_FOUND", "message": "Question not found"},
            http_code=404,
        )

    if question.created_by != user_id:
        return None, api_response(
            False,
            error={
                "code": "FORBIDDEN",
                "message": "Only the owner can manage collaborators",
            },
            http_code=403,
        )

    return question, None


@question_bp.route("/<int:question_id>/collaborators", methods=["POST"])
@jwt_required()
@role_required("teacher")
def add_collaborator(current_user_id, question_id):
    question, error = get_question_if_owner(question_id, current_user_id)
    if error:
        return error

    data = request.get_json()
    email = data.get("email")
    permission = data.get("permission", "viewer")

    if not email:
        return api_response(
            False,
            error={"code": "MISSING_EMAIL", "message": "Email is required"},
            http_code=400,
        )
    
    user = Users.query.filter_by(email=email).first()
    if not user:
        return api_response(
            False,
            error={"code": "USER_NOT_FOUND", "message": "User with this email does not exist"},
            http_code=404,
        )

    if permission not in ["viewer", "editor"]:
        return api_response(
            False,
            error={"code": "INVALID_PERMISSION", "message": "Invalid permission value"},
            http_code=400,
        )
    
    if permission == "editor" and user.role != "teacher":
        return api_response(
            False,
            error={"code": "INVALID_USER_ROLE", "message": "Only teachers can be editors"},
            http_code=400,
        )

    if user.id == question.created_by:  # type: ignore
        return api_response(
            False,
            error={
                "code": "INVALID_OP",
                "message": "Owner cannot be added as collaborator",
            },
            http_code=400,
        )

    existing = QuestionCollaborators.query.filter_by(
        question_id=question_id, user_id=user.id
    ).first()
    if existing:
        return api_response(
            False,
            error={"code": "ALREADY_EXISTS", "message": "Collaborator already exists"},
            http_code=400,
        )

    new_collab = QuestionCollaborators(
        question_id=question_id, user_id=user.id, permission=permission
    )
    db.session.add(new_collab)
    db.session.commit()

    return api_response(
        True,
        data={
            "collaborator": {
                "id": user.id,
                "name": user.name if user else None,
                "permission": permission,
            }
        },
        meta={"message": "Collaborator added"},
        http_code=201,
    )


@question_bp.route("/<int:question_id>/collaborators", methods=["PATCH"])
@jwt_required()
@role_required("teacher")
def update_collaborator_permission(current_user_id, question_id):
    _, error = get_question_if_owner(question_id, current_user_id)
    if error:
        return error

    data = request.get_json()
    user_id = data.get("user_id")
    new_permission = data.get("permission")

    if not user_id or not new_permission:
        return api_response(
            False,
            error={
                "code": "MISSING_FIELDS",
                "message": "user_id and permission are required",
            },
            http_code=400,
        )

    if new_permission not in ["viewer", "editor"]:
        return api_response(
            False,
            error={"code": "INVALID_PERMISSION", "message": "Invalid permission value"},
            http_code=400,
        )
    
    user = Users.query.get(user_id)
    if not user:
        return api_response(
            False,
            error={"code": "USER_NOT_FOUND", "message": "User not found"},
            http_code=404,
        )
    
    if new_permission == "editor" and user.role != "teacher":
        return api_response(
            False,
            error={"code": "INVALID_USER_ROLE", "message": "Only teachers can be editors"},
            http_code=400,
        )

    collab = QuestionCollaborators.query.filter_by(
        question_id=question_id, user_id=user_id
    ).first()
    if not collab:
        return api_response(
            False,
            error={
                "code": "COLLABORATOR_NOT_FOUND",
                "message": "Collaborator not found",
            },
            http_code=404,
        )

    collab.permission = new_permission
    db.session.commit()

    return api_response(
        True,
        data={
            "message": "Permission updated",
            "collaborator": {"id": user_id, "permission": new_permission},
        },
    )


@question_bp.route(
    "/<int:question_id>/collaborators/<int:collab_user_id>", methods=["DELETE"]
)
@jwt_required()
@role_required("teacher")
def remove_collaborator(current_user_id, question_id, collab_user_id):
    _, error = get_question_if_owner(question_id, current_user_id)
    if error:
        return error

    collab = QuestionCollaborators.query.filter_by(
        question_id=question_id, user_id=collab_user_id
    ).first()
    if not collab:
        return api_response(
            False,
            error={
                "code": "COLLABORATOR_NOT_FOUND",
                "message": "Collaborator not found",
            },
            http_code=404,
        )

    db.session.delete(collab)
    db.session.commit()

    return api_response(True, meta={"message": "Collaborator removed"})


@question_bp.route("/<int:question_id>/collaborators", methods=["GET"])
@jwt_required()
def list_collaborators(question_id):
    current_user_id = int(get_jwt_identity())

    question = Questions.query.get(question_id)
    if not question:
        return api_response(
            False,
            error={"code": "QUESTION_NOT_FOUND", "message": "Question not found"},
            http_code=404,
        )

    # Owner or collaborator can list collaborators
    if not (
        question.created_by == current_user_id
        or any(c.user_id == current_user_id for c in question.collaborators)
    ):
        return api_response(
            False,
            error={
                "code": "FORBIDDEN",
                "message": "You do not have access to this question",
            },
            http_code=403,
        )

    collaborators = [
        {
            "id": c.user_id,
            "name": Users.query.get(c.user_id).name if Users.query.get(c.user_id) else None,  # type: ignore
            "permission": c.permission,
            "added_at": c.added_at,
        }
        for c in question.collaborators
    ]

    return api_response(True, data={"collaborators": collaborators})
