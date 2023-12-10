from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import db
from .models import *
from .news import get_news
from datetime import datetime

views = Blueprint('views', __name__)

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

@views.before_app_request
def fill_news():
    from .models import News
    news, renewed = get_news(h=0, m=30, s=0)
    if renewed or len(News.query.all()) == 0:
        News.query.delete()
        Comment.query.delete()
        for n in news["data"]:
            d = parse_date(n["published"])
            new_n = News(title=n["title"], link=n["link"], content=n["summary"], published=d)
            db.session.add(new_n)
            db.session.commit()

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user, news=News.query.all())

@views.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def news_page(id):
    if request.method == 'POST': 
        comment = request.form.get('comment')

        if len(comment) < 1:
            flash('Comment is too short!', category='error') 
        else:
            new_comment = Comment(content=comment, date=datetime.now(), news_id=int(id), user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added!', category='success')
    
    return render_template("news.html", user=current_user, news=News.query.get(int(id)))
