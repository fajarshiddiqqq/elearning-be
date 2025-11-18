from flask import request, url_for, session, redirect
from flask_jwt_extended import create_access_token
from app.routes.auth import auth_bp
from app.services.utils import api_response
from app.extensions import oauth, db
from app.models import Users
from app.config import Config

@auth_bp.route("/test/google", methods=["GET"])
def test_google_config():
    """Test endpoint to verify Google OAuth configuration"""
    from flask import current_app
    
    config_status = {
        "client_id_set": bool(current_app.config.get('GOOGLE_OAUTH_CLIENT_ID')),
        "client_secret_set": bool(current_app.config.get('GOOGLE_OAUTH_CLIENT_SECRET')),
        "secret_key_set": bool(current_app.config.get('SECRET_KEY')),
        "redirect_uri": url_for('apis.auth.google_authorize', _external=True)
    }
    
    return api_response(True, data=config_status)

@auth_bp.route('/login/google', methods=['GET'])
def google_login():
    """
    Redirect user to Google OAuth login page.

    :return: Redirect response to Google's OAuth 2.0 authorization endpoint.
    """
    role = request.args.get('role', 'student')
    
    if role not in ['student', 'teacher']:
        error_info = {"code": "INVALID_ROLE", "message": "Role must be 'student' or 'teacher'."}
        return api_response(False, error=error_info, http_code=400)
    
    session['oauth_role'] = role
    
    redirect_uri = url_for('apis.auth.google_authorize', _external=True)
    if oauth.google:
        return oauth.google.authorize_redirect(redirect_uri)
    else:
        error_info = {"code": "OAUTH_NOT_CONFIGURED", "message": "Google OAuth is not properly configured."}
        return api_response(False, error=error_info, http_code=500)


@auth_bp.route("/authorize/google", methods=["GET"])
def google_authorize():
    """
    Handle Google OAuth callback.
    
    :return: Standard API response with user data and access token
    """
    try:
        # Get the access token from Google
        if not oauth.google:
            error_info = {"code": "OAUTH_NOT_CONFIGURED", "message": "Google OAuth is not properly configured."}
            return api_response(False, error=error_info, http_code=500)
        
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google
        user_info = token.get('userinfo')
        
        if not user_info:
            error_info = {"code": "OAUTH_ERROR", "message": "Failed to retrieve user information from Google."}
            return api_response(False, error=error_info, http_code=400)
        
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('sub')
        
        if not email:
            error_info = {"code": "OAUTH_ERROR", "message": "Email not provided by Google."}
            return api_response(False, error=error_info, http_code=400)
        
        # Get role from session (set during login initiation)
        role = session.pop('oauth_role', 'student')
        
        # Check if user already exists
        existing_user = Users.query.filter_by(email=email).first()
        
        if existing_user:
            # User exists - update Google ID if not set
            if not existing_user.google_id:
                existing_user.google_id = google_id
                db.session.commit()
            
            user_data = {
                "id": existing_user.id,
                "name": existing_user.name,
                "email": existing_user.email,
                "role": existing_user.role,
                "is_active": existing_user.is_active,
                "created_at": existing_user.created_at.isoformat(),
                "updated_at": existing_user.updated_at.isoformat(),
            }
            
            if not existing_user.is_active:
                error_info = {"code": "INACTIVE_ACCOUNT", "message": "User account is inactive."}
                return api_response(False, error=error_info, http_code=403)
            
            access_token = create_access_token(identity=str(existing_user.id))
            response_data = {"user": user_data, "access_token": access_token}
            
            return api_response(True, data=response_data, meta={"message": "Login successful"})
            
        else:
            # New user - create account
            is_active = False if role == 'teacher' else True
            
            new_user = Users(
                name=name,
                email=email,
                google_id=google_id,
                role=role,
                is_active=is_active,
                password_hash=None
            )
            
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

            if role == 'teacher':
                meta_message = "Registration successful. Your account is pending approval. redirecting..."
                return api_response(True, data=user_data, meta={"message": meta_message})
            
            access_token = create_access_token(identity=str(new_user.id))
            response_data = {"user": user_data, "access_token": access_token}
            redirect_uri = f"{Config.FRONTEND_URL}/oauth/callback?token={access_token}" 
            return redirect(redirect_uri)
    
    except Exception as e:
        error_info = {"code": "OAUTH_ERROR", "message": f"OAuth authentication failed: {str(e)}"}
        return api_response(False, error=error_info, http_code=400)