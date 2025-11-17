from flask import Flask
from app.extensions import db, migrate, jwt, bcrypt, oauth
from app.config import Config
from app.models import *
from app.services.utils import api_response


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
        client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    from app.routes import apis_bp

    app.register_blueprint(apis_bp, url_prefix="/")

    @app.errorhandler(404)
    def page_not_found(e):
        return api_response(False, http_code=404, error=str(e))

    return app
