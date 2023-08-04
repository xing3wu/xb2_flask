from flask import Flask, jsonify
import click
from loguru import logger
from xb2.extensions import db, jwt, migrate
from xb2.settings import config
import traceback
from xb2.views.auth import auth_bp
from xb2.views.file import file_bp
from xb2.views.user import user_bp
from xb2.views.post import post_bp
from xb2.views.tag import tag_bp
from xb2.views.comment import comment_bp
from xb2.utils import profile

@profile
def create_app(config_name: str) -> "Flask":
    app = Flask("xb2")
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_commands(app)
    register_exception_handlers(app)
    register_routes(app)
    return app

@profile
def register_extensions(app: Flask) -> None:
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

@profile
def register_exception_handlers(app: Flask) -> None:
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
            case "FILE_NOT_FOUND":
                status_code = 400
                message = 'FILE_NOT_FOUND'
            case "USER_DOES_NOT_OWN_RESOURCE":
                status_code = 400
                message = "USER_DOES_NOT_OWN_RESOURCE"
            case "TAG_NAME_NOT_FOUND":
                status_code = 400
                message = "TAG_NAME_NOT_FOUND"
            case "TAG_IS_EXISTS":
                status_code = 400
                message = "TAG_IS_EXISTS"
            case _:
                status_code = 500
                message = "服务暂时出了点问题"
                logger.error(traceback.format_exc())
        return jsonify({
            "message": message
        }), status_code

@profile
def register_routes(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(comment_bp)

@profile
def register_commands(app: Flask) -> None:
    @app.cli.command(help="create tables")
    @click.option("--drop", is_flag=True, default=True, help="create tables after drop")
    def initdb(drop: bool):
        if drop:
            db.drop_all()
            logger.info("drop all tables")
        db.create_all()
        logger.info("create all tables")
