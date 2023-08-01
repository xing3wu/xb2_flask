from flask import Flask
import click
from loguru import logger
from xb2.extensions import db, jwt, migrate
from xb2.settings import config

def create_app(config_name: str) -> "Flask":
    app = Flask("xb2")
    app.config.from_object(config[config_name])

    register_extensions(app)
    logger.info("create app success!")
    return app

def register_extensions(app: Flask) -> None:
    db.init_app(app)
    jwt.init_app(app)

    migrate.init_app(app, db)
    logger.info("app register extensions done")


def register_commands(app: Flask) -> None:
    @app.cli.command(help="create tables")
    @click.option("--drop", is_flag=True, default=True, help="create tables after drop")
    def initdb(drop: bool):
        if drop:
            db.drop_all()
            logger.info("drop all tables")
        db.create_all()
        logger.info("create all tables")
