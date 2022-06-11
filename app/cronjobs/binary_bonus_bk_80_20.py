from flask import jsonify, request, url_for, g, abort
from app.cronjobs import bp
from app import mongo
from app.utils import helpers
from datetime import datetime,date,timedelta

def get_percent(level):
    percent = 0
    if float(level) <= 3 and float(level) > 0:
        percent = 5
    if float(level) >= 4:
        percent = 8
    return percent
def get_id_tree(ids):
    listId = ''
    query = mongo.db.Users.find({'p_binary': int(ids)})
    for x in query:
        listId += ',%s'%(x['_id'])
        listId += get_id_tree(x['_id'])
    return listId
def total_binary_right(customer_id):
    customer =mongo.db.Users.find_one({'_id': customer_id})
    arrright = []
    if customer['right'] != 0:
        id_right_all = str(customer['right'])+get_id_tree(customer['right'])
        id_right_all = id_right_all.split(',')
        arrright  = id_right_all
    return arrright
def total_binary_left(customer_id):
    customer =mongo.db.Users.find_one({'_id': customer_id})
    arrleft = []
    if customer['left'] != 0:
        id_left_all = str(customer['left'])+get_id_tree(customer['left'])
        id_left_all = id_left_all.split(',')
        arrleft  = id_left_all
    return arrleft
def checkF1LeftRight(_id):
    userF1 =  mongo.db.Users.find({'p_node': _id},{'_id': '1'})
    f1_left = False
    f1_right = False

    user_left = total_binary_left(_id)
    user_right = total_binary_right(_id)
    if(userF1.count() > 0):
        for x in userF1:
            if str(x['_id']) in user_left:
                f1_left=True
            if str(x['_id']) in user_right:
                f1_right = True
    data = {"f1_left": f1_left, "f1_right": f1_right}
    return data


@bp.route('/jobs-binary-bonus', methods=['GET'])
def binary_bonus():
    user = mongo.db.Users.find({'$and': [{'balance.team_left':{'$gt': 0 }}, {'balance.team_right':{'$gt': 0 }}]})
    if user.count() > 0:
        for x in user:
            check_f1_left_right = checkF1LeftRight(x['_id'])
            print(x['name'], check_f1_left_right)
            if check_f1_left_right['f1_left'] == True and check_f1_left_right['f1_right'] == True:
                print(x['name'])
                if float(x['balance']['team_left']) > float(x['balance']['team_right']):
                    balanced = x['balance']['team_right']
                    pd_left = float(x['balance']['team_left'])-float(x['balance']['team_right'])
                    mongo.db.Users.update({ "_id" : x['_id'] }, { '$set': { "balance.team_left": pd_left } })
                    mongo.db.Users.update({ "_id" : x['_id'] }, { '$set': { "balance.team_right": 0 } })
                else:
                    balanced = x['balance']['team_left']
                    pd_right = float(x['balance']['team_right'])-float(x['balance']['team_left'])
                    mongo.db.Users.update({ "_id" : x['_id'] }, { '$set': { "balance.team_left": 0 } })
                    mongo.db.Users.update({ "_id" : x['_id'] }, { '$set': { "balance.team_right": pd_right } })
                percent = get_percent(x['level'])
                if float(percent) > 0:
                    commission = float(balanced)*float(percent)/100
                    # if float(commission) > float(x['balance']['max_out_day']) - float(x['balance']['receive_today']):
                    #     amount_receve = float(x['balance']['max_out_day']) - float(x['balance']['receive_today'])
                    # else:
                    #     amount_receve = commission
                    amount_receve = commission
                    new_receive_today = float(amount_receve) + float(x['balance']['receive_today'])

                    balance_remaining = float(x['balance']['commission_remain'])
                    new_balance_remaining = float(balance_remaining) - float(commission)
                    if float(amount_receve) > float(balance_remaining):
                        amount_receve = float(balance_remaining)
                        new_balance_remaining = 0
                    print(amount_receve)
                    if float(amount_receve) > 0:
                        commission_80 = float(amount_receve)*0.8
                        commission_20 = float(amount_receve) *0.2
                        price_coin = helpers.get_tickers(mongo.db.Tickers, 'coin')
                        convert_to_coin = float(commission_20)/float(price_coin)
                        convert_to_coin_satoshi = round(float(convert_to_coin)*100000000,0)
                        new_balance_coin_reward = float(x['wallet']['coin_balance']) + float(convert_to_coin_satoshi)

                        balance_usd = round(float(x['balance']['balance_usd']) + float(commission_80), 2)
                        balance_binary_commission = float(x['balance']['commission_binary'])+float(amount_receve)
                        mongo.db.Users.update({'_id': x['_id']},{"$set": {
                            'balance.balance_usd': round(balance_usd,2),
                            "wallet.coin_balance": round(new_balance_coin_reward, 0),
                            'balance.commission_binary': round(balance_binary_commission,2),
                            'balance.commission_remain': round(new_balance_remaining, 2),
                            'balance.receive_today': round(new_receive_today,2)
                        }})
                        _id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
                        transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                        mongo.db.Transactions.insert({
                            '_id': _id,
                            "transaction_id": transaction_id,
                            'user_id' : x['_id'],
                            'amount_binary': balanced,
                            'amount_usd' : commission_80,
                            "currency": "USD",
                            'detai' : 'Binary bonus',
                            'type' : 'Receive',
                            'wallet' : 'Binary Bonus',
                            'percent': percent,
                            "createdAt": datetime.now(),
                        })
                        __id = helpers.getNextSequence(mongo.db.Counters,"transactionId")
                        transaction_id_ = 'T%s' % (helpers.generate_transaction_id(__id))
                        mongo.db.Transactions.insert({
                            '_id': __id,
                            "transaction_id": transaction_id_,
                            'user_id' : x['_id'],
                            'amount_usd' : commission_20,
                            'amount_binary': balanced,
                            "currency": 'QTC',
                            "amount_coin": round(convert_to_coin_satoshi, 0),                           
                            'detai' : 'Binary bonus',
                            'type' : 'Receive',
                            'wallet' : 'Binary Bonus',
                            'percent': percent,
                            "createdAt": datetime.now(),
                        })
                        CommissionIncome(x['_id'], amount_receve)
    # print('============================================')
    # print(wallet, balance_coin, new_balance_coin)
    # print('currency', x['currency'])
    # print('amount_usd', amount_usd)
    # print('commission_coin', commission_coin)
    # print('commission_80', commission_80)
    # print('coin_reward', coin_reward)
    # print('coin_reward_20', coin_reward_20)
    # print("percent", percent)

            #  mongo.db.Investments.update({'_id' : x['_id']},{ '$set' : {'profit_daily' : 1}})
    return jsonify({'jobs-binary-bonus':user.count()})

def CommissionIncome(user_id, amount):
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
        countF1Level2 = users.find({'p_node': customer_ml_p_node['_id'], 'level': {'$gte':3}}).count()
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