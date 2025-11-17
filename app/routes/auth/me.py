from app.routes.auth import auth_bp
from app.models import Users
from app.extensions import db
from app.services.utils import api_response
from flask_jwt_extended import jwt_required, get_jwt_identity

@auth_bp.route("/me")
@jwt_required()
def get_current_user():
    """
    Retrieve information about the currently authenticated user.

    :return: Standard API response with user details.
    """
    current_user_id = get_jwt_identity()
    user = Users.query.get(current_user_id)

    if not user:
        error_info = {"code": "USER_NOT_FOUND", "message": "User does not exist."}
        return api_response(False, error=error_info, http_code=404)

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    }

    return api_response(True, data=user_data)