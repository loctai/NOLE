from datetime import datetime,date
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash, jsonify
from flask_login import login_required
from . import main
from app import cache, mongo
from functools import wraps
from .forms import withdrawCryptoForm, withdrawCommissionForm
from app.utils import helpers
from bson.objectid import ObjectId

def authy_required(f):
    @wraps(f)
    def  wrap(*args, **kwargs):
        users = mongo.db.Users
        user= users.find_one({'_id': session['user_id'] },{"security":'1','role':'1'})
        # if session.get(u'logged_in') is None:
        print("Session status_2fa", session.get(u'status_2fa'))
        # if user['security']['two_factor_auth']['status'] == 1 and session.get(u'status_2fa') is None:
        #     return redirect("/auth/2fa")
        # else:
        return f(*args, **kwargs)
    return wrap
def LimitWithdrawComm():
    data_invest = mongo.db.Investments.find({'user_id' : session['user_id'] })
    max_ = 0
    for i in data_invest:
        max_ = float(i['amount_usd']) if max_ < float(i['amount_usd']) else max_ 
    return max_
@main.route('/account/dashboard', methods=['GET','POST'])
@login_required
@authy_required
def dashboard():
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    percent = 0
    max_ = LimitWithdrawComm()
    price_trx = helpers.get_tickers(mongo.db.Tickers, "trx")
    price_qtc = helpers.get_tickers(mongo.db.Tickers, "coin")
    price_btc = helpers.get_tickers(mongo.db.Tickers, "btc")
    price_eth = helpers.get_tickers(mongo.db.Tickers, "eth")
    if float(user['balance']['total_invest']) > 0:
        total_max_out = float(user['balance']['total_invest'])*5
        received = float(total_max_out) - float(user['balance']['commission_remain'])
        percent = (float(received)/float(total_max_out))*100
        percent = round(percent, 2)
        total_profit_receive = 0
    print(user['wallet']['coin_reward_date'])
    dt_ = user['wallet']['coin_reward_date']
    date_time = dt_.strftime("%m/%d/%Y %H:%M:%S")
    return render_template('main/pages/dashboard.html', user=user,
            form_withdraw_token = withdrawCryptoForm(),
            form_withdraw_commission = withdrawCommissionForm(),
            percent=percent,
            price_trx=price_trx,
            price_qtc=price_qtc,
            price_btc=price_btc,
            price_eth=price_eth,
            date_time=date_time,
            max_ = max_*2
            )


@main.route('/account/contact-us', methods=['GET','POST'])
@main.route('/account/contact-us/<ids>', methods=['GET','POST'])
@login_required
@authy_required
def contactUs(ids=''):
    print('id', ids)
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data = mongo.db.Supports.find({'user_id' : session['user_id'] })
    data_detail = None
    if ids != "":
        data_detail = mongo.db.Supports.find_one({"_id": ObjectId(ids) })
        if data_detail is not None:
            mongo.db.Supports.update({'_id': data_detail['_id']}, {'$set':{
                'read': 1
            }})
    return render_template('main/pages/contactus.html', 
    user=user, data=data, data_detail=data_detail
            )

@main.route('/account/post-new-contact', methods=['GET','POST'])
@login_required
def PostcontactUs():
    try:
        user = mongo.db.Users.find_one({'_id' : session['user_id'] })
        if request.method == "POST":
            if "subject" in request.form and "msg" in request.form:
                print(request.form)
                if request.form['msg'] != "":
                    id_ = mongo.db.Supports.insert({    
                        "status": 0,
                        "read": 1,
                        "user": user['name'],
                        "user_id": user['_id'],    
                        'subject': request.form['subject'],
                        "content": [
                            {
                                "name": "You",
                                "date": datetime.now(),
                                "msg": request.form['msg']
                            }
                        ],
                        'createdAt': datetime.now()
                    })
                    print(id_)
                    return jsonify({'success': 1}), 200
            else:
                return jsonify({'success': 11}), 400
        else:
            return jsonify({'success': 1}), 400
        return jsonify({'success': 0}), 400
    except Exception as e:
        print(e)
        return jsonify({'success': 1}), 400

@main.route('/account/post-reply-contact', methods=['GET','POST'])
@login_required
def ReplyContacts():
    try:
        user = mongo.db.Users.find_one({'_id' : session['user_id'] })
        if request.method == "POST":
            if "msg" in request.form:
                mongo.db.Supports.update({'_id': ObjectId(request.form['_id'])},{"$set": {
                    "status": 0,
                    "read": 1
                },
                "$push": {
                    "content": {
                        "msg": request.form['msg'],
                        "name":'You',
                        "date": datetime.now(),
                    }
                }})
                return jsonify({'success': 1}), 200
            else:
                return jsonify({'success': 11}), 400
        else:
            return jsonify({'success': 1}), 400
        return jsonify({'success': 0}), 400
    except Exception as e:
        print(e)
        return jsonify({'success': 1}), 400
@main.route('/account/notifications', methods=['GET','POST'])
@login_required
@authy_required
def notifications():
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    return render_template('main/pages/notifications.html', user=user
            )