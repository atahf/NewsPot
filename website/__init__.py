from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
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
scheduler = BackgroundScheduler(timezone="Europe/Istanbul")

def creat_app():
    app = Flask(__name__)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['RECAPTCHA_SITE_KEY'] = os.environ['RECAPTCHA_SITE_KEY']
    app.config['RECAPTCHA_SECRET_KEY'] = os.environ['RECAPTCHA_SECRET_KEY']

    db.init_app(app)

    logging.basicConfig(filename='newspot.log', level=logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)

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
        with app.app_context():
            news, renewed = get_news(h=1, m=0, s=0)
            if renewed or len(db.session.query(News).all()) == 0:
                count = 0
                for n in news["data"]:
                    oldNews : News = db.session.query(News).filter(News.link == n["link"]).first()
                    if not oldNews:
                        img = n["images"][0] if len(n["images"]) > 0 else None
                        new_n = News(title=n["title"], link=n["link"], content=n["content"], published=parse_date(n["published"]), image_url=img)
                        db.session.add(new_n)
                        db.session.commit()
                        count += 1
                if count > 0:
                    logger.info(f"new added news count is {count}, at {datetime.now()}")
                else:
                    logger.info(f"no new news found, at {datetime.now()}")
    
    with app.app_context():
        db.create_all()
        print("Created Databse!")
        fill_news()

    if not scheduler.running:
        scheduler.add_job(func=fill_news, trigger='cron', minute="*/30", second=0)
        scheduler.start()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html', user=current_user), 404

    @app.after_request
    def after_request(response):
        classification = "safe"
        ip_address = str(request.remote_addr)
        URL = request.url
        body = dict(request.args)

        if "/users/" in URL:
            idx0 = URL.find("/users/")+7
            idx1 = URL.find("/", idx0)
            if idx1 == -1:
                try:
                    if int(URL[idx0:]) != current_user.id:
                        classification = "A4: Insecure direct object references (IDOR)"
                except Exception as e:
                    classification = "A4: Insecure direct object references (IDOR)"
        elif "/admins/comments" in URL:
            classification = "A8: Failure to Restrict URL Access"
        elif "/redirect?url=" in URL:
            if db.session.query(News).filter(News.link == body['url']).count() == 0:
                classification = "A10: Unvalidated Redirects and Forwards"

        log_message = f'User IP: {ip_address}, URL: {URL}, Method: {request.method}, Parameters: {body}, Classification: {classification}'
        logger.info(log_message)

        return response

    return app
