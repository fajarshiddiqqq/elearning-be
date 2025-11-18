from flask import request
from app.routes.auth import auth_bp
from app.services.utils import api_response
from app.services.auth_service import is_user_existing, verify_password
from flask_jwt_extended import create_access_token


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Handle user login.

    Expects JSON payload with 'email' and 'password'.

    :return: Standard API response indicating success or failure.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        error_info = {"code": "INVALID_INPUT", "message": "Email and password are required."}
        return api_response(False, error=error_info, http_code=400)

    stored_user = is_user_existing(email=email)
    if not stored_user:
        error_info = {"code": "USER_NOT_FOUND", "message": "User does not exist."}
        return api_response(False, error=error_info, http_code=404)
    
    if not stored_user.password_hash:
        error_info = {"code": "INVALID_CREDENTIALS", "message": "Password login not set for this user."}
        return api_response(False, error=error_info, http_code=401)

    if not verify_password(stored_user.password_hash, password):
        error_info = {"code": "INVALID_CREDENTIALS", "message": "Incorrect password."}
        return api_response(False, error=error_info, http_code=401)
    
    if not stored_user.is_active:
        error_info = {"code": "INACTIVE_ACCOUNT", "message": "User account is not yet approved or is inactive. For assistance, please contact support."}
        return api_response(False, error=error_info, http_code=403)

    user_data = {
        "id": stored_user.id,
        "name": stored_user.name,
        "email": stored_user.email,
        "role": stored_user.role,
        "is_active": stored_user.is_active,
        "created_at": stored_user.created_at.isoformat(),
        "updated_at": stored_user.updated_at.isoformat(),
    }

    access_token = create_access_token(identity=str(stored_user.id))
    response_data = {"user": user_data, "access_token": access_token}

    return api_response(True, data=response_data)