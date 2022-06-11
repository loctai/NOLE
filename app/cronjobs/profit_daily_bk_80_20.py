from flask import jsonify, request, url_for, g, abort
from app.cronjobs import bp
from app import mongo
from app.utils import helpers
from datetime import datetime,date,timedelta

@bp.route('/jobs-reset-maxout-profitday', methods=['GET'])
def reset_profit_daily():
    mongo.db.Investments.update({}, {'$set': {'profit_daily': 0 }}, multi=True)
    mongo.db.Users.update({}, {'$set': {'balance.receive_today': 0, 'balance.withdraw_usd_today': 0 }}, multi=True)
    mongo.db.Mailinvests.remove({})
    return jsonify({'jobs-reset_profit_daily':'success'})

@bp.route('/jobs-reset-volume-f1', methods=['GET'])
def reset_volume_f1():
    x = datetime.now()
    date_th = x.strftime("%w")
    if int(date_th) == 0:
        mongo.db.Users.update({}, {'$set': {'balance.team_volume_f1': 0 }}, multi=True)
    return jsonify({'jobs-reset-volume-f1':date_th}) 

@bp.route('/jobs-reset-maxout-day', methods=['GET'])
def reset_max_out_day():
    mongo.db.Users.update({}, {'$set': {'balance.receive_today': 0 }}, multi=True)
    return jsonify({'jobs-reset_max_out_day':'success'})

def get_profit(amount):
    dataprofit = mongo.db.Systems.find_one({},{'profit_daily':'1'})
    data = dataprofit['profit_daily'][0]
    percent = 0
    if amount <=500:
        percent = data['level1']
    if amount <= 3000 and amount >= 1000:
        percent = data['level2']
    if amount <=10000 and amount >= 5000:
        percent = data['level3']
    return percent
@bp.route('/jobs-profit-daily', methods=['GET'])
def profit_daily():
    investment = mongo.db.Investments.find({'$and' :[{'status' : 1},{"status_profit": 1, "profit_daily": 0}]} )
    for x in investment:
        amount_usd = int(x['amount_usd'])
        percent = get_profit(amount_usd)
        old_profit_coin = float(x['profit_coin'])
        amount_coin = float(x['amount_coin_satoshi'])
        date_invest = x['createdAt'] + timedelta(days=1)
        date_now = datetime.now()
        # and date_now > date_invest
        if float(percent) > 0 and amount_coin > old_profit_coin and x['currency'] == "TRX":
            user = mongo.db.Users.find_one({'_id' : x['user_id'] })
            commission_usd = round(float(percent)*float(amount_usd)/100, 3)
            commission_coin = round(float(percent)*float(amount_coin)/100, 0)
            commission_80 = float(commission_coin)*0.8
            wallet = '%s_balance' % (x['currency'].lower())
            balance_coin = user['wallet'][wallet]
            new_balance_coin = float(balance_coin) + float(commission_80)
            new_profit_coin = float(x['profit_coin']) + float(commission_coin)

            price_coin = helpers.get_tickers(mongo.db.Tickers, 'coin')
            coin_reward = commission_usd
            coin_reward_20 = float(coin_reward)*20/100
            convert_to_coin = float(coin_reward_20)/float(price_coin)
            convert_to_coin_satoshi = round(float(convert_to_coin)*100000000,0)
            new_balance_coin_reward = float(user['wallet']['coin_balance_profit']) + float(convert_to_coin_satoshi)
            
            wallet_update = 'wallet.%s_balance' % (x['currency'].lower())

            balance_remaining = float(user['balance']['commission_remain'])
            new_balance_remaining = float(balance_remaining) - float(commission_usd)

            mongo.db.Users.update({'_id': user['_id']},{"$set":
                {
                    wallet_update: round(new_balance_coin, 0),
                    "wallet.coin_balance_profit": round(new_balance_coin_reward, 0),
                    # 'balance.commission_remain': round(new_balance_remaining, 2),
                }
            })
            new_percent = float(x['percent'])+ float(percent)
            if new_percent > 300:
                new_percent = 300
            new_status = 1
            if new_percent >= 300 or balance_remaining <= 0:
                new_status = 2
            mongo.db.Investments.update({'_id': x['_id']},{"$set":
                {
                    "count_day": int(x['count_day']) + 1,
                    "percent": round(new_percent, 2),
                    "profit_coin": round(new_profit_coin, 0),
                    "profit_daily" : 1,
                    "status": new_status
                }
            })
            _id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            mongo.db.Transactions.insert({
                '_id': _id,
                "transaction_id": transaction_id,
                'user_id' : user['_id'],
                'amount_usd' : 0,
                "currency": x['currency'],
                "amount_coin": round(commission_80, 0),
                'package': amount_usd,
                'detai' : 'Profit daily package $%s'%(amount_usd),
                'type' : 'Receive',
                'wallet' : 'Daily Profit',
                'price_coin': price_coin,
                'percent': percent,
                "createdAt": datetime.now(),
            })
            _id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
            transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
            mongo.db.Transactions.insert({
                '_id': _id,
                "transaction_id": transaction_id,
                'user_id' : user['_id'],
                'amount_usd' : 0,
                "currency": 'QTC',
                "amount_coin": round(convert_to_coin_satoshi, 0),
                'package': amount_usd,
                'detai' : 'Profit daily package $%s'%(amount_usd),
                'type' : 'Receive',
                'wallet' : 'Daily Profit',
                'percent': percent,
                "createdAt": datetime.now(),
            })
            dataMails = {
                "currency": x['currency'],
                "amount_coin": round(commission_80, 0),
                'amount_qtc': round(convert_to_coin_satoshi, 0),          
                "plan": amount_usd,
                "amount_coin_invest":float(x['amount_coin_satoshi']),
                'user_id' : user['_id'],
                "name": user['name'],
                "email": user['email'],
                "percent": percent,
                "status": 0,
                "createdAt": datetime.now()
            }
            withdraw_id = mongo.db.Mailinvests.insert(dataMails)
            # address_qtc = user['wallet']['coin_address']
            # if address_qtc != "":
            #     fee_qtc = float(convert_to_coin_satoshi)*0.05
            #     amount_qtc = float(convert_to_coin_satoshi)-float(fee_qtc)
            #     __id = helpers.getNextSequence(mongo.db.Counters,"withdrawProfitId")
            #     transaction_id_ = 'T%s' % (helpers.generate_transaction_id(__id))
            #     amount_usd_qtc = float(convert_to_coin)*float(price_coin)
            #     data_withdraw_qtc = {
            #         "_id": __id,
            #         "transaction_id": transaction_id_,
            #         'currency': 'QTC',
            #         'address': address_qtc,
            #         'price': price_coin,
            #         'amount_usd': round(amount_usd_qtc, 2),
            #         'fee_satoshi': round(float(fee_qtc), 0),
            #         'amount_coin_satoshi': round(float(amount_qtc), 0),                
            #         'user_id' : user['_id'],
            #         'tx': "",
            #         "status": 0,
            #         "createdAt": datetime.now()
            #     }
            #     withdraw_id = mongo.db.WithdrawProfits.insert(data_withdraw_qtc)
            print('============================================')
            print(wallet, balance_coin, new_balance_coin)
            print('currency', x['currency'])
            print('amount_usd', amount_usd)
            print('commission_coin', commission_coin)
            print('commission_80', commission_80)
            print('coin_reward', coin_reward)
            print('coin_reward_20', coin_reward_20)
            print("percent", percent)

            #  mongo.db.Investments.update({'_id' : x['_id']},{ '$set' : {'profit_daily' : 1}})
    return jsonify({'jobs-profit-daily':'success'})

@bp.route('/jobs-auto-withdraw-profit', methods=['GET'])
def auto_withdraw_profit_daily():
    data = mongo.db.Users.find({"level": {"$ne": 0}})
    price_btc = helpers.get_tickers(mongo.db.Tickers, 'btc')
    price_eth = helpers.get_tickers(mongo.db.Tickers, 'eth')
    price_trx = helpers.get_tickers(mongo.db.Tickers, 'trx')
    price_usdt = helpers.get_tickers(mongo.db.Tickers, 'usdt')
    price_qtc = helpers.get_tickers(mongo.db.Tickers, 'coin')
    for x in data:
        
        amount_coin = 0
        amount_btc = float(x['wallet']['btc_balance'])
        address_btc = x['wallet']['btc_address']

        amount_eth = float(x['wallet']['eth_balance'])
        address_eth = x['wallet']['eth_address']

        amount_trx = float(x['wallet']['trx_balance'])
        address_trx = x['wallet']['trx_address']

        amount_usdt = float(x['wallet']['usdt_balance'])
        address_usdt = x['wallet']['usdt_address']

        amount_qtc = float(x['wallet']['coin_balance_profit'])
        address_qtc = x['wallet']['coin_address']
        
        if amount_btc > 0 and address_btc != "":
            fee_btc = float(amount_btc)*0.05
            satoshi_to_amount_btc = float(amount_btc)/100000000
            amount_usd_btc = float(price_btc)* satoshi_to_amount_btc
            if float(amount_usd_btc) >= 10:
                satoshi_fee_to_btc = float(fee_btc)/100000000
                amount_btc = float(amount_btc)-float(fee_btc)
                satoshi_to_btc = float(amount_btc)/100000000
                _id = helpers.getNextSequence(mongo.db.Counters,"withdrawProfitId")
                transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                data_withdraw_btc = {
                    "_id": _id,
                    "transaction_id": transaction_id,
                    'currency': 'BTC',
                    'address': address_btc,
                    'price': price_btc,
                    'amount_usd': round(float(price_btc)*float(satoshi_to_btc), 2),
                    'fee_satoshi': round(float(fee_btc), 0),
                    'amount_coin_satoshi': round(float(amount_btc), 0),                
                    'user_id' : x['_id'],
                    'name': x['name'],
                    'tx': "",
                    "status": 0,
                    "createdAt": datetime.now()
                }
                withdraw_id = mongo.db.WithdrawProfits.insert(data_withdraw_btc)
                mongo.db.Users.update({'_id': x['_id']},{"$set": { "wallet.btc_balance": 0 } })
        
        # if amount_eth > 0 and address_eth != "":
        #     fee_eth = float(amount_eth)*0.05
        #     satoshi_fee_to_eth = float(fee_eth)/100000000
        #     amount_eth = float(amount_eth)-float(fee_eth)
        #     satoshi_to_eth = float(amount_eth)/100000000
        #     amount_usd_eth = float(price_eth)* satoshi_to_eth
        #     if float(amount_usd_eth) >= 20:
        #         _id = helpers.getNextSequence(mongo.db.Counters,"withdrawProfitId")
        #         transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
        #         data_withdraw_eth = {
        #             "_id": _id,
        #             "transaction_id": transaction_id,
        #             'currency': 'ETH',
        #             'address': address_eth,
        #             'price': price_eth,
        #             'amount_usd': round(float(price_eth)*float(satoshi_to_eth), 2),
        #             'fee_satoshi': round(float(fee_eth), 0),
        #             'amount_coin_satoshi': round(float(amount_eth), 0),                
        #             'user_id' : x['_id'],
        #             'tx': "",
        #             "status": 0,
        #             "createdAt": datetime.now()
        #         }
        #         withdraw_id = mongo.db.WithdrawProfits.insert(data_withdraw_eth)
        #         mongo.db.Users.update({'_id': x['_id']},{"$set": { "wallet.eth_balance": 0 } })
        
        if amount_trx > 0 and address_trx != "":
            fee_trx = float(amount_trx)*0.05
            satoshi_fee_to_trx = float(fee_trx)/100000000
            amount_trx = float(amount_trx)-float(fee_trx)
            satoshi_to_trx = float(amount_trx)/100000000
            amount_usd_trx = float(price_trx)* satoshi_to_trx
            if float(amount_usd_trx) > 0:
                _id = helpers.getNextSequence(mongo.db.Counters,"withdrawProfitId")
                transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                data_withdraw_trx = {
                    "_id": _id,
                    "transaction_id": transaction_id,
                    'currency': 'TRX',
                    'address': address_trx,
                    'price': price_trx,
                    'amount_usd': round(float(price_trx)*float(satoshi_to_trx), 2),
                    'fee_satoshi': round(float(fee_trx), 0),
                    'amount_coin_satoshi': round(float(amount_trx), 0),                
                    'user_id' : x['_id'],
                    'tx': "",
                    "status": 0,
                    "createdAt": datetime.now()
                }
                withdraw_id = mongo.db.WithdrawProfits.insert(data_withdraw_trx)
                mongo.db.Users.update({'_id': x['_id']},{"$set": { "wallet.trx_balance": 0 } })

        if amount_usdt > 0 and address_usdt != "":
            fee_usdt = float(amount_usdt)*0.05
            satoshi_fee_to_usdt = float(fee_usdt)/100000000
            amount_usdt = float(amount_usdt)-float(fee_usdt)
            satoshi_to_usdt = float(amount_usdt)/100000000
            if float(satoshi_to_usdt)> 0:
                _id = helpers.getNextSequence(mongo.db.Counters,"withdrawProfitId")
                transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                data_withdraw_usdt = {
                    "_id": _id,
                    "transaction_id": transaction_id,
                    'currency': 'USDT',
                    'address': address_usdt,
                    'price': price_usdt,
                    'amount_usd': round(float(price_usdt)*float(satoshi_to_usdt), 2),
                    'fee_satoshi': round(float(fee_usdt), 0),
                    'amount_coin_satoshi': round(float(amount_usdt), 0),                
                    'user_id' : x['_id'],
                    'tx': "",
                    "status": 0,
                    "createdAt": datetime.now()
                }
                withdraw_id = mongo.db.WithdrawProfits.insert(data_withdraw_usdt)
                mongo.db.Users.update({'_id': x['_id']},{"$set": { "wallet.usdt_balance": 0 } })
        if amount_qtc > 0 and address_qtc != "":
            fee_qtc = float(amount_qtc)*0.05
            satoshi_fee_to_qtc = float(fee_qtc)/100000000
            amount_qtc = float(amount_qtc)-float(fee_qtc)
            satoshi_to_qtc = float(amount_qtc)/100000000
            amount_usd_qtc = float(price_qtc)*float(satoshi_to_qtc)
            if amount_usd_qtc > 0:
                _id = helpers.getNextSequence(mongo.db.Counters,"withdrawProfitId")
                transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                data_withdraw_qtc = {
                    "_id": _id,
                    "transaction_id": transaction_id,
                    'currency': 'QTC',
                    'address': address_qtc,
                    'price': price_qtc,
                    'amount_usd': round(amount_usd_qtc, 2),
                    'fee_satoshi': round(float(fee_qtc), 0),
                    'amount_coin_satoshi': round(float(amount_qtc), 0),                
                    'user_id' : x['_id'],
                    'tx': "",
                    "status": 0,
                    "createdAt": datetime.now()
                }
                withdraw_id = mongo.db.WithdrawProfits.insert(data_withdraw_qtc)
                mongo.db.Users.update({'_id': x['_id']},{"$set": { "wallet.coin_balance_profit": 0 } })
    return jsonify({'jobs-auto-withdraw-profit':'success'})


@bp.route('/test',  methods=['GET'])
def createmaswithd():
    data = [
        {
            "_id" : 11,
            "transaction_id" : "T11738116",
            "currency" : "USDT",
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "price" : 1,
            "amount_usd" : 9.5,
            "fee_satoshi" : 50000000,
            "amount_coin_satoshi" : 950000000,
            "user_id" : 1,
            "tx" : "",
            "status" : 0
        },

        {
            "_id" : 10,
            "transaction_id" : "T10212465",
            "currency" : "USDT",
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "price" : 1,
            "amount_usd" : 1663.49,
            "fee_satoshi" : 8755200000,
            "amount_coin_satoshi" : 166348800000,
            "user_id" : 1,
            "tx" : "",
            "status" : 0
        },
        {
            "_id" : 9,
            "transaction_id" : "T91269557",
            "currency" : "ETH",
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "price" : 234.13,
            "amount_usd" : 1442,
            "fee_satoshi" : 32415655,
            "amount_coin_satoshi" : 615897449,
            "user_id" : 1,
            "tx" : "",
            "status" : 0
        },

        {
            "_id" : 8,
            "transaction_id" : "T86051284",
            "currency" : "BTC",
            "address" : "1BCS3J8AotVBfMast1WvGPBtKyR6fSrXfe",
            "price" : 9269.62,
            "amount_usd" : 429.83,
            "fee_satoshi" : 244051,
            "amount_coin_satoshi" : 4636961,
            "user_id" : 1,
            "name" : "qtt",
            "tx" : "",
            "status" : 0
        },

        {
            "_id" : 7,
            "transaction_id" : "T71632948",
            "currency" : "USDT",
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "price" : 1,
            "amount_usd" : 6419.72,
            "fee_satoshi" : 33788000000,
            "amount_coin_satoshi" : 641972000000,
            "user_id" : 1,
            "tx" : "",
            "status" : 0
        },

        {
            "_id" : 6,
            "transaction_id" : "T62647031",
            "currency" : "ETH",
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "price" : 237.85,
            "amount_usd" : 5395.31,
            "fee_satoshi" : 119387810,
            "amount_coin_satoshi" : 2268368385,
            "user_id" : 1,
            "tx" : "",
            "status" : 0
        },
        {
            "_id" : 5,
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "amount_coin_satoshi" : 4560000000,
            "amount_usd" : 45.6,
            "currency" : "USDT",
            "fee_satoshi" : 240000000,
            "price" : 1,
            "status" : 0,
            "transaction_id" : "T52681343",
            "tx" : "",
            "user_id" : 1
        },
        {
            "_id" : 3,
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "amount_coin_satoshi" : 4560000000,
            "amount_usd" : 45.6,
            "currency" : "USDT",
            "fee_satoshi" : 240000000,
            "price" : 1,
            "status" : 0,
            "transaction_id" : "T31805517",
            "tx" : "",
            "user_id" : 1
        },
        {
            "_id" : 2,
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "amount_coin_satoshi" : 4560000000,
            "amount_usd" : 45.6,
            "currency" : "USDT",
            "fee_satoshi" : 240000000,
            "price" : 1,
            "status" : 0,
            "transaction_id" : "T21710674",
            "tx" : "",
            "user_id" : 1
        },
        {
            "_id" : 1,
            "address" : "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF",
            "amount_coin_satoshi" : 4560000000,
            "amount_usd" : 45.6,
            "currency" : "USDT",
            "fee_satoshi" : 240000000,
            "price" : 1,
            "status" : 0,
            "transaction_id" : "T11753729",
            "tx" : "",
            "user_id" : 1
        }
    ]
    # print(data)
    new_data = []
    for x in data:
        x['sum'] = 0
        for y in data:
            if x['address'] == y['address'] and x['currency'] == y['currency']:
                print(x)
                x['sum'] = float(x['amount_coin_satoshi'])+float(y['amount_coin_satoshi'])
                new_data.append(x)
            else:
                new_data.append(x)
    print(new_data)
    # newlist = [[y[0] for y in list if y[1]==x] for x in values]
    # print(newlist)
    return jsonify({'success':1})