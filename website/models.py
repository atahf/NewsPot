from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import ForeignKey
from datetime import datetime, timedelta

def three_minutes_from_now():
    return datetime.utcnow() + timedelta(minutes=3)

def lazy_datetime_picker():
    return datetime.utcnow()

class Base(DeclarativeBase):
    pass

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(1023), nullable=False)
    title = db.Column(db.String(4095), nullable=False)
    content = db.Column(db.String(131071), nullable=False)
    published = db.Column(db.DateTime(timezone=True), default=func.now())
    image_url = db.Column(db.String(1023), nullable=True)
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
    registration_date = db.Column(db.DateTime(timezone=True), nullable=False)
    failed_attempt = db.Column(db.Integer, default=0)
    last_failed_attempt = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    login_timeout = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    comments = db.relationship('Comment')
    reset_tokens = db.relationship('PasswordResetToken')

    def __str__(self):
        return f"{self.first_name[0].upper()}{'*' * (len(self.first_name)-1)} {self.last_name[0].upper()}{'*' * (len(self.last_name)-1)}"
    
class PasswordResetToken(db.Model):
    
    
    uuid = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    is_confirmed= db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.DateTime(timezone=True), nullable=True, default=three_minutes_from_now)
    six_digit= db.Column(db.String(255), nullable=False)
    remaining_rights = db.Column(db.Integer, default=3)
    created_at =  db.Column(db.DateTime(timezone=True), nullable=True, default=lazy_datetime_picker)
    
    def getUser(self):
        return User.query.filter_by(id=self.user_id).first()
    
    
    
