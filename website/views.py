from flask import Blueprint, render_template, request, flash, redirect, url_for
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
    news, renewed = get_news(h=3, m=0, s=0)
    if renewed or len(News.query.all()) == 0:
        News.query.delete()
        Comment.query.delete()
        for n in news["data"]:
            d = parse_date(n["published"])
            new_n = News(title=n["title"], link=n["link"], content=n["content"], published=d)
            db.session.add(new_n)
            db.session.commit()

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user, news=News.query.order_by(News.published.desc()).all())

@views.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def news_page(id):
    if request.method == 'POST': 
        comment = request.form.get('comment')
        if len(comment) < 1:
            flash('Comment is too short!', category='error') 
        else:
            new_comment = Comment(content=comment, date=datetime.now(), news_id=int(id), user_id=current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added!', category='success')
    
    return render_template("news.html", user=current_user, news=News.query.get(int(id)))

@views.route('/news/<int:news_id>/delete-comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(news_id, comment_id):
    if current_user.role.isAdmin():
        comment = Comment.query.get(int(comment_id))
        if comment:
            db.session.delete(comment)
            db.session.commit()
            flash("Comment Removed", category="success")
        else:
            flash("Comment Does not exists!", category="success")
    else:
        flash("Not Authorized to remove!")
    return redirect(url_for("views.news_page", id=int(news_id)))

@views.route('/users')
@login_required
def users():
    if current_user.role.isAdmin():
        return render_template("users.html", user=current_user, users=User.query.all())
    else:
        return redirect(url_for('views.home'))

# A10: Unvalidated Redirects and Forwards
@views.route('/redirect')
def redirect_user():
    url = request.args.get('url')
    return redirect(url) if url else 'No URL provided.'
