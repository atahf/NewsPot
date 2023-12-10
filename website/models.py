from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(1000))
    title = db.Column(db.String(5000))
    content = db.Column(db.String(100000))
    published = db.Column(db.DateTime(timezone=True), default=func.now())
    comments = db.relationship('Comment')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    isAdmin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    comments = db.relationship('Comment')
