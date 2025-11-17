from flask import jsonify
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models import Users

def api_response(status: bool, data=None, meta=None, error=None, http_code=200):
    """
    Standard wrapper for API JSON responses.

    :param status: Boolean indicating success (True) or failure (False).
    :param data: The primary resource(s) being returned (list or dict).
    :param meta: Optional dictionary for metadata (e.g., pagination).
    :param error: Optional dictionary for error details.
    :param http_code: The HTTP status code to return.
    :return: A Flask Response object with the standard JSON structure.
    """
    response = {
        "status": status,
        "meta": meta if meta is not None else {},
        "data": data,
        # Add error only if present
    }
    if error is not None:
        response["error"] = error
        
    return jsonify(response), http_code

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            if not user_id:
                return api_response(False, error={"code": "AUTH_REQUIRED", "message": "Authentication required."}, http_code=401)

            user = Users.query.get(user_id)
            if not user:
                return api_response(False, error={"code": "USER_NOT_FOUND", "message": "User not found."}, http_code=401)
            
            if user.role not in roles:
                return api_response(False, error={"code": "FORBIDDEN", "message": "Forbidden access."}, http_code=403)

            from flask import g
            g.current_user = user

            # Expose the authenticated user id to the wrapped route.
            kwargs.setdefault("current_user_id", user.id)

            return f(*args, **kwargs)
        return wrapper
    return decorator
