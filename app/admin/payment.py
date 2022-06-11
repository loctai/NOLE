from datetime import datetime,date
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash, jsonify
from . import admin_router
from flask_pymongo import pymongo ,MongoClient
from flask_login import login_required
from .forms import PostForm,PropertyForm,EditProfileForm,CommentForm,EditProfileAdminForm, ProfitForm
from flask_login import current_user
from werkzeug import secure_filename
from functools import wraps
from cloudinary.uploader import upload_image
from cloudinary.utils import cloudinary_url
from app import cache 
from app.utils import helpers,web3_api, tron_api
import logging
import json
import time

# mongodb database connection
from app import mongo, ClientCoinpayment, rpc_connection

def admin_required(f):
    @wraps(f)
    def  wrap(*args, **kwargs):
        users = mongo.db.Users
        user= users.find_one({'_id': session['user_id'] },{'role':'1'})
        if user['role'] != 'admin':
                return redirect(url_for('auth.login', next=request.url))
        else:
            return f(*args, **kwargs)
    return wrap

@admin_router.route('/admin-management-page/pay-withdraw/<int:id>', methods=['POST'])
@login_required
@admin_required
def payment_withdraw(id):
    try:
        if request.method == 'POST':
            # new_address = web3_api.create_new_wallet_via_web3()
           
            dataSend = mongo.db.Withdraws.find_one({'_id': int(id), 'status': 0})
            if dataSend is not None:
                amount = float(dataSend['amount_coin_satoshi'])/100000000
                address = dataSend['address']
                if dataSend['currency'] == 'QTC' or dataSend['currency'] == 'QTC1' or dataSend['currency'] == 'QTC2' or dataSend['currency'] == 'QTC3':
                    print('QTCKKKKKKKKKKK')
                    # tx_hash = web3_api.transferToken(address, round(amount, 8), dataSend['_id'])
                    # print(tx_hash,'===')
                    # txid = rpc_connection.sendtoaddress(address, round(amount, 8))
                    txid = rpc_connection.sendfrom("admin", address, round(amount, 8))
                    print(txid)
                    mongo.db.Withdraws.update({'_id' : int(id) },{'$set' : {'status' : 1, 'tx': txid }})
                # elif dataSend['currency'] == "TRX":
                #     trx_status = tron_api.transferTrx(address, round(amount, 4))
                #     if trx_status['status'] == True:
                #         mongo.db.Withdraws.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': trx_status['txid'] }})
                elif dataSend['currency'] == "USD":
                    print(1)
                    res = tron_api.send_usdt(address, round(amount, 4))
                    if res:
                        mongo.db.Withdraws.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': res }})
                else:
                    amount = float(dataSend['amount_coin_satoshi'])/100000000
                    address = dataSend['address']
                    currency = "USDT.ERC20" if dataSend['currency'] == "USDT" else dataSend['currency']
                    print(amount,currency,address)
                    status_withdraw = ClientCoinpayment.create_withdrawal(amount=amount,currency=currency,address=address, auto_confirm = 1) 
                    print(status_withdraw,'respon_withdrawrespon_withdraw')
                    if status_withdraw['error'] == 'ok':
                        mongo.db.Withdraws.update({'_id' : int(id) },{'$set' : {'status' : 1}})
        return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")



@admin_router.route('/admin-management-page/pay-withdraw-profit/<int:id>', methods=['POST'])
@login_required
@admin_required
def payment_withdraw_profit(id):
    try:
        if request.method == 'POST':
            dataSend = mongo.db.WithdrawProfits.find_one({'_id': int(id), 'status': 0})
            if dataSend is not None:
                amount = float(dataSend['amount_coin_satoshi'])/100000000
                address = dataSend['address']
                if dataSend['currency'] == 'QTC':
                    # tx_hash = web3_api.transferToken(address, round(amount, 8), dataSend['_id'])
                    # print(tx_hash,'===')
                    # txid = rpc_connection.sendtoaddress(address, round(amount, 8))
                    txid = rpc_connection.sendfrom("admin", address, round(amount, 8))
                    print(txid)
                    mongo.db.WithdrawProfits.update({'_id' : int(id) },{'$set' : {'status' : 1, 'tx': txid }})
                # elif dataSend['currency'] == "TRX":
                #     trx_status = tron_api.transferTrx(address, round(amount, 4))
                #     if trx_status['status'] == True:
                #         mongo.db.WithdrawProfits.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': trx_status['txid'] }})
                else:                    
                    currency = "USDT.ERC20" if dataSend['currency'] == "USDT" else dataSend['currency']
                    print(amount,currency,address)
                    status_withdraw = ClientCoinpayment.create_withdrawal(amount=amount,currency=currency,address=address, auto_confirm = 1) 
                    print(status_withdraw,'respon_withdrawrespon_withdraw')
                    if status_withdraw['error'] == 'ok':
                        mongo.db.WithdrawProfits.update({'_id' : int(id) },{'$set' : {'status' : 1}})
        return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")
@admin_router.route('/admin/auto-pay-withdraw-profit-qtc', methods=['GET'])
def auto_payment_withdraw_profit_coin():
    try:
        # trx_status = tron_api.transferTrx("TTCbSEi55BnDrHF6LJ5YwsRPUXBdGbdtqS", 3.0933)
        # print('trx_status', trx_status['status'])
        # if trx_status['status'] == True:
        #     print(trx_status['txid'])
        # else:
        #     print("===============False==================")
        # return jsonify({'success':111})
        dataSend = mongo.db.WithdrawProfits.find_one({'status': 0, "currency": "QTC"})
        if dataSend is not None:
            amount = float(dataSend['amount_coin_satoshi'])/100000000
            address = dataSend['address']
            if dataSend['currency'] == 'QTC':
                # tx_hash = web3_api.transferToken(address, round(amount, 8), dataSend['_id'])
                # print(tx_hash,'===')
                # txid = rpc_connection.sendtoaddress(address, round(amount, 8))
                txid = rpc_connection.sendfrom("admin", address, round(amount, 8))
                print(txid)
                mongo.db.WithdrawProfits.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': txid }})
        return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")
@admin_router.route('/admin/caculator_withdraw', methods=['GET'])
def caculator_withdraw():
    # print({
    #             "i":1,
    #             "a":4
    #         })
    # return jsonify({'success':2})
    dataWithdraw = mongo.db.WithdrawProfits.aggregate(
        [
            {
                '$match' : { 'status': 0, "currency": "QTC" }
            },
            {
            '$group':
                {
                '_id' : "$address",
                'totalAmount': { '$sum': "$amount_coin_satoshi" },
                'count': { '$sum': 1 }
                }
            },
            { '$limit' : 5 }
        ]
    )
    
    i = 0
    for dataSend in dataWithdraw:
        i = i+1
        amount = float(dataSend['totalAmount'])/100000000
        address = dataSend['_id']
        txid = rpc_connection.sendtoaddress(address, round(amount, 8))
        if txid:
            mongo.db.WithdrawProfits.update({'address': dataSend['_id'], 'status': 0}, {'$set': {'status' : 1, 'tx': txid }}, multi=True)
            invoice_idss = mongo.db.PaymentSuccess.insert({
                'coin':'QTC',
                'amount': amount,
                'address': address,
                'txid': txid
            })
            print({
                "i":1,
                "a":4
            })
            print(i, address, amount,txid )
        time.sleep(4)
        # mongo.db.WithdrawProfits.update({'address': dataSend['_id']}, {'$set': {'status' : 1, 'tx': txid }}, multi=True)
    #     if dataSend is not None:
    #         amount = float(dataSend['amount_coin_satoshi'])/100000000
    return jsonify({'success':1})

@admin_router.route('/admin/auto-pay-withdraw-profit-qtc-list', methods=['GET'])
def auto_payment_withdraw_profit_coin_list():
    try:
        dataWithdraw = mongo.db.WithdrawProfits.find({'status': 0, "currency": "QTC"})
        i = 0
        for dataSend in dataWithdraw:
            if dataSend is not None:
                amount = float(dataSend['amount_coin_satoshi'])/100000000
                address = dataSend['address']
                print(amount, address)
                if dataSend['currency'] == 'QTC':
                    # tx_hash = web3_api.transferToken(address, round(amount, 8), dataSend['_id'])
                    # print(tx_hash,'===')
                    txid = rpc_connection.sendtoaddress(address, round(amount, 8))
                    # txid = rpc_connection.sendfrom("admin", address, round(amount, 8))
                    print(txid)
                    if txid:
                        mongo.db.WithdrawProfits.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': txid }})
                        invoice_idss = mongo.db.PaymentSuccess.insert({
                            'coin':'QTC',
                            'amount': amount,
                            'address': address,
                            'txid': txid
                        })
                    i = i + 1
                    print(i)
                time.sleep(4)
                if i == 100 or i == 200 or i == 300 or i == 400 or i == 500 :
                    print("Time_sleepppppppppppp")
                    time.sleep(10)
        return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")
@admin_router.route('/admin/auto-pay-withdraw-profit-trx-list', methods=['GET'])
def auto_payment_withdraw_profit_trx_list():
    try:
        dataWithdraw = mongo.db.WithdrawProfits.find({'status': 0, "currency": "TRX"})
        i = 0
        # tx_ = ClientCoinpayment.get_tx_info(txid="CWEJ2JLKXK4EDN9KZD7GMIHEYX")
        # print(tx_)
        # return jsonify({'success':12})
        for dataSend in dataWithdraw:
            if dataSend is not None:
                amount = float(dataSend['amount_coin_satoshi'])/100000000
                address = dataSend['address']
                currency = dataSend['currency']
                print(amount, address, currency)
                status_withdraw = ClientCoinpayment.create_withdrawal(amount=amount,currency=currency,address=address, auto_confirm = 1) 
                print(status_withdraw,'respon_withdrawrespon_withdraw')
                if status_withdraw['error'] == 'ok':
                    mongo.db.WithdrawProfits.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': status_withdraw['result']['id']}})
                    i=i+1
                    print(i)
                else:
                    break
                time.sleep(3)
                if i == 100 or i == 200 or i == 300 or i == 400 or i == 500:
                    print("Time_sleepppppppppppp")
                    time.sleep(10)
        return jsonify({'success':1})
    except Exception as e:
        print(e)
        logging.exception("An exception was thrown!")
@admin_router.route('/admin/auto-pay-withdraw-profit', methods=['GET'])
def auto_payment_withdraw_profit():
    try:
        # trx_status = tron_api.transferTrx("TTCbSEi55BnDrHF6LJ5YwsRPUXBdGbdtqS", 3.0933)
        # print('trx_status', trx_status['status'])
        # if trx_status['status'] == True:
        #     print(trx_status['txid'])
        # else:
        #     print("===============False==================")
        # return jsonify({'success':111})
        dataSend = mongo.db.WithdrawProfits.find_one({'status': 0, "currency": {"$ne": "QTC"}})
        if dataSend is not None:
            amount = float(dataSend['amount_coin_satoshi'])/100000000
            address = dataSend['address']
            if dataSend['currency'] == 'QTC':
                # tx_hash = web3_api.transferToken(address, round(amount, 8), dataSend['_id'])
                # print(tx_hash,'===')
                # txid = rpc_connection.sendtoaddress(address, round(amount, 8))
                txid = rpc_connection.sendfrom("admin", address, round(amount, 8))
                print(txid)
                mongo.db.WithdrawProfits.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': txid }})
            # elif dataSend['currency'] == "TRX":
            #     trx_status = tron_api.transferTrx(address, round(amount, 4))
            #     print(trx_status)
            #     if trx_status['status'] == True:
            #         mongo.db.WithdrawProfits.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': trx_status['txid'] }})
            else:                    
                currency = "USDT.ERC20" if dataSend['currency'] == "USDT" else dataSend['currency']
                print(amount,currency,address)
                status_withdraw = ClientCoinpayment.create_withdrawal(amount=amount,currency=currency,address=address, auto_confirm = 1) 
                print(status_withdraw,'respon_withdrawrespon_withdraw')
                if status_withdraw['error'] == 'ok':
                    mongo.db.WithdrawProfits.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': status_withdraw['result']['id']}})
        return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")

@admin_router.route('/admin/auto-pay-withdraw', methods=['GET'])
def auto_payment_withdraw():
    try:
        dataSend = mongo.db.Withdraws.find_one({'status': 0})
        if dataSend is not None:
            amount = float(dataSend['amount_coin_satoshi'])/100000000
            address = dataSend['address']
            if dataSend['currency'] == 'QTC' or dataSend['currency'] == 'QTC2' or dataSend['currency'] == 'QTC3' or dataSend['currency'] == 'QTC4':
                # tx_hash = web3_api.transferToken(address, round(amount, 8), dataSend['_id'])
                # print(tx_hash,'===')
                # txid = rpc_connection.sendtoaddress(address, round(amount, 8))
                txid = rpc_connection.sendfrom("admin", address, round(amount, 8))
                print(txid)
                mongo.db.Withdraws.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': txid }})
            # elif dataSend['currency'] == "TRX":
            #     trx_status = tron_api.transferTrx(address, round(amount, 4))
            #     if trx_status['status'] == True:
            #         mongo.db.Withdraws.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': trx_status['txid'] }})
            elif dataSend['currency'] == "USD":
                print(1)
                res = tron_api.send_usdt(address, round(amount, 4))
                if res:
                    mongo.db.Withdraws.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1, 'tx': res }})
            else:                    
                currency = "USDT.ERC20" if dataSend['currency'] == "USDT" else dataSend['currency']
                print(amount,currency,address)
                status_withdraw = ClientCoinpayment.create_withdrawal(amount=amount,currency=currency,address=address, auto_confirm = 1) 
                print(status_withdraw,'respon_withdrawrespon_withdraw')
                if status_withdraw['error'] == 'ok':
                    mongo.db.Withdraws.update({'_id' : dataSend['_id'] },{'$set' : {'status' : 1}})
        return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")

@admin_router.route('/admin/withdraw-all/<currency>')
@login_required
@admin_required
def withdraw_all(currency):
    pipeline = [
        {'$match': { 'currency': currency, 'status': 0 } },
        {
            '$group': {
                '_id': '$address',
                'total': { '$sum': "$amount_coin_satoshi" },
                'amount_coin_satoshi': {'$push': "$amount_coin_satoshi"},
                'withdraw_id': {'$push': '$_id'}
            }
        }
    ]
    query = mongo.db.WithdrawProfits.aggregate(pipeline)
    arr = {
        'wd': {}
    }
    send = []
    withdraw_id = []
    no = 0
    for i in query:
        obj = {}
        no = no + 1
        withdraw_id.append(i['withdraw_id'])
        # for j in i['withdraw_id']:
        #     withdraw_id.append(j)    
            # mongo.db.WithdrawProfits.update(
            #     { '_id': j },
            #     { '$set': { 'status':1 } } 
            # )    
        currency = "USDT.ERC20" if currency == "USDT" else currency
        t_ = 'wd'+str(no)
        t__ = 'wd['+str(t_)+'][amount]'
        print(str(t__))
        arr['wd'][t_] = {}
        arr['wd'][t_]['address'] = i['_id']
        arr['wd'][t_]['amount'] = round(float(i['total'])/100000000, 5)
        arr['wd'][t_]['currency'] = currency
    print(arr)
    try:
        status_withdraw = ClientCoinpayment.create_mass_withdrawal(wd = arr) 
        print(status_withdraw)
    except Exception as e:
        print("Error:===" + str(e))
        return jsonify({'Error':str(e)})
    print(withdraw_id)
    # mongo.db.WithdrawProfits.update(
    #     { '_id': { '$in': withdraw_id } },
    #     { '$set': { 'status':1 } } 
    # )
    return jsonify({'success':arr})
def cb_mass(err, res):
    print(err, res)
@admin_router.route('/admin/cancel-withdraw/<int:id>')
@login_required
@admin_required
def cancel_withdraw(id): 
    count_posts = mongo.db.Posts.count()
    count_estates = mongo.db.Estates.count()
    count_users = mongo.db.Users.count()
    return render_template('admin/pages/admin.html' , count_posts=count_posts,count_estates=count_estates,count_users=count_users )
