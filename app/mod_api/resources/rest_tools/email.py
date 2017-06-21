from itsdangerous import URLSafeTimedSerializer
from flask.ext.mail import Message

from app import app, mail, templates
from app.mod_api import models

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        return -1
    user = User.query.filter_by(email=email).first()
    if user.confirmed:
        return 0
    else:
        user.confirm()
        return 1

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=templates.email_activation.html,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

