from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from xb2.extensions import db
from xb2.models import Post

post_bp = Blueprint('post', __name__)

@post_bp.post("/posts")
@jwt_required()
def create_one():

    title = request.json["title"]
    content = request.json["content"]
    user_id = current_user.id
    post = Post(title=title, content=content, userId=user_id)
    db.session.add(post)
    db.session.commit()

    return {
        "id": post.id
    }


@post_bp.get("/posts")
@jwt_required()
def get_all():
    posts: list["Post"] = current_user.posts
    return [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content
        }
        for post in posts
    ]

@post_bp.get("/posts/<int:post_id>")
@jwt_required()
def get_one(post_id: int):
    post: Post = Post.query.get(post_id)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content
    }

@post_bp.delete("/posts/<int:post_id>")
@jwt_required()
def post_del(post_id: int):
    post: Post = Post.query.get(post_id)
    if post is None:
        raise Exception("POST_NOT_FOUND")

    if current_user.own_post(post.id):
        pass
    else:
        raise Exception("USER_DOES_NOT_OWN_RESOURCE")

    db.session.delete(post)
    db.session.commit()
    return {
        "id": post.id
    }

@post_bp.patch("/posts/<int:post_id>")
@jwt_required()
def post_update(post_id: int):
    post: Post = Post.query.get(post_id)
    if post is None:
        raise Exception("POST_NOT_FOUND")

    if current_user.own_post(post.id):
        pass
    else:
        raise Exception("USER_DOES_NOT_OWN_RESOURCE")

    if request.json.get("title", None):
        post.title = request.json["title"]
    if request.json.get("content", None):
        post.content = request.json["content"]


    db.session.commit()
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content
    }