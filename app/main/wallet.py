from datetime import datetime,date, timedelta
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash, jsonify
from flask_login import login_required
from . import main
import json
from app import cache, mongo, ClientCoinpayment, rpc_connection
from app.utils import helpers, web3_api, tron_api
from .forms import withdrawCommissionForm, withdrawTokenForm, convertTokenForm, withdrawCryptoForm
import logging
import onetimepass
import random as r
from .send_mail import send_mail_otp
from .dashboard import LimitWithdrawComm
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)
def otpgen():
    otp=""
    for i in range(6):
        otp+=str(r.randint(1,9))
    return otp
@main.route('/account/wallet', methods=['GET','POST'])
@login_required
def WalletMain():
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data = mongo.db.Deposits.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    data_crypto_withdraw = mongo.db.WithdrawCryptos.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    return render_template('main/pages/wallet.html', 
        user=user,
        data=data,
        data_crypto_withdraw=data_crypto_withdraw,
        form = withdrawCryptoForm()
    )

@main.route("/account/wallet/get-otp", methods=['POST'])
@login_required
def GetOTP():
    try:
        if request.method == 'POST':
            print("==================")
            otp_code = otpgen()
            print(otp_code)
            user = mongo.db.Users.find_one({'_id' : session['user_id'] })
            data_code = {
                'code': otp_code,
                'user_id' : user['_id'],
                "name": user['name'],
                "email": user['email'],
                "type": request.form['type'],
                "status": 0,
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Otps.insert(data_code)
            send_mail_otp(data_code, request.form['type'])
            return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")
        return jsonify({'success':0})

def validate_crypto_address(currency, address):
    status = False
    currency_valid = currency #if currency != "QTC" else "ETH"
    currency_valid = currency_valid if currency != "QTC2" else "QTC"
    currency_valid = currency_valid if currency != "QTC3" else "QTC"
    currency_valid = currency_valid if currency != "QTC4" else "QTC"
    currency_valid = currency_valid if currency != "USDT" else "ETH"
    currency_valid = currency_valid if currency != "USD" else "TRX"
    if currency_valid == "QTC":
        valid = rpc_connection.validateaddress(address)
        status = valid['isvalid']
    elif currency_valid == "TRX":
        status = tron_api.isAddress(address)
    else:
        validate_address_usdt = helpers.verify_address(address, currency_valid.lower())
        if validate_address_usdt == 0:
            status = False
        else:
            status = True
    return status

@main.route('/account/wallet/withdraw-crypto', methods=['GET','POST'])
@login_required
def withdrawCrypto():
    try:
        form = withdrawCryptoForm()
        user = mongo.db.Users.find_one({'_id' : session['user_id'] })
        # if(session['user_id'] == 7):
        #     return jsonify({'success': 0, "msg": "Your account is currently unable to withdraw funds. Please contact admin for support"})
        if form.validate_on_submit():
            currency = request.form['_currency']
            amount = request.form['amount']
            address = request.form['address']
            otp = request.form['code']
            otp_2fa = request.form['otp']
            print(currency)
            currency_valid = currency #if currency != "QTC" else "ETH"
            currency_valid = currency_valid if currency != "QTC2" else "QTC"
            currency_valid = currency_valid if currency != "QTC3" else "QTC"
            currency_valid = currency_valid if currency != "QTC4" else "QTC"
            valid_address = validate_crypto_address(currency, address)
            if valid_address == False:
                return jsonify({'success': 0, "msg": "Invalid Address"})

            check_otp = mongo.db.Otps.find_one({'user_id': session['user_id'], "code": otp, "status": 0})
            if check_otp is None:
                return jsonify({'success': 0, "msg": "Wrong OTP code"})
            check_2fa = verify_totp(otp_2fa, user['security']['two_factor_auth']['code'])
            if check_2fa == False:
                return jsonify({'success': 0, "msg": "The two-factor authentication code you specified is incorrect."})
            coin_price = currency
            balance = 0
            wallet_update  = ''
            
            amount_satoshi = float(amount)*100000000
            if currency == "USD":
                coin_price="USDT"
                fee_percent = 5
                balance = float(user['wallet']['usd_balance'])*100000000
                wallet_update  = 'wallet.usd_balance'
            elif currency == "USDT":
                fee_percent = 5
                balance = user['wallet']['USDT']['balance']
                wallet_update  = 'wallet.USDT.balance'
            elif currency == "BTC":
                fee_percent = 5
                balance = user['wallet']['BTC']['balance']
                wallet_update  = 'wallet.BTC.balance'
            elif currency == "ETH":
                fee_percent = 5
                balance = user['wallet']['ETH']['balance']
                wallet_update  = 'wallet.ETH.balance'
            elif currency == "TRX":
                fee_percent = 5
                balance = user['wallet']['TRX']['balance']
                wallet_update  = 'wallet.TRX.balance'
            elif currency =="QTC3":
                fee_percent = 1
                coin_price = "coin"
                wallet_update  = 'wallet.QTC.balance'
                balance = user['wallet']['QTC']['balance']
            elif currency == "QTC":
                fee_percent = 5
                coin_price = "coin"
                # balance = user['wallet']['QTC']['balance']
                wallet_update  = 'wallet.coin_balance'
                balance = float(user['wallet']['coin_balance'])
            elif currency == "QTC4":
                fee_percent = 5
                coin_price = "coin"
                # balance = user['wallet']['QTC']['balance']
                wallet_update  = 'wallet.balance_promotion'
                balance = float(user['wallet']['balance_promotion'])
            elif currency == "QTC2":
                fee_percent = 1
                coin_price = "coin"
                wallet_update = 'wallet.coin_balance_reward'
                balance = float(user['wallet']['coin_balance_reward']) 
                d1 = user['wallet']['coin_reward_date']
                d2 = datetime.now()
                listOn = ['hcm68' , 'phuloc1', 'phulocteam','maihien','maihien1','maihien2', 'tn366']
                if user['name'] not in listOn:
                    if d1 > d2:
                        return jsonify({'success': 0, "msg": 'Your next withdrawal date is %s' %  d1})
                    else:
                        max_withdraw = float(balance)*0.1
                        if float(amount_satoshi) > float(max_withdraw):
                            error = True
                            max_withdraw_coin = round(float(max_withdraw)/100000000, 8)
                            return jsonify({'success': 0, "msg": 'Max amount: %s QTC' %  max_withdraw_coin})
            else:
                return jsonify({'success': 0, "msg": "Error currency"})
            # balance = user['wallet'][currency]['balance']
            
            print(amount_satoshi, balance)
            if float(amount_satoshi) > float(balance):
                return jsonify({'success':0, "msg": "Your balance not enough"})
            price = helpers.get_tickers(mongo.db.Tickers, coin_price.lower())
            max_ = LimitWithdrawComm()
            max_withdraw_usd = float(max_)*2
            print('priceamount==================',price, amount)
            amount_usd = float(amount)*float(price)
            withdraw_usd_today = float(user['balance']['withdraw_usd_today'])
            new_withdraw_usd_today = float(withdraw_usd_today)+float(amount_usd)
            if float(amount_usd) > float(max_withdraw_usd) - float(withdraw_usd_today):
                return jsonify({'success': 0, "msg": "Exceeded withdrawal limit"})
            new_balance = float(balance) - float(amount_satoshi)
            balance_withdraw_week = float(user['balance']['withdraw_usd_week'])
            if currency == "USD":
                new_balance = float(new_balance)/100000000
                balance_withdraw_week = float(balance_withdraw_week)+float(amount_usd)
            if float(balance_withdraw_week) > 100:
                return jsonify({'success': 0, "msg": "Exceeded withdrawal limit $100 per week"})
            if currency == "QTC2":
                mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { 
                    wallet_update: round(new_balance, 0),
                    'wallet.coin_reward_date':  datetime.now() + timedelta(days=30)
                } })
            else:
                mongo.db.Users.update({'_id' : user['_id'] },{'$set' : {
                    wallet_update : round(new_balance, 0),
                    "balance.withdraw_usd_today": round(new_withdraw_usd_today, 3),
                    "balance.withdraw_usd_week": round(balance_withdraw_week, 3),
                }})
            _id = helpers.getNextSequence(mongo.db.Counters,"withdrawId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            fee_ = 100 - fee_percent
            amount_after_fee = float(amount_satoshi)*float(fee_)/100
            data_withdraw = {
                "_id": _id,
                "transaction_id": transaction_id,
                'currency': currency,
                'tx': "",
                'address': address,
                'amount_coin_satoshi': round(float(amount_after_fee), 0),
                "fee_percent": fee_percent, 
                "amount_usd": amount_usd,             
                'user_id' : user['_id'],
                "status": 0,
                "detail": "To %s Address" % (currency),
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Withdraws.insert(data_withdraw)
            mongo.db.Otps.update({"_id": check_otp['_id']}, {"$set":{"status": 1}})
            if user['name'] != "root":
                text_bot =  str(user['name']) + ' - Withdraw - '  + str(amount) + ' ' + str(currency)
                helpers.telegram_bot_sendtext("withdraw", text_bot)
            return jsonify({'success':1})
        else:
            return jsonify({'success':0, 'msg':"Error"})
    except Exception as e:
        print(e)
        logging.exception("An exception was thrown!")
        return jsonify({'success':0, 'msg':"Error"})
@main.route('/account/fetch-balance', methods=['GET','POST'])
@main.route('/account/fetch-balance/<currency>', methods=['GET','POST'])
@login_required
def fetchBalance(currency=""):
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    if currency != "":
        if currency == "USD":
            return jsonify({'data': {'balance': user['wallet']['usd_balance']}})
        send_data= user['wallet'][currency] if currency != "QTC" else {'balance': user['wallet']['coin_balance']}
    else:
        send_data = user['wallet']
    return jsonify({'data': send_data})

@main.route('/account/fetch-ticker', methods=['GET','POST'])
def fetchTicker():
    data = mongo.db.Tickers.find_one({})
    data_send = {
        "btc": data['btc_price'],
        "trx": data['trx_price'],
        "eth": data['eth_price'],
        "qtc": data['coin_price']
    }
    return jsonify({'data': data_send})

@main.route('/account/wallet/get-address', methods=['GET','POST'])
@login_required
def WalletMainGetAddress():
    # return jsonify({'success':0})
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    try:
        if request.method == 'POST':
            currency = request.form['currency']
            if currency == "QTC":
                address = user['wallet']['qtc_address']
            elif currency =="BTC":
                address = user['wallet']['BTC']['address']
            elif currency =="ETH":
                address = user['wallet']['ETH']['address']
            elif currency =="TRX":
                address = user['wallet']['TRX']['address']
            elif currency =="USDT":
                address = user['wallet']['USDT']['address']
            url_callback = 'http://192.254.73.26:5889/account/cbcadwejswtryqweqeweoacnmlfkqeqwe'
            if address == "":
                wallet_update = 'wallet.'+currency+'.address' if currency != 'USDT.ERC20' else 'wallet.USDT.address'
                if currency == "QTC":
                    # result = web3_api.create_new_wallet_via_web3()
                    # address = result['address']
                    # key =result['key']
                    address = rpc_connection.getnewaddress('')
                    if address:
                        mongo.db.Users.update({'_id' : session['user_id'] },{'$set' : {
                            'wallet.qtc_address' : address, 
                            'wallet.qtc_private_key': "",
                            'wallet.QTC.address': address,
                            'wallet.QTC.private_key': ""
                        }})
                    else:
                        address = ""
                else:
                    coin = currency if currency != 'USDT' else 'USDT.ERC20'
                    respon_wallet_btc = ClientCoinpayment.get_callback_address(currency=coin, ipn_url=url_callback)
                    if respon_wallet_btc['error'] == 'ok':
                        address =  respon_wallet_btc['result']['address']
                        mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { 
                            wallet_update : address
                        } })
                    else:
                        address = ''
                
        return jsonify({'success':1, 'address': address})
    except BaseException:
        logging.exception("An exception was thrown!")
        return jsonify({'success':0})

@main.route('/account/wallet/callback-qtc/<txid>', methods=['GET','POST'])
def callbAckCoinqTC(txid):
    transaction = rpc_connection.gettransaction(txid)
    checkTx = mongo.db.Txs.find_one({'tx': txid})
    if checkTx is None:
        gen = False
        if 'generated' in transaction:
            gen = True
            print(transaction['generated'])
        details = transaction['details']
        print(details)
        if len(details) > 0 and gen == False:
            for x in details:
                if x['category'] == 'receive':
                    address = x['address']
                    amount_deposit = float(x['amount'])
                    user = mongo.db.Users.find_one({'wallet.qtc_address' : address })
                    if user is not None:
                        amount_satoshi = float(amount_deposit)*100000000
                        new_balance = float(user['wallet']['coin_balance'])+float(amount_satoshi)
                        new_coin_balance = float(user['wallet']['QTC']['balance'])+float(amount_satoshi)
                        price = helpers.get_tickers(mongo.db.Tickers, 'coin')
                        amount_usd = float(amount_deposit)*float(price)
                        # mongo.db.Users.update({'_id' : user['_id'] },{'$set' : {
                        #     'wallet.coin_balance' : new_balance,
                        #     # 'wallet.QTC.balance': round(new_coin_balance,0)
                        # }})
                        _id = helpers.getNextSequence(mongo.db.Counters,"TxId")
                        transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                        data_withdraw = {
                            "_id": _id,
                            "transaction_id": transaction_id,
                            'currency': 'QTC',
                            'tx': txid,
                            'address': address,
                            'amount_coin_satoshi': round(float(amount_satoshi), 0),                
                            "amount_usd": amount_usd,
                            'user_id' : user['_id'],
                            "status": 0,
                            "detail": "From QTC Address",
                            "createdAt": datetime.now()
                        }
                        withdraw_id = mongo.db.Txs.insert(data_withdraw)
    return jsonify({'success':1})
@main.route('/account/wallet/callback-token', methods=['GET','POST'])
def callbAckToken():
    print('==================')
    data = json.loads(request.data)
    print(data['tx'], data['address'], data['amount'])
    # print(request.data['tx'], request.data['address'], request.data['amount'])
    print('====================')
    amount = data['amount']
    amount_satoshi = float(amount)*100000000
    to_address = data['address']
    checkTx = mongo.db.Deposits.find_one({'tx': data['tx']})
    if checkTx is None:
        user = mongo.db.Users.find_one({'wallet.qtc_address' : to_address })
        if user is not None:
            new_balance = float(user['wallet']['coin_balance'])+float(amount_satoshi)
            new_coin_balance = float(user['wallet']['QTC']['balance'])+float(amount_satoshi)
            price = helpers.get_tickers(mongo.db.Tickers, 'coin')
            amount_usd = float(amount)*float(price)
            mongo.db.Users.update({'_id' : user['_id'] },{'$set' : {
                # 'wallet.coin_balance' : new_balance,
                'wallet.QTC.balance': new_coin_balance
            }})
            _id = helpers.getNextSequence(mongo.db.Counters,"DepositId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            data_withdraw = {
                "_id": _id,
                "transaction_id": transaction_id,
                'currency': 'QTC',
                'tx': data['tx'],
                'address': to_address,
                'amount_coin_satoshi': round(float(amount_satoshi), 0),                
                "amount_usd": amount_usd,
                'user_id' : user['_id'],
                "status": 1,
                "detail": "From QTC Address",
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Deposits.insert(data_withdraw)
    return jsonify({'success':1})
@main.route('/account/cbcadwejswtryqweqeweoacnmlfkqeqwe', methods=['GET','POST'])
def callbackCoinpayment():
    print('request')
    if request.method == 'POST':
        print(request.form)
        tx = request.form['txn_id']
        address = request.form['address']
        amount = float(request.form['amount'])
        currency = request.form['currency']
        query_search = 'wallet.'+currency+'.address' if currency != "USDT.ERC20" else 'wallet.USDT.address'  
        check_deposit = mongo.db.Txs.find_one({'tx': tx})
        user = mongo.db.Users.find_one({query_search: address })
        print(check_deposit)
        if check_deposit is None and user is not None:
            if currency =="BTC":
                balance = user['wallet']['BTC']['balance']
            elif currency =="ETH":
                balance = user['wallet']['ETH']['balance']
            elif currency =="TRX":
                balance = user['wallet']['TRX']['balance']
            elif currency =="USDT.ERC20":
                currency = "USDT"
                balance = user['wallet']['USDT']['balance']
            print(balance)
            price = helpers.get_tickers(mongo.db.Tickers, currency.lower())
            amount_usd = float(amount)*float(price)
            amount_satoshi = float(amount)*100000000
            new_balance = float(balance)+float(amount_satoshi)
            wallet_update  = 'wallet.'+currency+'.balance'
            # mongo.db.Users.update({'_id' : user['_id'] },{'$set' : {wallet_update : round(new_balance, 0)}})
            _id = helpers.getNextSequence(mongo.db.Counters,"TxId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            data_withdraw = {
                "_id": _id,
                "transaction_id": transaction_id,
                'currency': currency,
                'tx': tx,
                'address': address,
                'amount_coin_satoshi': round(float(amount_satoshi), 0),
                "amount_usd": amount_usd,             
                'user_id' : user['_id'],
                "status": 0,
                "detail": "From %s Address" % (currency),
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Txs.insert(data_withdraw)
    return json.dumps({'txid': 'complete'})

@main.route('/account/auto-txs', methods=['GET','POST'])
def autoCallbackTxs():
    print('request')
    dataTx = mongo.db.Txs.find_one({'status': 0})
    if dataTx is not None:
        print(dataTx)
        tx = dataTx['tx']
        address = dataTx['address']
        amount = float(dataTx['amount_coin_satoshi'])
        currency = dataTx['currency']
        query_search = 'wallet.'+currency+'.address' if currency != "USDT.ERC20" else 'wallet.USDT.address'
        query_search = "wallet.qtc_address" if currency == "QTC" else query_search
        check_deposit = mongo.db.Deposits.find_one({'tx': tx})
        user = mongo.db.Users.find_one({query_search: address })
        if check_deposit is None and user is not None:
            if currency =="BTC":
                balance = user['wallet']['BTC']['balance']
            elif currency =="QTC":
                balance = user['wallet']['coin_balance']
            elif currency =="ETH":
                balance = user['wallet']['ETH']['balance']
            elif currency =="TRX":
                balance = user['wallet']['TRX']['balance']
            elif currency =="USDT.ERC20":
                currency = "USDT"
                balance = user['wallet']['USDT']['balance']
            print(balance)
            new_balance = float(balance)+float(amount)
            wallet_update  = 'wallet.'+currency+'.balance' if currency != "QTC" else 'wallet.coin_balance'
            print(wallet_update, new_balance)
            mongo.db.Users.update({'_id' : user['_id'] },{'$set' : {wallet_update : round(new_balance, 0)}})
            _id = helpers.getNextSequence(mongo.db.Counters,"DepositId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            data_withdraw = {
                "_id": _id,
                "transaction_id": transaction_id,
                'currency': currency,
                'tx': tx,
                'address': address,
                'amount_coin_satoshi': round(float(amount), 0),
                "amount_usd": float(dataTx['amount_usd']),             
                'user_id' : user['_id'],
                "status": 1,
                "detail": "From %s Address" % (currency),
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Deposits.insert(data_withdraw)
            mongo.db.Txs.update({"_id": dataTx['_id']}, {"$set":{"status": 1}})
        else:
            mongo.db.Txs.update({"_id": dataTx['_id']}, {"$set":{"status": 1}})
    return json.dumps({'txid': 'complete'})

@main.route('/account/withdrawals', methods=['GET','POST'])
@login_required
def withdraw():
    form_withdraw_commission = withdrawCommissionForm()
    form_withdraw_token = withdrawTokenForm()
    form_convert_token = convertTokenForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data = mongo.db.Withdraws.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    data_convert = mongo.db.Converts.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    return render_template('main/pages/withdraw.html', 
    user=user, data=data, 
    data_convert=data_convert,
    form_withdraw_commission = form_withdraw_commission,
    form_withdraw_token=form_withdraw_token,
    form_convert_token=form_convert_token
    )

@main.route('/account/withdraw-commission', methods=['GET','POST'])
@login_required
def withdrawCommission():
    form_withdraw_commission = withdrawCommissionForm()
    form_withdraw_token = withdrawTokenForm()
    form_convert_token = convertTokenForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data = mongo.db.Withdraws.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    data_convert = mongo.db.Converts.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    if form_withdraw_commission.validate_on_submit():
        max_ = LimitWithdrawComm()
        max_withdraw = float(max_)*2
        error = False
        print(request.form)
        
        otp = request.form['code']
        otp_2fa = request.form['otp']
        amount_usd = request.form['amount_usd']
        address = request.form['address']
        payment_system = request.form['payment_system'] #BTC,ETH,USDT, TRX
        if payment_system != "QTC":
            error = True
            flash("Error currency")
        # if(session['user_id'] == 7):
        #     error = True
        #     flash("Your account is currently unable to withdraw funds. Please contact admin for support")
        coin_price = payment_system
        if payment_system == "QTC":
            coin_price = "coin"
            check_trx_address = rpc_connection.validateaddress(address)
            if check_trx_address == False:
                error = True
                flash("Invalid QTC Address")
        if payment_system == "TRX":
            check_trx_address = tron_api.isAddress(address)
            if check_trx_address == False:
                error = True
                flash("Invalid Address")
        withdraw_usd_today = float(user['balance']['withdraw_usd_today'])
        if float(amount_usd) > float(max_withdraw) - float(withdraw_usd_today):
            error = True
            flash("Exceeded withdrawal limit")
        new_withdraw_usd_today = float(withdraw_usd_today)+float(amount_usd)
        currency_valid = payment_system
        if payment_system == "USDT":
            currency_valid = "ETH"
        validate_address = helpers.verify_address(address, currency_valid)
        print("validate_address", validate_address)
        check_otp = mongo.db.Otps.find_one({'user_id': session['user_id'], "code": otp, "status": 0})
        if check_otp is None:
            error = True
            flash("Wrong OTP code")
        check_2fa = verify_totp(otp_2fa, user['security']['two_factor_auth']['code'])
        if check_2fa == False:
            error = True
            flash("The two-factor authentication code you specified is incorrect.")
        if payment_system == "ETH":
            error = True
            flash("Coming Soon")
        if validate_address == 0:
            error = True
            flash("Invalid Address")
        check_amount = helpers.is_number(amount_usd)
        if check_amount == False:
            flash("Please enter amount")
            error = True
        balance_usd = float(user['balance']['balance_usd'])
        if float(amount_usd) > float(balance_usd):
            flash("Your balance is not enough")
            error = True
        if float(amount_usd) < 50:
            error = True
            flash("Min withdraw commission $50")
        if error == False:
            mongo.db.Otps.update({"_id": check_otp['_id']}, {"$set":{"status": 1}})
            new_balance_wallets = float(balance_usd) - float(amount_usd)
            mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { 
                "balance.balance_usd": float(new_balance_wallets),
                "balance.withdraw_usd_today": round(new_withdraw_usd_today, 3)
                } })
            price = helpers.get_tickers(mongo.db.Tickers, coin_price.lower())
            
            amount_usd_fee = float(amount_usd)*0.05
            total_amount_usd = float(amount_usd)*0.95
            amount_coin = round(float(total_amount_usd)/float(price),8)
            
            amount_coin_satoshi = float(amount_coin)*100000000
            print(total_amount_usd, amount_coin, amount_coin_satoshi)
            _id = helpers.getNextSequence(mongo.db.Counters,"withdrawId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            data_withdraw = {
                "_id": _id,
                "transaction_id": transaction_id,
                'currency': payment_system,
                'address': address,
                'price': price,
                'amount_usd': round(float(amount_usd), 2),
                'fee': round(float(amount_usd_fee), 2),
                "fee_percent": 5,
                'amount_coin_satoshi': round(float(amount_coin_satoshi), 0),                
                'user_id' : session['user_id'],
                'tx': "",
                "status": 0,
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Withdraws.insert(data_withdraw)
            text_bot =  str(user['name']) + ' - Withdraw Commission with '+ str(payment_system) +' $'  + str(amount_usd) + ' = ' +str(amount_coin) + ' ' + str(payment_system)
            helpers.telegram_bot_sendtext("withdraw", text_bot)
            flash("Withdraw Successful")
        return redirect('/account/dashboard')
    return render_template('main/pages/withdraw.html', 
    user=user, data=data,
    data_convert=data_convert,
    form_withdraw_commission = form_withdraw_commission,
    form_withdraw_token=form_withdraw_token,
    form_convert_token=form_convert_token
    )

@main.route('/account/convert-token', methods=['GET','POST'])
@login_required
def convertToken():
    form_withdraw_commission = withdrawCommissionForm()
    form_withdraw_token = withdrawTokenForm()
    form_convert_token = convertTokenForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data = mongo.db.Withdraws.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    data_convert = mongo.db.Converts.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    if form_convert_token.validate_on_submit():
        error = False
        to_wallet = request.form['to_wallet']
        amount_from = request.form['amount_from']
        check_amount = helpers.is_number(amount_from)
        if check_amount == False:
            flash("Please enter amount")
            error = True
        coin_balance = float(user['wallet']['coin_balance'])
        amount_from_satoshi =round(float(amount_from)*100000000, 0)
        if float(amount_from_satoshi) > float(coin_balance):
            flash("Your balance is not enough")
            error = True
        if error == False:
            price_from = helpers.get_tickers(mongo.db.Tickers, 'coin')
            price_to = helpers.get_tickers(mongo.db.Tickers, to_wallet.lower())
            amount_usd_from = float(amount_from)*float(price_from)
            amount_convert = round(float(amount_usd_from)/float(price_to), 8)
            amount_convert_satoshi = round(float(amount_convert)*100000000, 0)

            wallet_to = 'wallet.'+to_wallet.lower()+'_balance'
            
            balance_to =  user['wallet'][to_wallet.lower()+'_balance']
            new_balance_coin = float(coin_balance) - float(amount_from_satoshi)
            new_balance_to = float(balance_to)+float(amount_convert_satoshi)
            print(wallet_to, amount_convert_satoshi, new_balance_to)
            mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { 
                "wallet.coin_balance": str(round(float(new_balance_coin), 0)),
                wallet_to : str(round(float(new_balance_to), 0))
            } })
            _id = helpers.getNextSequence(mongo.db.Counters,"convertId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            data_history = {
                "_id": _id,
                "transaction_id": transaction_id,
                'user_id' : session['user_id'],
                'from_wallet': 'QTC',
                'to_wallet': to_wallet,
                'amount_from': amount_from,
                'amount_coin_receive_satoshi': str(amount_convert_satoshi),
                'price_from': price_from,
                'price_to': price_to,
                'createdAt': datetime.now()
            }
            mongo.db.Converts.insert(data_history)
            flash("Convert Successfully")
        return redirect('/account/withdrawals')
    return render_template('main/pages/withdraw.html', 
    user=user, data=data, 
    data_convert=data_convert,
    form_withdraw_commission = form_withdraw_commission,
    form_withdraw_token=form_withdraw_token,
    form_convert_token=form_convert_token
    )


@main.route('/account/withdraw-token', methods=['GET','POST'])
@login_required
def withdrawToken():
    form_withdraw_commission = withdrawCommissionForm()
    form_withdraw_token = withdrawTokenForm()
    form_convert_token = convertTokenForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data = mongo.db.Withdraws.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    data_convert = mongo.db.Converts.find({'user_id': session['user_id']}, sort=[("_id", -1)])
    if form_withdraw_token.validate_on_submit():
        error = False
        
        wallet = request.form['wallet'].lower().strip()
        amount = request.form['amount']
        address = request.form['address']
        currency_valid = "ETH"
        validate_address = helpers.verify_address(address, currency_valid)
        print("validate_address", validate_address)
        if validate_address == 0:
            error = True
            flash("Invalid Address")
        check_amount = helpers.is_number(amount)
        if check_amount == False:
            flash("Please enter amount")
            error = True
        amount_satoshi = round(float(amount)*100000000, 0)
        coin_balance = float(user['wallet']['coin_balance'])
        wallet_to = 'wallet.coin_balance'         
        if wallet == 'coin_reward':
            wallet_to = 'wallet.coin_balance_reward'
            coin_balance = float(user['wallet']['coin_balance_reward']) 
            d1 = user['wallet']['coin_reward_date']
            d2 = datetime.now()
            if d1 > d2:
                error = True
                flash( 'Your next withdrawal date is %s' %  d1)
            else:
                 max_withdraw = float(coin_balance)*0.1
                 if float(amount_satoshi) > float(max_withdraw):
                     error = True
                     max_withdraw_coin = round(float(max_withdraw)/100000000, 8)
                     flash( 'Max amount: %s QTC' %  max_withdraw_coin)
        
        if float(amount_satoshi) > float(coin_balance):
            flash("Your balance is not enough")
            error = True
        if error == False:
            amountFee = float(amount_satoshi)*0.05
            new_amount_satoshi = float(amount_satoshi) - float(amountFee)
            new_balance = round(float(coin_balance) - float(amount_satoshi), 0)
            if wallet == 'coin_reward':
                mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { 
                    wallet_to: str(new_balance),
                    'wallet.coin_reward_date':  datetime.now() + timedelta(days=30)
                } })
            else:
                mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { 
                    wallet_to: str(new_balance)                    
                } })
            print('pooooooooooooooooooooooo')
            price = helpers.get_tickers(mongo.db.Tickers, 'coin')
            amount_usd = float(amount)*float(price)
            amountFee_usd = (float(amountFee)/100000000)*float(price)
            _id = helpers.getNextSequence(mongo.db.Counters,"withdrawId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            data_withdraw = {
                "_id": _id,
                "transaction_id": transaction_id,
                'currency': 'QTC',
                'address': address,
                'price': price,
                'amount_usd': round(float(amount_usd), 2),
                'fee': round(float(amountFee_usd), 3),
                'amount_coin_satoshi': round(float(new_amount_satoshi), 0),                
                'user_id' : session['user_id'],
                'tx': "",
                "status": 0,
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Withdraws.insert(data_withdraw)
           
            flash("Withdraw Successfully")
        return redirect('/account/withdrawals')
    return render_template('main/pages/withdraw.html', 
    user=user, data=data, 
    data_convert=data_convert,
    form_withdraw_commission = form_withdraw_commission,
    form_withdraw_token=form_withdraw_token,
    form_convert_token=form_convert_token
    )