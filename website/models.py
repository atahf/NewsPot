from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from enum import Enum

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(1023), nullable=False)
    title = db.Column(db.String(4095), nullable=False)
    content = db.Column(db.String(131071), nullable=False)
    published = db.Column(db.DateTime(timezone=True), default=func.now())
    comments = db.relationship('Comment')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2047), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    news_id = db.Column(db.Integer, db.ForeignKey('news.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    def getUser(self):
        return User.query.filter_by(id=self.user_id).first()

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

    def isAdmin(self):
        return self.name == UserRole.ADMIN.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    comments = db.relationship('Comment')

    def __str__(self):
        return f"{self.first_name[0].upper()}{'*' * (len(self.first_name)-1)} {self.last_name[0].upper()}{'*' * (len(self.last_name)-1)}"
