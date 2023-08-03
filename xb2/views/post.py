from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from xb2.extensions import db
from xb2.models import Post, Tag

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

# get all tags for a post
@post_bp.get("/posts/<int:post_id>/tag")
def get_all_tag(post_id: int):
    post: Post = Post.query.get(post_id)
    return {
        "id": post.id,
        "tags": [
            tag.name
            for tag in post.tags
        ]
    }

# add a tag for a post
@post_bp.post("/posts/<int:post_id>/tag")
def create_tag(post_id: int):
    post: Post = Post.query.get(post_id)
    if post is None:
        raise Exception("POST_NOT_FOUND")

    tag_name = request.json.get("name")
    if tag_name is None:
        raise Exception("TAG_NAME_NOT_FOUND")
    
    tag: Tag = Tag.query.filter_by(name=tag_name).one_or_none()
    if tag is None:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit()
    
    post.tags.append(tag)
    db.session.commit()
    return {
        "id": post.id,
    }

# delete a tag for a post
@post_bp.delete("/posts/<int:post_id>/tag")
def delete_tag(post_id: int):
    post: Post = Post.query.get(post_id)
    if post is None:
        raise Exception("POST_NOT_FOUND")

    tag_name = request.json.get("name")
    if tag_name is None:
        raise Exception("TAG_NAME_NOT_FOUND")
    
    tag: Tag = Tag.query.filter_by(name=tag_name).one_or_none()
    if tag is None:
        raise Exception("TAG_NOT_FOUND")
    
    post.tags.remove(tag)
    db.session.commit()
    return {
        "id": post.id,
    }