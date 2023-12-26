from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .models import User, UserRole
from . import db, recaptcha
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

MAX_ATTEMPTS = 3
TIMEOUT_DURATION = 5
INCREMENT_FACTOR = 2

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        recaptcha_response = request.form.get('g-recaptcha-response')
        if recaptcha_response and recaptcha.verify(recaptcha_response):
            email = request.form.get('email')
            password = request.form.get('password')

            user = User.query.filter_by(email=email).first()
            if user:
                if user.login_timeout and user.login_timeout > datetime.now():
                    remaining_time = user.login_timeout - datetime.now()
                    flash(f"Please try again in {remaining_time.seconds // 60} minutes.", category="error")
                    return render_template("login.html", user=current_user)

                if check_password_hash(user.password, password):
                    user.failed_attempt = 0
                    user.login_timeout = None
                    db.session.commit()

                    flash("Logged in Successfully!", category="success")
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    user.last_failed_attempt = datetime.now()
                    user.failed_attempt += 1
                    if user.failed_attempt >= MAX_ATTEMPTS:
                        timeout_duration = TIMEOUT_DURATION * (INCREMENT_FACTOR ** (user.failed_attempt - MAX_ATTEMPTS))
                        user.login_timeout = datetime.now() + timedelta(minutes=timeout_duration)
                        flash(f"Too many failed attempts. Try again in {timeout_duration} minutes.", category="error")
                    else:
                        flash("Wrong email or password entered!", category="error")

                    db.session.commit()
            else:
                flash("Wrong email or password entered!", category="error")
        else:
            flash("Captcha failed!", category="error")
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        recaptcha_response = request.form.get('g-recaptcha-response')

        if user:
            flash("Email in use!", category='error')
        elif len(email) < 4:
            flash("Email is short!", category='error')
        elif len(firstName) < 2:
            flash("First name is short!", category='error')
        elif len(lastName) < 2:
            flash("Last name is short!", category='error')
        elif password1 != password2:
            flash("passwords are not same!", category='error')
        elif len(password1) < 7:
            flash("password is short!", category='error')
        elif not recaptcha_response or not recaptcha.verify(recaptcha_response):
            flash("Captcha failed!", category='error')
        else:
            new_user = User(
                email=email,
                first_name=firstName, 
                last_name=lastName,
                registration_date=datetime.now(),
                password=generate_password_hash(password1, method="pbkdf2:sha256", salt_length=16)
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created!", category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/admin/add-user', methods=['POST'])
@login_required
def admin_add_user():
    if current_user.role.isAdmin():
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        userRole = UserRole.ADMIN if request.form.get('isAdmin') else UserRole.USER

        user = User.query.filter_by(email=email).first()
        recaptcha_response = request.form.get('g-recaptcha-response')

        if user:
            flash("Email in use!", category='error')
        elif len(email) < 4:
            flash("Email is short!", category='error')
        elif len(firstName) < 2:
            flash("First name is short!", category='error')
        elif len(lastName) < 2:
            flash("Last name is short!", category='error')
        elif password1 != password2:
            flash("passwords are not same!", category='error')
        elif len(password1) < 7:
            flash("password is short!", category='error')
        elif not recaptcha_response or not recaptcha.verify(recaptcha_response):
            flash("Captcha failed!", category='error')
        else:
            new_user = User(
                email=email,
                first_name=firstName, 
                last_name=lastName, 
                password=generate_password_hash(password1, method="pbkdf2:sha256", salt_length=8),
                role=userRole
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created!", category='success')
            return redirect(url_for('views.users'))
    else:
        return redirect(url_for("views.home"))

@auth.route('/admin/remove-user/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_remove_user(id):
    
    if not current_user.role.isAdmin():
        return redirect(url_for("views.home"))
    
    user = User.query.get(int(id))
    
    if not user:
        flash("User does not Exist!", category="error")
        return redirect(url_for("views.users"))
        
    if user.id == current_user.id:
        flash("Cannot Remove Yourself!", category="error")
        return redirect(url_for("views.users"))
    
    db.session.delete(user)
    db.session.commit()
    flash("Removed User!", category="success")
    return redirect(url_for("views.users"))
    
