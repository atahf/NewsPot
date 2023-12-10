from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import *
from datetime import datetime

views = Blueprint('views', __name__)

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
