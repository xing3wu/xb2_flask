from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from xb2.models import User

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


@jwt.user_identity_loader
def user_identity_lookup(user: User):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return User.query.filter_by(id=identity).one_or_none()