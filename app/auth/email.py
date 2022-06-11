from flask import render_template, current_app
import jwt
from time import time
from app import mongo
from app.email import send_email, send_grid_mail

def get_reset_password_token(id, expires_in=600):
    return jwt.encode(
        {'reset_password': id, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

def verify_reset_password_token(token):
    users = mongo.db.Users
    try:
        id = jwt.decode(token, current_app.config['SECRET_KEY'],
                        algorithms=['HS256'])['reset_password']
    except:
        return
    return users.find_one({'_id': id})

def send_password_reset_email(user):
    token = get_reset_password_token(user['_id'], 3600)
    print(token)
    send_grid_mail('[NOLE] Reset Your Password',
               sender=current_app.config['SENDER'],
               recipients=user['email'],
               text_body=render_template('auth/email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/reset_password.html',
                                         user=user, token=token))
    # send_email('[NOLE] Reset Your Password',
    #            sender=current_app.config['SENDER'],
    #            recipients=user['email'],
    #            text_body=render_template('auth/email/reset_password.txt',
    #                                      user=user, token=token),
    #            html_body=render_template('auth/email/reset_password.html',
    #                                      user=user, token=token))

def send_confirm_email(user):
    token = get_reset_password_token(user['_id'], 86400)
    print(token)
    send_grid_mail('[NOLE] Confirm Your Account',
               sender=current_app.config['SENDER'],
               recipients=user['email'],
               text_body=render_template('auth/email/confirm.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/confirm.html',
                                         user=user, token=token))