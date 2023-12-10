from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .models import User
from . import db, recaptcha
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        recaptcha_response = request.form.get('g-recaptcha-response')
        
        if recaptcha_response and recaptcha.verify(recaptcha_response):
            email = request.form.get('email')
            password = request.form.get('password')

            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash("Logged in Successfully!", category="success")
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash("Wrong email or password entered!", category="error")
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
                isAdmin=False,
                first_name=firstName, 
                last_name=lastName, 
                password=generate_password_hash(password1, method="pbkdf2:sha256", salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created!", category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
