from flask import Blueprint, request
from typing import cast
from xb2.models import User
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/login')
def login():
    if request.json.get("name") is None:
        raise Exception("NAME_IS_REQUIRED")
    if request.json.get("password") is None:
        raise Exception("PASSWORD_IS_REQUIRED")

    name = request.json["name"]

    user: User = User.query.filter_by(name=name).one_or_none()
    if user is None:
        raise Exception("USER_NOT_EXIST")

    password = cast(str, request.json["password"])

    if user.validate_password(password):
        pass
    else:
        raise Exception("PASSWORD_IS_WRONG")

    access_token = create_access_token(identity=user, expires_delta=timedelta(days=1))
    return {
        "id": user.id,
        "access_token": access_token
    }