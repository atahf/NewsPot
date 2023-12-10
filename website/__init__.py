from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_recaptcha import ReCaptcha
import logging
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

    logging.basicConfig(filename='newspot.log', level=logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)

    @app.after_request
    def after_request(response):
        client_ip = request.remote_addr
        request_url = request.url
        request_method = request.method
        request_params = request.args if request.method == 'GET' else request.form

        log_message = f'Client IP: {client_ip}, URL: {request_url}, Method: {request_method}, Parameters: {request_params}'
        logger.info(log_message)

        return response

    return app
