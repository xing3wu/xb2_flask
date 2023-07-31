from flask import Flask
from loguru import logger
from xb2.extensions import db, jwt, migrate
from xb2.settings import config

def create_app(config_name: str) -> "Flask":
    app = Flask("xb2")
    app.config.from_object(config[config_name])

    register_extensions(app)
    logger.info("app init success!")
    return app

def register_extensions(app: Flask) -> None:
    db.init_app(app)
    jwt.init_app(app)

    migrate.init_app(app, db)

    logger.info("app register extensions done")