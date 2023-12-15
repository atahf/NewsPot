from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_recaptcha import ReCaptcha
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

db = SQLAlchemy()
DB_NAME = "database.db"
recaptcha = ReCaptcha()
scheduler = BackgroundScheduler()

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
    from .news import get_news

    def parse_date(date_str):
        try:
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',  # Format 1: "Fri, 08 Dec 2023 13:52:54 +0000"
                '%a, %d %b %Y %H:%M:%S %Z'   # Format 2: "Sun, 10 Dec 2023 08:55:50 GMT"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    pass
            raise ValueError("Date string does not match expected formats.")
        except Exception as e:
            print("Error: ", e)
            return None

    def fill_news():
        news, renewed = get_news(h=0, m=59, s=0)
        if renewed or len(db.session.query(News).all()) == 0:
            News.query.delete()
            Comment.query.delete()
            for n in news["data"]:
                new_n = News(title=n["title"], link=n["link"], content=n["content"], published=parse_date(n["published"]))
                db.session.add(new_n)
                db.session.commit()
    scheduler.add_job(func=fill_news, trigger='cron', hour='*', minute='0', second='0')
    
    with app.app_context():
        db.create_all()
        print("Created Databse!")
        fill_news()
        scheduler.start()

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
