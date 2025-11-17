from app.models import Users
from app.extensions import bcrypt


def is_user_existing(email: str | None = None) -> Users | None:
    """
    Check if a user with the given username or email already exists.

    :param email: The email to check.
    :return: True if user exists, False otherwise.
    """
    if email:
        user = Users.query.filter_by(email=email).first()
        if user:
            return user
    return None

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """
    Verify a provided password against the stored hashed password.

    :param stored_password_hash: The hashed password stored in the database.
    :param provided_password: The plaintext password provided by the user.
    :return: True if the password matches, False otherwise.
    """
    return bcrypt.check_password_hash(stored_password_hash, provided_password)

def hash_pashword(password: str) -> str:
    """
    Hash a plaintext password.

    :param password: The plaintext password to hash.
    :return: The hashed password.
    """
    return bcrypt.generate_password_hash(password).decode('utf-8')