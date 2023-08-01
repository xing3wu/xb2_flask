import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@192.168.50.145:5432/xb2_node"
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')


config = {
    'development': DevelopmentConfig,
}