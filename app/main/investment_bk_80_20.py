from datetime import datetime,date,timedelta  
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash, jsonify
from flask_login import login_required
from . import main
from app import cache, mongo, ClientCoinpayment
from .forms import InvestForm
from app.utils import helpers
from app.tasks import celery
import time

def amount_fee(amount):
    fee = 1
    return fee
    # if amount == 200: 
    #     fee = 5
    # elif amount == 500: 
    #     fee = 5
    # elif amount == 1000: 
    #     fee = 10
    # elif amount == 3000: 
    #     fee = 30
    # elif amount == 5000: 
    #     fee = 50
    # elif amount == 10000: 
    #     fee = 100
    # else: 
    #     fee = 0
    # return fee

@main.route('/account/investment/create-invoice', methods=['GET', 'POST'])
@login_required
def investInvoice():
    try:
        form = InvestForm()
        user = mongo.db.Users.find_one({'_id' : session['user_id'] })
        print(user['wallet'])
        if form.validate_on_submit():
            payment = request.form['payment']
            if payment =="ETH":
                return jsonify({
                    "success": 0,
                    "msg": "Coming Soon"
                })
            amount = request.form['amount']
            
            currency = request.form['payment']
            price = helpers.get_tickers(mongo.db.Tickers, payment.lower())
            usd_fee = float(amount)*0.01
            amount_coin_fee =round(usd_fee/float(price), 8)
            amount_coin_invest = round(float(amount)/float(price),8)
            # total_coin_amount = float(amount_coin_fee) + float(amount_coin_invest)
            # print(amount_coin_fee, amount_coin_invest)
            total_coin_amount = float(amount_coin_invest)
            fee_add = amount_fee(float(amount))
            # print(fee_add)
            amount_coin_fee_add = float(fee_add)/float(price)
            total_coin_amount_send = float(total_coin_amount)+float(amount_coin_fee_add)
            # total_coin_amount = 0.005
            if payment == "QTC":
                crypto_address = user['wallet']['qtc_address']
                address = user['wallet']['qtc_address']
            elif payment =="BTC":
                crypto_address = user['wallet']['btc_address']
                address = user['wallet']['BTC']['address']
            elif payment =="ETH":
                crypto_address = user['wallet']['eth_address']
                address = user['wallet']['ETH']['address']
            elif payment =="TRX":
                total_coin_amount = round(total_coin_amount, 0)
                amount_coin_invest = total_coin_amount
                crypto_address = user['wallet']['trx_address']
                address = user['wallet']['TRX']['address']
            elif payment =="USDT":
                crypto_address = user['wallet']['usdt_address']
                payment = "USDT.ERC20"
                address = user['wallet']['USDT']['address']
            ipn_url = 'http://192.254.73.26:5889/account/callback-invoiceaksjdfo134ADkweruhasdf'
            if crypto_address == "":
                return jsonify({
                    "success": 0,
                    "msg": "Error! Please update your %s address"  % (payment)
                })
            if user['wallet']['coin_address'] == "":
                return jsonify({
                    "success": 0,
                    "msg": "Error! Please update your Nole address"
                })
            # print('======================')
            # print(address)
            # print('======================')
            if address == "":
                wallet_update = 'wallet.'+currency+'.address' if currency != 'USDT.ERC20' else 'wallet.USDT.address'
                # print(wallet_update)
                if currency == "QTC":
                    result = web3_api.create_new_wallet_via_web3()
                    address = result['address']
                    key =result['key']
                    mongo.db.Users.update({'_id' : session['user_id'] },{'$set' : {
                        'wallet.qtc_address' : address, 
                        'wallet.qtc_private_key': key,
                        'wallet.QTC.address': address,
                        'wallet.QTC.private_key': key
                    }})
                else:
                    respon_wallet_btc = ClientCoinpayment.get_callback_address(currency=payment, ipn_url=ipn_url)
                    if respon_wallet_btc['error'] == 'ok':
                        address =  respon_wallet_btc['result']['address']
                        mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { 
                            wallet_update : address
                        } })
                    else:
                        address = ''
            if address != "":
        # Invoice =  ClientCoinpayment.create_transaction(amount=1, currency1='USDT.ERC20', currency2='USDT.ERC20', buyer_email='noleai@gmail.com', ipn_url=ipn_url)
        # Invoice =  ClientCoinpayment.create_transaction(amount=total_coin_amount, currency1=payment, currency2=payment, buyer_email='noleai@gmail.com', ipn_url=ipn_url)
        # print(Invoice)
        # Invoice = {'error': 'ok', 'result': {'amount': '0.04829857', 'txn_id': 'CPED1H5KTBE5ZXIHFFDIFQ4TZU', 'address': '3H6uNKrUbHDgTG2DRbyCGVxpmw9cP6L4A2', 'confirms_needed': '2', 'timeout': 27000, 'checkout_url': 'https://www.coinpayments.net/index.php?cmd=checkout&id=CPED1H5KTBE5ZXIHFFDIFQ4TZU&key=56c6625cdc141ac59991116c57281f81', 'status_url': 'https://www.coinpayments.net/index.php?cmd=status&id=CPED1H5KTBE5ZXIHFFDIFQ4TZU&key=56c6625cdc141ac59991116c57281f81', 'qrcode_url': 'https://www.coinpayments.net/qrgen.php?id=CPED1H5KTBE5ZXIHFFDIFQ4TZU&key=56c6625cdc141ac59991116c57281f81'}}
                _id = helpers.getNextSequence(mongo.db.Counters,"invoiceId")
                transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                total_coin_amount_satoshi = float(total_coin_amount)*100000000                
                checkInvoice = mongo.db.Invoices.find_one(
                    {'$and' : [{"user_id": user['_id'], "currency": request.form['payment'], "received": 0, "status": 0}]}
                )
                if checkInvoice is None:
                    invoice_id = mongo.db.Invoices.insert({
                        '_id': _id,
                        'transaction_id': transaction_id,
                        'amount_usd': amount,
                        'user_id' : user['_id'],
                        'status': 0,
                        'txn_id': "",
                        "id_deposit": "",
                        'received': 0,
                        "address": address,
                        "total_coin_amount": round(total_coin_amount_satoshi, 0),
                        'amount_coin_invest': str(amount_coin_invest),
                        'amount_coin_fee': str(amount_coin_fee),
                        'currency': request.form['payment'],
                        'createdAt': datetime.now(),
                        "check": 0
                    })
                else:
                    mongo.db.Invoices.update({'_id': checkInvoice['_id']}, {'$set':{
                        'amount_usd': amount,
                        'user_id' : user['_id'],
                        'status': 0,
                        'txn_id': "",
                        'received': 0,
                        "address": address,
                        "total_coin_amount": round(total_coin_amount_satoshi, 0),
                        'amount_coin_invest': str(amount_coin_invest),
                        'amount_coin_fee': str(amount_coin_fee),
                        'currency': request.form['payment'],
                        'createdAt': datetime.now(),
                    }})
                return jsonify({
                    "success": 1,
                    "address": address,
                    # "amount": round(total_coin_amount, 8),
                    "amount":round(total_coin_amount_send, 0),
                    "amount_usd": amount,
                    "currency": currency
                })
            else:
                return jsonify({
                    "success": 0,
                    "msg": "Error! Please try again"
                })
        else:
            return jsonify({
                "success": 0,
                "msg": "Error! Please try again"
            })
    except Exception as e:
        print(e)
        return jsonify({"success": 0})

@main.route('/account/auto-check', methods=['GET', 'POST'])
def autoCheck():
    data = mongo.db.Invoices.find({'$and' : [{'id_deposit': {"$ne": ""}, "check": 0, "status": 2 }]})
    for item in data:
        data_invoice = {
            "id_deposit": item['id_deposit'],
            "received": item['received'],
            "amount_coin_invest": item['amount_coin_invest'],
            "total_coin_amount": item['total_coin_amount']
        }
        amount_coin_invest = float(item['amount_coin_invest'])*2 - 10
        if(amount_coin_invest > float(item['received'])):
            amount_satoshi_received = float(item['received'])*100000000
            mongo.db.Investments.update( {'_id':item['id_deposit']},{
                "$set": {'amount_coin_satoshi': amount_satoshi_received}
            })
        mongo.db.Invoices.update( {'_id':item['_id']},{
                "$set": {'check': 1}
        })
    return jsonify({"success": 0})

@main.route('/account/investment/check-status/<currency>', methods=['GET', 'POST'])
@login_required
def CheckStatus(currency):
    data = mongo.db.Invoices.find_one({'$and' : [{'currency': currency, "user_id": session['user_id'], "status": 0 }]},sort=[("_id", -1)])
    print(data['createdAt'])
    price_trx = helpers.get_tickers(mongo.db.Tickers, 'trx')
    date_invoice = data['createdAt'] + timedelta(minutes=45)
    date_now = datetime.now()
    print(date_invoice, date_now)
    amount_coin_fee_add = 1/float(price_trx)
    amount_send = float(data['amount_coin_invest'])+float(amount_coin_fee_add)
    if date_now > date_invoice:
        new_coin = round(float(data['amount_usd'])/float(price_trx), 0)
        amount_satoshi = float(new_coin)*100000000
        mongo.db.Invoices.update({'_id': data['_id']}, {'$set':{
            'total_coin_amount': amount_satoshi,
            'amount_coin_invest': new_coin,
            'createdAt': datetime.now()
        }})
        amount_send = new_coin+float(amount_coin_fee_add)
    if data is None:
        return jsonify({"success": 1,"amount_send": amount_send})
    else:
        return jsonify({"success": 0, "amount_send": round(amount_send, 0)})
@main.route('/account/callback-invoiceaksjdfo134ADkweruhasdf', methods=['GET','POST'])
def callbackCoinpaymentInvoice():
    print('request')
    if request.method == 'POST':
        print(request.form)
        tx = request.form['txn_id']
        address = request.form['address']
        amount = float(request.form['amount'])
        currency = request.form['currency']
        received_confirms = request.form['confirms']
        if currency == 'USDT.ERC20':
            currency = 'USDT'
        checkInvoice = mongo.db.Invoices.find_one({'$and' : [{'currency': currency, 'address': address, "status": {'$ne': 2} }]},sort=[("_id", -1)])
        checkTx = mongo.db.Invoices.find_one({"txn_id": tx})
        if checkInvoice is not None and checkTx is None:
            msg = {'txn_id':tx, "address": address, 'received_confirms':received_confirms, 'amount1':amount, 'currency1':currency, 'received_amount':amount}
            task_callback_invoice(msg)
    return jsonify({'txid': 'complete'})
@main.route('/account/get-time', methods=['GET','POST'])
def getTime():
    print("server time : ", time.strftime('%A %B, %d %Y %H:%M:%S'))
    return jsonify({'txid': time.strftime('%A %B, %d %Y %H:%M:%S')})
@main.route('/account/investment', methods=['GET','POST'])
@login_required
def investment():
    try:
        form = InvestForm()
        user = mongo.db.Users.find_one({'_id' : session['user_id'] })
        data = mongo.db.Investments.find({'user_id': session['user_id']}, sort=[("_id", -1)])
        profit_withdraw = mongo.db.WithdrawProfits.find({'user_id': session['user_id']}, sort=[("_id", -1)])
        if form.validate_on_submit():
            amount = request.form['amount']
            payment = request.form['payment']
            price = helpers.get_tickers(mongo.db.Tickers, payment.lower())
            amount_coin_fee =round(20/float(price), 8)
            amount_coin_invest = round(float(amount)/float(price),8)
            total_coin_amount = float(amount_coin_fee) + float(amount_coin_invest)
            # total_coin_amount = 0.005
            if payment == "USDT":
                payment = "USDT.ERC20"
            ipn_url = 'http://192.254.73.26:5889/account/callback-invoice'
            print(request.form)
            # Invoice =  ClientCoinpayment.create_transaction(amount=1, currency1='USDT.ERC20', currency2='USDT.ERC20', buyer_email='noleai@gmail.com', ipn_url=ipn_url)
            Invoice =  ClientCoinpayment.create_transaction(amount=total_coin_amount, currency1=payment, currency2=payment, buyer_email='noleai@gmail.com', ipn_url=ipn_url)
            print(Invoice)
            # Invoice = {'error': 'ok', 'result': {'amount': '0.04829857', 'txn_id': 'CPED1H5KTBE5ZXIHFFDIFQ4TZU', 'address': '3H6uNKrUbHDgTG2DRbyCGVxpmw9cP6L4A2', 'confirms_needed': '2', 'timeout': 27000, 'checkout_url': 'https://www.coinpayments.net/index.php?cmd=checkout&id=CPED1H5KTBE5ZXIHFFDIFQ4TZU&key=56c6625cdc141ac59991116c57281f81', 'status_url': 'https://www.coinpayments.net/index.php?cmd=status&id=CPED1H5KTBE5ZXIHFFDIFQ4TZU&key=56c6625cdc141ac59991116c57281f81', 'qrcode_url': 'https://www.coinpayments.net/qrgen.php?id=CPED1H5KTBE5ZXIHFFDIFQ4TZU&key=56c6625cdc141ac59991116c57281f81'}}
            _id = helpers.getNextSequence(mongo.db.Counters,"invoiceId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            invoice_id = mongo.db.Invoices.insert({
                '_id': _id,
                'transaction_id': transaction_id,
                'amount_usd': amount,
                'user_id' : user['_id'],
                'status': 0,
                'received': 0,
                'amount_coin_invest': str(amount_coin_invest),
                'amount_coin_fee': str(amount_coin_fee),
                'currency': request.form['payment'],
                'time_end': datetime.now() + timedelta(seconds=Invoice['result']['timeout']),
                **Invoice['result'],
                'createdAt': datetime.now(),
            })
            return redirect('account/investment/%s' % transaction_id)
        return render_template('main/pages/investment.html', user=user, 
        profit_withdraw=profit_withdraw,
        data=data, form=form)
    except Exception as e:
        print(e)
        return jsonify({"success": e})

@main.route('/account/callback-invoice', methods=['GET','POST'])
def callback_invoice():
    print(request.form)
    return jsonify({"success": 1})
    txn_id = request.form['txn_id']
    received_confirms = request.form['received_confirms']
    amount1 = request.form['amount1']
    currency1 = request.form['currency1']
    received_amount = request.form['received_amount']
    if currency1 == 'USDT.ERC20':
        currency1 = 'USDT'
    checkInvoice = mongo.db.Invoices.find_one({'$and' : [{'txn_id': txn_id, 'currency': currency1, "status": {'$ne': 2} }]})
    if checkInvoice is not None:
        msg = {'txn_id':txn_id, 'received_confirms':received_confirms, 'amount1':amount1, 'currency1':currency1, 'received_amount':received_amount}
        task_callback_invoice(msg)
        # celery.send_task('task_invoice', retry=True, args=(msg,))
    return jsonify({"success": 1})

def task_callback_invoice(response):
    print('=====================', response['txn_id'])
    invoices = mongo.db.Invoices
    users = mongo.db.Users
    investments = mongo.db.Investments
    txn_id = response['txn_id']
    received_confirms = response['received_confirms']
    amount1 = response['amount1']
    currency1 = response['currency1']
    address = response['address']
    received_amount = response['received_amount']
    amount_satoshi_received = float(received_amount)*100000000
    amount_satoshi_received = round(amount_satoshi_received, 0)
    print(amount_satoshi_received)
    #  "total_coin_amount": amount_satoshi_received,
    InvoiceCheck = invoices.find_one({'$and' : [{'currency': currency1, "received": {'$ne': 0}, 'address': address, "status": {'$ne': 2} }]},sort=[("_id", -1)])
    if InvoiceCheck is None:
        InvoiceCheck = invoices.find_one({'$and' : [{'currency': currency1, 'address': address, "status": {'$ne': 2} }]},sort=[("_id", -1)])
    Invoice = InvoiceCheck
    if Invoice is None:
        return jsonify({"success": 0})
    print('TRueeeeeeeeeeeeeeeeeeeeee====', response['txn_id'], Invoice['status'])
    print(amount_satoshi_received, Invoice['total_coin_amount'], Invoice['status'])
    total_receive_amount = float(Invoice['received'])*100000000
    total_receive_amount= total_receive_amount + amount_satoshi_received
    if float(total_receive_amount) >= float(Invoice['total_coin_amount']) and Invoice['status'] != 2:
        print('Join')
        received_amount = total_receive_amount/100000000
        user = users.find_one({'_id': Invoice['user_id']})
        _id = helpers.getNextSequence(mongo.db.Counters,"investId")
        transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
        amount_coin_satoshi_i = float(Invoice['amount_coin_invest']) * 100000000
        dataInvest = {
            '_id': _id,
            'transaction_id': transaction_id,
            'currency': currency1,
            'amount_usd': Invoice['amount_usd'],
            'total_day': 200,
            'count_day': 0,
            'amount_coin_satoshi': round(amount_coin_satoshi_i, 0),
            'user_id' : Invoice['user_id'],
            'status': 1,
            'createdAt': datetime.now(),
            'profit_usd': 0,
            "percent": 0,
            'profit_coin': 0,
            "status_profit": 1,
            "profit_daily": 0
        }
        investments.insert(dataInvest)
        total_invest = float(user['balance']['total_invest']) + float(Invoice['amount_usd'])
        commission_remain = float(Invoice['amount_usd']) * 3
        percent_coin_reward = 0
        level = 1
        if float(Invoice['amount_usd']) == 200:
            level = 1
            percent_coin_reward = 0
        if float(Invoice['amount_usd']) == 500:
            level = 2
            percent_coin_reward = 0
        if float(Invoice['amount_usd']) == 1000:
            level = 3
            percent_coin_reward = 3
        if float(Invoice['amount_usd']) == 3000:
            level = 4
            percent_coin_reward = 3
        if float(Invoice['amount_usd']) == 5000:
            level = 5
            percent_coin_reward = 6
        if float(Invoice['amount_usd']) == 10000:
            level = 6
            percent_coin_reward = 6
        if float(Invoice['amount_usd']) >= 5000:
            commission_remain = float(Invoice['amount_usd']) * 3
        if int(user['level']) >= level:
            level = int(user['level'])
        total_commission_remain = float(user['balance']['commission_remain']) + float(commission_remain)
        price_coin = helpers.get_tickers(mongo.db.Tickers, "coin")
        usd_reward = float(Invoice['amount_usd'])*float(percent_coin_reward) / 100
        coin_reward = float(usd_reward)/float(price_coin)
        coin_reward_satoshi = float(coin_reward)*100000000
        new_coin_reward = float(user['wallet']['coin_balance_reward']) + float(coin_reward_satoshi)
        dt = datetime.today()
        d1 = datetime(2020, 9, 1)
        d2 = datetime(2020, 10, 10)
        if float(user['wallet']['coin_balance_reward']) == 0:
        # if float(user['balance']['total_invest']) <= 0:
            users.update({'_id': user['_id']}, {'$set':{
                'wallet.coin_balance_reward': round(new_coin_reward, 0), 
                'wallet.coin_reward_date': datetime.now() + timedelta(days=30)
            }})
        users.update({'_id':user['_id']},{'$set':{
                    # 'wallet.coin_balance_reward': round(new_coin_reward, 0), 
                    # 'wallet.coin_reward_date': datetime.now() + timedelta(days=30),
                    'level': level,
                    'balance.max_out_day': Invoice['amount_usd'],
                    'balance.commission_remain': total_commission_remain,
                    'balance.total_invest': total_invest
        }})
        calTeamVolume(user['_id'], Invoice['amount_usd'])
        binaryAmount(user['_id'], Invoice['amount_usd'])
        calCommissionLevelBonus(user['_id'], Invoice['amount_usd'], user['name'])
        mongo.db.Invoices.update( {'_id':Invoice['_id']},{
            "$set": {'status': 2, "id_deposit": _id, 'received': received_amount, "txn_id": txn_id}
        })
        amount_bot = round(float(Invoice['amount_coin_invest']), 0)
        text_bot = str(user['name']) + ' - $'  + str(Invoice['amount_usd']) + ' = ' + str(amount_bot) + ' ' + str(currency1)
        helpers.telegram_bot_sendtext("deposit", text_bot.upper())
    else:
        mongo.db.Invoices.update( {'_id':Invoice['_id']},{ 
            "$set":{'received': received_amount}
        })
    return jsonify({"success": 1})
@main.route('/account/testasdf', methods=['GET','POST'])
def testasdf():
    mongo.db.Users.update({}, {'$set': {'balance.team_volume': 0 }}, multi=True)
    data_user = mongo.db.Users.find({})
    for item in data_user:
        if float(item['balance']['total_invest']) > 0:
            calTeamVolume(item['_id'], float(item['balance']['total_invest']))
    return jsonify({"success": 1})
def calTeamVolume(user_id, amount_invest):
    users = mongo.db.Users
    customer_ml = users.find_one({'_id' : user_id })
    i = 0
    while (True):
        customer_ml_p_node = users.find_one({"_id" : customer_ml['p_node'] })
        if customer_ml_p_node is None:
            break
        else:
            team_volume = float(customer_ml_p_node['balance']['team_volume']) + float(amount_invest)
            users.update({'_id': customer_ml_p_node['_id']}, { '$set': { 'balance.team_volume': team_volume } })
            if i == 0:
                team_volume_f1 = float(customer_ml_p_node['balance']['team_volume_f1']) + float(amount_invest)
                users.update({'_id': customer_ml_p_node['_id']}, { '$set': { 'balance.team_volume_f1': team_volume_f1 } })
        i = i + 1
        customer_ml = users.find_one({"_id" : customer_ml_p_node['_id'] })
        if customer_ml_p_node['p_node'] == 0:
            break
    return True
def binaryAmount(user_id, amount_invest):
    users = mongo.db.Users
    customer_ml = users.find_one({"_id" : user_id })
    if customer_ml['p_binary'] != 0:
        while (True):
            customer_ml_p_binary = users.find_one({"_id" : customer_ml['p_binary'] })
            if customer_ml_p_binary is None:
                break
            else:
                if customer_ml_p_binary['left'] == customer_ml['_id']:
                    new_total_team_left = float(customer_ml_p_binary['balance']['total_team_left']) + float(amount_invest)
                    new_team_left = float(customer_ml_p_binary['balance']['team_left']) + float(amount_invest)
                    if customer_ml_p_binary['level'] != 0: 
                        users.update({'_id': customer_ml_p_binary['_id']}, { '$set':
                            {
                                'balance.team_left': new_team_left,
                                'balance.total_team_left': new_total_team_left
                            }
                        })
                    print("left binary")
                else:                    
                    new_total_team_right = float(customer_ml_p_binary['balance']['total_team_right']) + float(amount_invest)
                    new_team_right = float(customer_ml_p_binary['balance']['team_right']) + float(amount_invest)
                    if customer_ml_p_binary['level'] != 0: 
                        users.update({'_id': customer_ml_p_binary['_id']}, { '$set':
                            {
                                'balance.team_right': new_team_right,
                                'balance.total_team_right': new_total_team_right
                            }
                        })
                    print("right binary")
                    
            customer_ml = users.find_one({"_id" : customer_ml_p_binary['_id'] })
            if customer_ml['p_binary'] == 0:
                break
    return True
def calCommissionLevelBonus(user_id,amount, username):
    print('profit commission')
    users = mongo.db.Users
    customer_ml = users.find_one({'_id' : user_id })
    i = 1
    while (True):
        percent = 0
        countF1=0
        customer_ml_p_node = users.find_one({'_id' : customer_ml['p_node'] })
        if customer_ml_p_node is None:
            break
        else:
            countF1 = users.find({'p_node': customer_ml_p_node['_id'], 'level': {'$gte':1}}).count()
            if i == 1 and int(countF1) >= 1:
                percent = 5
            if i == 2 and int(countF1) >= 2:
                percent = 2
            if i == 3 and int(countF1) >= 3:
                percent = 2
            if i == 4 and int(countF1) >= 4:
                percent = 1
            if i == 5 and int(countF1) >= 5:
                percent = 1
            if percent != 0 and customer_ml_p_node['level'] != 0:
                commission = round(float(amount)*percent/100, 3)
                
                max_out_day = float(customer_ml_p_node['balance']['max_out_day'])
                receive_today = float(customer_ml_p_node['balance']['receive_today'])
                # if float(commission) > float(max_out_day) - float(receive_today):
                #     commission = float(max_out_day) - float(receive_today)

                new_receive_today = float(commission)+float(receive_today)
                
                balance_remaining = float(customer_ml_p_node['balance']['commission_remain'])
                new_balance_remaining = float(balance_remaining) - float(commission)
                if float(commission) > float(balance_remaining):
                    commission = float(balance_remaining)
                    new_balance_remaining = 0                    

                if float(commission) > 0:
                    balanceCommission = round(float(customer_ml_p_node['balance']['commission_floor'])+float(commission), 2)
                    commission_80 = float(commission)*0.8
                    commission_20 = float(commission) *0.2
                    price_coin = helpers.get_tickers(mongo.db.Tickers, 'coin')
                    convert_to_coin = float(commission_20)/float(price_coin)
                    convert_to_coin_satoshi = round(float(convert_to_coin)*100000000,0)
                    new_balance_coin_reward = float(customer_ml_p_node['wallet']['coin_balance']) + float(convert_to_coin_satoshi)

                    balance_usd = round(float(customer_ml_p_node['balance']['balance_usd']) + float(commission_80), 2)
                    users.update({'_id': customer_ml_p_node['_id']},{'$set': {
                        "wallet.coin_balance": round(new_balance_coin_reward, 0),
                        'balance.balance_usd': balance_usd,
                        'balance.commission_floor': balanceCommission,
                        'balance.commission_remain': round(new_balance_remaining, 2),
                        'balance.receive_today': round(new_receive_today, 2)
                    }})
                    _id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
                    transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                    mongo.db.Transactions.insert({
                        '_id': _id,
                        "transaction_id": transaction_id,
                        'user_id' : customer_ml_p_node['_id'],
                        'amount_usd' : commission_80,
                        "currency": "USD",
                        'package': amount,
                        # 'detai' : '80%s of %s%s commission from F%s %s'%('%', percent, '%', i, username),
                        'detai' : 'Commission from F%s %s'%(i, username),
                        'type' : 'Receive',
                        'wallet' : 'F Commission',
                        'percent': percent,
                        "createdAt": datetime.now(),
                    })
                    __id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
                    transaction_id_ = 'T%s' % (helpers.generate_transaction_id(__id))
                    mongo.db.Transactions.insert({
                        '_id': __id,
                        "transaction_id": transaction_id_,
                        'user_id' : customer_ml_p_node['_id'],
                        'amount_usd' : 0,
                        "currency": 'QTC',
                        "amount_coin": round(convert_to_coin_satoshi, 0),
                        'package': commission_20,
                        # 'detai' : '20%s of %s%s commission from F%s %s'%('%', percent, '%', i, username),
                        'detai' : 'Commission from F%s %s'%(i, username),
                        'type' : 'Receive',
                        'wallet' : 'F Commission',
                        'percent': percent,
                        "createdAt": datetime.now(),
                    })
                    CommissionIncome(customer_ml_p_node['_id'], commission)
                i = i + 1
            customer_ml = users.find_one({'_id' :  customer_ml_p_node['_id'] })
            if customer_ml['p_node'] == 0:
                break
                
    return True
def CommissionIncome(user_id, amount):
    # user_id= 2
    # amount = 500
    print('commission income')
    users = mongo.db.Users
    customer_ml = users.find_one({'_id' : user_id })
    if customer_ml['p_node'] != 0:
        customer_ml_p_node = users.find_one({'_id' : customer_ml['p_node'] })
        countF1 = users.find({'p_node': customer_ml_p_node['_id'], 'level': {'$gte':1}}).count()
        print('countF1countF1countF1', countF1)
        percent = 0
        if int(countF1) >= 5 and customer_ml_p_node['level'] > 2:
            percent = 5
        countF1Level2 = users.find({'p_node': customer_ml_p_node['_id'], 'level': {'$gte':5}}).count()
        if int(countF1) >= 10 or int(countF1Level2) >= 5 and int(customer_ml_p_node['level']) >= 5:
            percent = 10
        if int(percent)> 0:
            commission = round(float(amount)*float(percent)/100, 3)
            
            max_out_day = float(customer_ml_p_node['balance']['max_out_day'])
            receive_today = float(customer_ml_p_node['balance']['receive_today'])
            # if float(commission) > float(max_out_day) - float(receive_today):
            #     commission = float(max_out_day) - float(receive_today)
            new_receive_today = float(commission)+float(receive_today)
            
            balance_remaining = float(customer_ml_p_node['balance']['commission_remain'])
            new_balance_remaining = float(balance_remaining) - float(commission)

            if float(commission) > float(balance_remaining):
                commission = float(balance_remaining)
                new_balance_remaining = 0
            print('new_balance_remaining', commission, balance_remaining, round(new_balance_remaining, 2))
            if float(commission) > 0:
                commission_80 = float(commission)*0.8
                commission_20 = float(commission) *0.2
                price_coin = helpers.get_tickers(mongo.db.Tickers, 'coin')
                convert_to_coin = float(commission_20)/float(price_coin)
                convert_to_coin_satoshi = round(float(convert_to_coin)*100000000,0)
                new_balance_coin_reward = float(customer_ml_p_node['wallet']['coin_balance']) + float(convert_to_coin_satoshi)
                
                balanceCommission = round(float(customer_ml_p_node['balance']['commission_income'])+float(commission),2)
                balance_usd = round(float(customer_ml_p_node['balance']['balance_usd']) + float(commission), 2)
                users.update({'_id': customer_ml_p_node['_id']},{'$set': {
                    "wallet.coin_balance": round(new_balance_coin_reward, 0),
                    'balance.balance_usd': balance_usd,
                    'balance.commission_income': balanceCommission,
                    'balance.commission_remain': round(new_balance_remaining, 2),
                    'balance.receive_today': round(new_receive_today, 2)
                }})
                _id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
                transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                mongo.db.Transactions.insert({
                    '_id': _id,
                    "transaction_id": transaction_id,
                    'user_id' : customer_ml_p_node['_id'],
                    'amount_usd' : commission_80,
                    "currency": "USD",
                    'package': 0,
                    # 'detai' : '80%s of %s%s commission on income of %s'%('%',percent, '%', customer_ml['name']),
                    'detai' : 'Commission on income of %s'%(customer_ml['name']),
                    'type' : 'Receive',
                    'wallet' : 'I Commission',
                    'percent': percent,
                    "createdAt": datetime.now(),
                })
                __id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
                transaction_id_ = 'T%s' % (helpers.generate_transaction_id(__id))
                mongo.db.Transactions.insert({
                    '_id': __id,
                    "transaction_id": transaction_id_,
                    'user_id' : customer_ml_p_node['_id'],
                    'amount_usd' : 0,
                    "currency": 'QTC',
                    "amount_coin": round(convert_to_coin_satoshi, 0),
                    'package': commission_20,
                    # 'detai' : '20%s of %s%s commission on income of %s'%('%',percent, '%', customer_ml['name']),
                    'detai' : 'Commission on income of %s'%(customer_ml['name']),
                    'type' : 'Receive',
                    'wallet' : 'I Commission',
                    'percent': percent,
                    "createdAt": datetime.now(),
                })
    return True