from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from xb2.models import Comment
from xb2.extensions import db

comment_bp = Blueprint('comment', __name__)



@comment_bp.post('/comments')
@jwt_required()
def create():
    comment = Comment(
        content=request.json['content'],
        postId=request.json['postId'],
        userId=current_user.id
    )
    db.session.add(comment)
    db.session.commit()
    return {
        'id': comment.id
    }

@comment_bp.patch('/comments/<int:comment_id>')
@jwt_required()
def update(comment_id: int):
    comment: Comment = Comment.query.filter_by(userId=current_user.id, id=comment_id).one_or_none()
    if comment is None:
        raise Exception('COMMENT_NOT_FOUND')

    comment.content = request.json['content']
    db.session.commit()
    return {
        'id': comment.id
    }

# delete a comment by comment_id
@comment_bp.delete('/comments/<int:comment_id>')
@jwt_required()
def delete(comment_id: int):
    comment: Comment = Comment.query.filter_by(userId=current_user.id, id=comment_id).one_or_none()
    if comment is None:
        raise Exception('COMMENT_NOT_FOUND')

    db.session.delete(comment)
    db.session.commit()
    return {
        'id': comment.id
    }

# reply a comment by comment_id
@comment_bp.post('/comments/<int:comment_id>/reply')
@jwt_required()
def reply(comment_id: int):
    reply_comment = Comment(
        content=request.json['content'],
        postId=request.json['postId'],
        userId=current_user.id,
        parentId=comment_id
    )
    db.session.add(reply_comment)
    db.session.commit()

    return {
        'id': reply_comment.id
    }