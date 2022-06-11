from datetime import datetime,date
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash 
from flask_login import login_required
from . import main
from app import cache, mongo

@main.route('/account/transactions', methods=['GET','POST'])
@login_required
def transaction():
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data = mongo.db.Transactions.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    daily_profit = []
    binary_bonus = []
    i_commission = []
    f_commission = []
    for item in data:
        if item['wallet'] == "Daily Profit":
            daily_profit.append(item)
        if item['wallet'] == "Binary Bonus":
            binary_bonus.append(item)
        if item['wallet'] == "I Commission":
            i_commission.append(item)
        if item['wallet'] == "F Commission":
            f_commission.append(item)
    transaction = {
        "daily_profit": daily_profit,
        "binary_bonus": binary_bonus,
        "i_commission": i_commission,
        "f_commission": f_commission
    }
    return render_template('main/pages/transaction.html', user=user, transaction=transaction)

@main.route('/account/arbitrage', methods=['GET','POST'])
@login_required
def arbitrage():
    return redirect("/account/dashboard")
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    return render_template('main/pages/arbitrage.html', user=user)