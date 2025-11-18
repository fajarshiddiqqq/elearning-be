from flask import request
from flask_jwt_extended import create_access_token
from app.models import Users
from app.routes.auth import auth_bp
from app.services.utils import api_response
from app.services.auth_service import hash_pashword
from app.extensions import db

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Handle user registration.

    Expects JSON payload with 'name', 'email', 'password', and optional 'role'.

    :return: Standard API response indicating success or failure.
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if not name or not email or not password:
        error_info = {"code": "INVALID_INPUT", "message": "Name, email, and password are required."}
        return api_response(False, error=error_info, http_code=400)
    
    if role not in ['student', 'teacher']:
        error_info = {"code": "INVALID_ROLE", "message": "Role must be one of 'student' or 'teacher'."}
        return api_response(False, error=error_info, http_code=400)
    
    is_active = False if role == 'teacher' else True # Auto-activate students, require approval for others

    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        error_info = {"code": "USER_EXISTS", "message": "A user with this email already exists."}
        return api_response(False, error=error_info, http_code=409)

    password_hash = hash_pashword(password)
    new_user = Users(name=name, email=email, password_hash=password_hash, role=role, is_active=is_active)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        error_info = {"code": "DATABASE_ERROR", "message": str(e)}
        return api_response(False, error=error_info, http_code=500)

    user_data = {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at.isoformat(),
        "updated_at": new_user.updated_at.isoformat(),
    }

    if not new_user.is_active:
        message = "Registration successful. Your account is pending approval."
        return api_response(True, data={"user": user_data}, meta={"message": message})
    
    access_token = create_access_token(identity=str(new_user.id))
    response_data = {"user": user_data, "access_token": access_token}
    return api_response(True, data=response_data)