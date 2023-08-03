from flask import Blueprint, request
from xb2.models import Tag
from flask_jwt_extended import jwt_required
from xb2.extensions import db

tag_bp = Blueprint('tag', __name__)


@tag_bp.post('/tags')
def create_one():
    name = request.json.get('name')
    if name is None:
        raise Exception('TAG_NAME_NOT_FOUND')
    
    tag: Tag = Tag.query.filter_by(name=name).one_or_none()
    if tag is not None:
        raise Exception('TAG_IS_EXISTS')
    
    wait_to_add: Tag = Tag(name=name)
    db.session.add(wait_to_add)
    db.session.commit()

    return {
        "id": wait_to_add.id
    }