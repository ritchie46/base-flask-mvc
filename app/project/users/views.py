from flask import Blueprint, request, flash, render_template, redirect, url_for, abort
from project.users.forms import RegisterForm, LoginForm, EmailForm, PasswordForm
from project.models import User
from project import db, app
from itsdangerous import URLSafeTimedSerializer, BadData
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from mailing import send_confirmation_email, send_password_reset_email, send_token_email

bp = Blueprint("user", __name__)


@bp.route('/')
def landing():
    return render_template('landing.html')


@bp.route('/home')
@login_required
def home():
    return render_template('home.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(form.email.data, form.password.data)
                db.session.add(new_user)
                db.session.commit()
                send_confirmation_email(new_user.email)
                flash("Thanks for registering! Please check your email to activate your account.", 'success')
                return redirect(url_for('main.home'))
            except IntegrityError:
                db.session.rollback()
                flash(f'Error, Email {form.email.data} is already registered.', 'error')
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            # sqlalchemy query
            user = User.query.filter_by(email=form.email.data).first()

            if user is not None and not user.email_confirmed:
                flash('Please confirm your email first.', 'error')

            elif user is not None and user.is_correct_password(form.password.data):
                user.authenticated = True
                user.last_logged_in = user.current_logged_in
                user.current_logged_in = datetime.now()

                db.session.add(user)
                db.session.commit()
                login_user(user)
                # current_user is a proxy to the current user's object from the User class
                flash(f"Hi {current_user.email}.", 'success')
                return redirect(url_for('user.home'))
            else:
                flash('Error, incorrect login credentials.', 'error')
    return render_template('form_login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash("You're logged out.", 'info')
    return redirect(url_for('user.login'))


@bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation', max_age=3600)
    except BadData:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('user.register'))

    # When email is changed the token is actually a list with [old_email, new_email].
    if type(email) is list:
        new_email = email[1]
        email = email[0]
    else:
        new_email = False

    user = User.query.filter_by(email=email).first()
    if user is not None:
        if user.email_confirmed:
            if not new_email:
                flash('Account is already confirmed. Please login', 'info')
                return redirect(url_for('user.login'))
            else:
                user.email = new_email
        else:
            user.registration_date = datetime.now()

        user.email_confirmed = True
        user.email_confirmation_date = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('Thank you for confirming your email address!', 'success')
        return redirect(url_for('user.home'))
    return redirect(url_for('user.login'))


@bp.route('/reset', methods=['GET', 'POST'])
def reset():
    form = EmailForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            user = User.query.filter_by(email=form.email.data).first()

            if user is None:
                flash('Invalid email adress!', 'error')
                return render_template('form_password_reset.html', form=form)

            if user.email_confirmed:
                send_password_reset_email(user.email)
                flash('Please check your email for a password reset link.', 'success')
            else:
                flash('Your email address must be confirmed before attempting a password reset.', 'error')
            return redirect(url_for('user.login'))

    return render_template('form_password_reset.html', form=form)


@bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except BadData:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('user.reset'))

    form = PasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()

            if user is None:
                flash("Invalid email address!", 'error')
                return redirect(url_for('user.login'))

            user.password_ = form.password.data
            db.session.add(user)
            db.session.commit()
            flash("Your password has been updated!", 'success')
            return redirect(url_for('user.login'))

    return render_template('form_reset_password_with_token.html', form=form, token=token)


@bp.route('/user_profile')
@login_required
def user_profile():
    return render_template('user_profile.html')


@bp.route('/email_change', methods=['GET', 'POST'])
@login_required
def user_email_change():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            email_exists = User.query.filter_by(email=form.email.data).first()
            if email_exists is None:
                user = current_user

                new_email = form.email.data
                send_token_email(new_email,
                                 'user.confirm_email',
                                 'email_confirmation.html',
                                 'Confirm your email address.',
                                 [user.email, new_email],
                                 'email-confirmation')
                flash('A verification email is sent to your new email address. Please verify this new address.',
                      'success')
                return redirect(url_for('user.user_profile'))

            else:
                flash('Sorry, that email is already registered.', 'error')

    return render_template('form_change_email.html', form=form)


@bp.route('/password_change', methods=['GET', 'POST'])
@login_required
def user_password_change():
    form = PasswordForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = current_user

            if not user.is_correct_password(form.old_password.data):
                flash('Sorry, your current password is incorrect', 'error')
                return redirect(url_for('user.user_password_change'))

            user.password_ = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Password had been updated!', 'success')
    return render_template('form_password_change.html', form=form)


@bp.route('/admin_view_users')
@login_required
def admin_view_users():
    if current_user.role != 'admin':
        abort(403)
    else:
        n_rows = User.query.count()
        limit = min(n_rows, 50)
        users = User.query.order_by(User.id).limit(limit).all()
        return render_template('view_users.html', users=users)


