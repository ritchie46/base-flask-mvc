from app.project import app, mail
from flask import url_for, render_template
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from threading import Thread


def send_email(subject, recipients, html_body):
    def send_async_email(msg):
        with app.app_context():
            mail.send(msg)

    msg = Message(subject, recipients)
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()


def send_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    confirm_url = url_for(
        'user.confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation'),
        _external=True
    )

    html = render_template('email_confirmation.html', url=confirm_url)

    send_email('Confirm your email address.', [user_email], html)


def send_password_reset_email(user_email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    reset_url = url_for(
        'user.reset_with_token',
        token=serializer.dumps(user_email, salt='password-reset'),
        _external=True
    )

    html = render_template('email_password_reset.html', url=reset_url)
    send_email('Password reset requested', [user_email], html)


def send_token_email(user_email, url_route, html_file, subject, msg, salt):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    url = url_for(
        url_route,
        token=serializer.dumps(msg, salt=salt),
        _external=True
    )
    html = render_template(html_file, url=url)
    send_email(subject, [user_email], html)