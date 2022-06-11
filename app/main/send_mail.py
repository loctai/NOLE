from flask import jsonify, request, url_for, g, abort, current_app, render_template
from app.cronjobs import bp
from app import mongo
from app.utils import helpers
from datetime import datetime,date,timedelta
from app.email import send_email, send_grid_mail
def send_mail_otp(data, type_otp="withdraw"):    
    if data is not None:
        txt_ = "Use the following code to confirm withdraw:"
        if type_otp == "update_email":
            txt_ = "Use the following code to confirm change email:"
        if type_otp == "update_address":
            txt_ = "Use the following code to confirm update wallet:"
        status = send_grid_mail('[NOLE] Verification code',
               sender=current_app.config['SENDER'],
               recipients=data['email'],
               text_body=render_template('main/email/mail_otp.txt',
                                         data=data,
                                         txt = txt_),
               html_body=render_template('main/email/mail_otp.html',
                                         data=data,
                                         txt = txt_))
    return True