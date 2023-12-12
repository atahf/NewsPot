from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, News, Comment

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    """
        this endpoint displays all news, which are ordered according to their 
        publish datetime, as the home page
    """
    ordered_news = News.query.order_by(News.published.desc()).all()
    return render_template("home.html", user=current_user, news=ordered_news)

@views.route('/news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def news_page(news_id):
    """
        endpoint displays a specific news by news_id
    """
    if request.method == 'POST':
        comment = request.form.get('comment')
        if len(comment) < 1:
            flash('Comment is too short!', category='error')
        else:
            new_comment = Comment(
                content=comment,
                date=datetime.now(),
                news_id=int(news_id),
                user_id=current_user.id
            )
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added!', category='success')
    return render_template("news.html", user=current_user, news=News.query.get(int(news_id)))

@views.route('/news/<int:news_id>/delete-comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(news_id, comment_id):
    """
        this endpoint tries to delete a comment with given commend_id and reopens 
        the page of specific news with news_id
    """
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
    """
        this endpoint displays list of users if currect user is an admin otherwise 
        redirects to home page '/'
    """
    if current_user.role.isAdmin():
        return render_template("users.html", user=current_user, users=User.query.all())
    return redirect(url_for('views.home'))

@views.route('/redirect')
def redirect_user():
    """
        this endpoint should have 'A10: Unvalidated Redirects and Forwards' 
        or 'CWE-601: Open Redirects' vulnerability
    """
    url = request.args.get('url')
    return redirect(url, code=301) if url else 'No URL provided.'
