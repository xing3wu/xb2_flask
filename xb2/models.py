from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from xb2.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    posts = relationship('Post', back_populates='user')
    
    def own_post(self, post_id: int):
        return any(p.id == post_id for p in self.posts)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    userId = Column(Integer, ForeignKey('user.id'))
    user = db.relationship('User', back_populates='posts')

class File(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    originalname = Column(String(255), nullable=False)
    mimetype = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    width = Column(Integer,nullable=True)
    height = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    postId = Column(Integer, ForeignKey('post.id'))
    userId = Column(Integer, ForeignKey('user.id'))

class Tag(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
