import click
from flask import Flask, jsonify, request, g, current_app
from loguru import logger
from flask_sqlalchemy import SQLAlchemy
import traceback
from typing import cast
import sqlalchemy as sa
import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, JWTManager, current_user
from flask_migrate import Migrate

NAME_IS_REQUIRED = "NAME_IS_REQUIRED"
PASSWORD_IS_REQUIRED = "PASSWORD_IS_REQUIRED"
USER_ALREADY_EXIST = "USER_ALREADY_EXIST"
USER_NOT_EXIST = "USER_NOT_EXIST"
PASSWORD_IS_WRONG = "PASSWORD_IS_WRONG"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@192.168.50.145:5432/xb2_node"
app.secret_key = "hello flask"
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255), unique=True, nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    posts = db.relationship('Post', back_populates='user')
    
    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def own_post(self, post_id: int):
        return any(p.id == post_id for p in self.posts)


@jwt.user_identity_loader
def user_identity_lookup(user: User):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return User.query.filter_by(id=identity).one_or_none()


class Post(db.Model):
    __tablename__ = 'post'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String(255), nullable=False)
    content = sa.Column(sa.Text)
    userId = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='posts')


class File(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    originalname = sa.Column(sa.String(255), nullable=False)
    mimetype = sa.Column(sa.String(255), nullable=False)
    filename = sa.Column(sa.String(255), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)
    postId = sa.Column(sa.Integer, sa.ForeignKey('post.id'))
    userId = sa.Column(sa.Integer, sa.ForeignKey('user.id'))


@app.post("/posts")
@jwt_required()
def post_index():

    title = request.json["title"]
    content = request.json["content"]
    user_id = current_user.id
    post = Post(title=title, content=content, userId=user_id)
    db.session.add(post)
    db.session.commit()

    return {
        "id": post.id
    }


@app.get("/posts")
@jwt_required()
def post_all():
    posts: list["Post"] = current_user.posts
    return [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content
        }
        for post in posts
    ]


@app.get("/posts/<int:post_id>")
@jwt_required()
def post_one(post_id: int):
    post: Post = Post.query.get(post_id)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content
    }


@app.delete("/posts/<int:post_id>")
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


@app.patch("/posts/<int:post_id>")
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


@app.post("/users")
def create_user():
    if request.json.get("name") is None:
        raise Exception(NAME_IS_REQUIRED)
    if request.json.get("password") is None:
        raise Exception(PASSWORD_IS_REQUIRED)

    name = request.json["name"]

    user: User = db.session.query(User.id).filter_by(name=name).first()
    if user is not None:
        raise Exception(USER_ALREADY_EXIST)

    password = request.json["password"]
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = User()
    user.name = name
    user.password = hashed_password.decode('utf-8')

    db.session.add(user)
    db.session.commit()
    return {
        "id": user.id
    }


@app.post('/login')
def login():
    if request.json.get("name") is None:
        raise Exception(NAME_IS_REQUIRED)
    if request.json.get("password") is None:
        raise Exception(PASSWORD_IS_REQUIRED)

    name = request.json["name"]

    user = User.query.filter_by(name=name).one_or_none()
    if user is None:
        raise Exception(USER_NOT_EXIST)

    password = cast(str, request.json["password"])

    if user.check_password(password):
        pass
    else:
        raise Exception(PASSWORD_IS_WRONG)

    access_token = create_access_token(identity=user)
    return {
        "id": user.id,
        "access_token": access_token
    }

@app.cli.command(help="create tables")
@click.option("--drop", is_flag=True, help='create after drop')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.errorhandler(Exception)
def handle_exception(e: Exception):
    error_message = str(e)
    match error_message:
        case "NAME_IS_REQUIRED":
            status_code = 400
            message = "请提供用户名"
        case "PASSWORD_IS_REQUIRED":
            status_code = 400
            message = "请提供用户密码"
        case "USER_ALREADY_EXIST":
            status_code = 409
            message = '用户名已被占用'
        case "USER_NOT_EXIST":
            status_code = 400
            message = '用户不存在'
        case "PASSWORD_IS_WRONG":
            status_code = 400
            message = 'PASSWORD_IS_WRONG'
        case "POST_NOT_FOUND":
            status_code = 400
            message = 'POST_NOT_FOUND'
        case "USER_DOES_NOT_OWN_RESOURCE":
            status_code = 400
            message = "USER_DOES_NOT_OWN_RESOURCE"
        case _:
            status_code = 500
            message = "服务暂时出了点问题"
            logger.error(traceback.format_exc())
    return jsonify({
        "message": message
    }), status_code
