from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from . import db
from .models import User, News, Comment, PasswordResetToken
import uuid
import random
from .utils import send_mail
from werkzeug.security import generate_password_hash

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    """
        this endpoint displays all news, which are ordered according to their 
        publish datetime, as the home page
    """
    ordered_news = News.query.order_by(News.published.desc()).all()

    query = request.args.get('query')
    page_numS = request.args.get('page')
    
    if query and query.strip() != "":
        res = []
        for n in ordered_news:
            if query in n.title.lower() or query in n.content.lower():
                res.append(n)
    else:
        res = ordered_news
    count = len(res)
    maxPage = count // 10
    if count % 10 > 0:
        maxPage += 1

    try:
        if not page_numS:
            page_num = 1
        else:
            page_num = int(page_numS)

            if page_num <= 0 or page_num > maxPage:
                raise Exception("Invalid page number!")
    except Exception as e:
        flash("Invalid page number!", category="error")
        page_num = 1

    idx = 10 * page_num
    if idx > count:
        return render_template("home.html", user=current_user, news=res[idx-10:], searchQ=query, sLen=count, page=page_num, maxPage=maxPage)
    return render_template("home.html", user=current_user, news=res[idx-10:idx], searchQ=query, sLen=count, page=page_num, maxPage=maxPage)

@views.route('/news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def news_page(news_id):
    """
        endpoint displays a specific news by news_id
    """
    news = News.query.get(int(news_id))
    if not news:
        flash('Page not found!', category='error')
        return redirect(url_for("views.home"))
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
    return render_template("news.html", user=current_user, news=news)

@views.route('/news/<int:news_id>/delete-comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(news_id, comment_id):
    """
        this endpoint tries to delete a comment with given commend_id
    """
    comment = Comment.query.get(int(comment_id))
    if not comment:
        flash("Comment Does not exists!", category="success")
        return redirect(url_for("views.comments"))
    
    db.session.delete(comment)
    db.session.commit()
    flash("Comment Removed", category="success")
    return redirect(url_for("views.comments"))

@views.route('/admins/users')
@login_required
def users():
    """
        this endpoint displays list of users if currect user is an admin otherwise 
        redirects to home page '/'
    """
    if current_user.role.isAdmin():
        return render_template("users.html", user=current_user, users=User.query.all())
    return redirect(url_for('views.home'))

@views.route('/admins/add-user')
@login_required
def add_user():
    if current_user.role.isAdmin():
        return render_template("add_user.html", user=current_user, users=User.query.all())
    return redirect(url_for('views.home'))

@views.route('/admins/comments')
@login_required
def comments():
    """
        this endpoint should have 'A8: Failure to Restrict URL Access'
    """
    return render_template("comments.html", user=current_user, comments=Comment.query.all())

@views.route('/redirect')
def redirect_user():
    """
        this endpoint should have 'A10: Unvalidated Redirects and Forwards' 
        or 'CWE-601: Open Redirects' vulnerability
    """
    url = request.args.get('url')
    if url.startswith('http://') or url.startswith('https://'):
        return redirect(url)
    else:
        return send_file(url, as_attachment=False)


@views.route("/passwordReset", methods=['GET', 'POST'])
def password_reset():
    
    if request.method == "POST":
        email = request.form.get("email")
        user : User = db.session.query(User).filter(User.email == email).first()
        
        if not user:
            flash("There is no such account!", category="error")
            return redirect(url_for('auth.login'))
        
        instances = db.session.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id, PasswordResetToken.created_at > datetime.utcnow() - timedelta(hours=1) ).all()
        if len(instances) > 0:
            flash("Yo can only try to reset your password once a hour!", category="error")
            return redirect(url_for('auth.login'))
        
        new_token = PasswordResetToken(user_id = user.id, uuid = str(uuid.uuid4()), is_confirmed = False, six_digit = str(random.randint(100000,999999)))
        send_mail(recipient=user.email, uuid=new_token.uuid, name=user.first_name, six_digit=new_token.six_digit)
        db.session.add(new_token)
        db.session.commit()
        
        flash("Instructions are sent to your email!", category="info")
        return redirect(url_for('auth.login'))
    
    return render_template("password_reset.html", user=current_user)
    
@views.route("passwordReset/<string:uuid>", methods=["GET", "POST"])
def password_reset_confirm(uuid):
    instance : PasswordResetToken = db.session.query(PasswordResetToken).filter(PasswordResetToken.uuid == str(uuid)).first()
    if request.method == "POST":
        if not instance:
            flash("Token could not be found!", category="error")
            return redirect(url_for('auth.login'))
        
        if instance.is_confirmed:
            flash("This token already issued!", category="error")
            return redirect(url_for('auth.login'))
        
        if instance.expiry_date < datetime.utcnow():
            flash("This token is expired!", category="error")
            return redirect(url_for('auth.login'))
        
        if instance.remaining_rights <= 0:
            flash("No rights left!", category="error")
            return redirect(url_for('auth.login'))
        
        user = instance.getUser()
        if not user:
            flash("The user could not be found!")
            return redirect(url_for('auth.login'))
            
        if instance.six_digit != request.form.get("six_digit"):
            instance.remaining_rights -= 1
            db.session.commit()
            flash("The 6 digit code is incorrect", category="error")
            return redirect(request.url)
        
        if str(request.form.get("new_password")) != str(request.form.get("new_password_again")):
            flash("The passwords are not matching!", category="error")
            return redirect(request.url)
            
        instance.is_confirmed = True
        user.password = generate_password_hash(str(request.form.get("new_password")), method="pbkdf2:sha256", salt_length=16)
        db.session.commit()
        flash("Password change succeed!", category="info")
        return redirect(url_for('auth.login'))
        
    return render_template("password_reset_confirm.html", user=current_user)
            
@views.route("/users/<int:userId>")
@login_required
def getUser(userId):
    userData : User = db.session.query(User).filter(User.id == userId).first()
    if not userData:
        flash("User does not exist!", category="error")
        return redirect(url_for("views.home"))
    
    userName = userData.first_name.capitalize() + " " + userData.last_name.capitalize()

    comments : Comment = db.session.query(Comment).filter(Comment.user_id == userId)
    return render_template("user_profile.html", user=current_user, userId=userId, userName=userName, comments=comments, count=comments.count())
        
@views.route("/users/<int:userId>/my-details")
@login_required
def getMyUserDetails(userId):
    if userId != current_user.id:
        flash("Unathorized Access!", category="error")
        return redirect(url_for("views.home"))

    userData : User = db.session.query(User).filter(User.id == userId).first()
    if not userData:
        flash("User does not exist!", category="error")
        return redirect(url_for("views.home"))
    
    return render_template("user_details.html", user=current_user, userData=userData)
