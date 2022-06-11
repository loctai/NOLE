from flask import jsonify, request, url_for, g, abort, current_app, render_template
from app.cronjobs import bp
from app import mongo
from app.utils import helpers
from datetime import datetime,date,timedelta
from app.email import send_email, send_grid_mail
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


@bp.route('/send-mail-profit', methods=['GET'])
def auto_sendmail_profit():    
    data = mongo.db.Mailinvests.find_one({"status":0})
    print(data)
    if data is not None:
        data['amount_coin'] = round(float(data['amount_coin'])/100000000,8)
        data['amount_qtc'] = round(float(data['amount_qtc'])/100000000,8)
        status = send_grid_mail('[NOLE] Notice',
               sender=current_app.config['SENDER'],
               recipients=data['email'],
               text_body=render_template('main/email/mail_profit.txt',
                                         data=data),
               html_body=render_template('main/email/mail_profit.html',
                                         data=data))
        if status == True:
            mongo.db.Mailinvests.update({ "_id" : data['_id'] }, {'$set': {'status': 1 }})
        print('status', status)
    return jsonify({'auto_sendmail_profit':'success'})