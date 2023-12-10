from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_recaptcha import ReCaptcha
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
DB_NAME = "database.db"
recaptcha = ReCaptcha()

def creat_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['RECAPTCHA_SITE_KEY'] = os.environ['RECAPTCHA_SITE_KEY']
    app.config['RECAPTCHA_SECRET_KEY'] = os.environ['RECAPTCHA_SECRET_KEY']

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, News, Comment
    
    with app.app_context():
        db.create_all()
        print("Created Databse!")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
