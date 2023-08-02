from flask import Blueprint, request
from typing import cast
from xb2.models import User
from flask_jwt_extended import create_access_token
from datetime import timedelta
from xb2.extensions import db


user_bp = Blueprint('user', __name__)

@user_bp.post("/users")
def create_one():
    if request.json.get("name") is None:
        raise Exception("NAME_IS_REQUIRED")
    if request.json.get("password") is None:
        raise Exception("PASSWORD_IS_REQUIRED")

    name = request.json["name"]
    user: User = User.query.filter_by(name=name).one_or_none()
    if user is not None:
        raise Exception("USER_ALREADY_EXIST")

    password = request.json["password"]

    user = User()
    user.name = name
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return {
        "id": user.id
    }