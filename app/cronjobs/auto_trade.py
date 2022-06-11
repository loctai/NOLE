from flask import jsonify, request, url_for, g, abort, json
from app.cronjobs import bp
from app import mongo
from app.utils import helpers
from datetime import datetime,date,timedelta
import time
import random
import string
import uuid
from flask_socketio import disconnect, emit
from app import socketio
from threading import Thread, Event
thread = Thread()
thread_stop_event = Event()

def id_generator_code(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def SaveTrade(types,amount, currency, qty, profit, exchange, transactionID):
    data = {
        'type': types,
        'amount' : amount,
        'currency': currency,
        'qty': qty,
        'profit':  profit,
        'exchange': exchange,
        'transactionID': transactionID,
        'date_added' : datetime.now(),
        'status': 0
    }
    mongo.db.trades.insert(data)
def generate_id():
    uid = uuid.uuid4()
    _id = str(uid.fields[-1])[:8]
    new_id = str(_id)
    return str(new_id)[0:8]
@bp.route('/trade', methods=['GET', 'POST'])
def SaveTrades():

    i_array = [1,2,3,4,5]
    time_array = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    i = 0
    while i < int(random.choice(i_array)):
        time.sleep( random.choice(time_array) )

        types_array = ['buy','sell']
        currency_array = ['BNB','REP','ZEC','BCH','BTC','ETH','LTC','BAT', 'TRX']
        types_profit = [0,round(random.uniform(1,5),2),]
        exhchange_array = ['Dcoin','HitBTC','Iquant','CHAOEX','IDCM','DigiFinex','Binance','LATOKEN','EXX','HitBTC','Gate.io','Coinall','BitMart','Huobi','DOBI Exchange','Bittrex','RightBTC','Bitrabbit','CoinBene','OKEx','IDAX','LocalTrade','BCEX','CoinTiger','55 Global Markets','LATOKEN','ABCC','P2PB2B','Tidebit']

        currency = random.choice(currency_array)

        if currency == 'BTC' or currency == 'ETH':
            qty = round(random.uniform(0,1),8)
        else:
            qty = round(random.uniform(0,800),8)

        SaveTrade(
            random.choice(types_array), 
            round(random.uniform(1000,8000),2),
            currency, 
            qty, 
            random.choice(types_profit),
            random.choice(exhchange_array),
            generate_id()
        )
        i +=1
        print(i)
    return jsonify({'status' : 'success'})
def randomTrading():
    print("Making Jobs")
    i_array = [1,2,3,4,5]
    time_array = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    i = 0
    _cls = "even"
    while not thread_stop_event.isSet():
        _cls = "even" if i % 2 == 0 else "odd"    
        types_array = ['buy','sell']
        currency_array = ['BNB','REP','ZEC','BCH','BTC','ETH','LTC','BAT', 'TRX']
        types_profit = [0,round(random.uniform(1,5),2),]
        exhchange_array = ['Dcoin','HitBTC','Iquant','CHAOEX','IDCM','DigiFinex','Binance','LATOKEN','EXX','HitBTC','Gate.io','Coinall','BitMart','Huobi','DOBI Exchange','Bittrex','RightBTC','Bitrabbit','CoinBene','OKEx','LocalTrade','BCEX','CoinTiger','LATOKEN','ABCC','P2PB2B','Tidebit']
        currency = random.choice(currency_array)
        qty = round(random.uniform(30,800),5)
        if currency == "BTC":
            qty = round(random.uniform(0,0.5),5)
        if currency == "ETH":
            qty = round(random.uniform(0,0.9),5)
        if currency == "REP":
            qty = round(random.uniform(0.5,30),5)
        if currency == "ZEC" or currency == "LTC":
            qty = round(random.uniform(0.5,7),5)
        if currency == "BNB":
            qty = round(random.uniform(1,7),5)
        if currency == "BCH":
            qty = round(random.uniform(0.1,2),5)
        if currency == "BAT":
            qty = round(random.uniform(30,800),5)
        if currency == "TRX":
            qty = round(random.uniform(30,800),5)
        data = {
            "_cls": _cls,
            'type': random.choice(types_array), 
            'amount' :round(random.uniform(1000,8000),2),
            'currency':currency, 
            'qty': qty, 
            'profit': random.choice(types_profit),
            'exchange':random.choice(exhchange_array),
            'transactionID': generate_id(),
            'date_added' : format_date_time(datetime.now()),
            'status': 0
        }
        socketio.emit('@TRADING_BOT', json.dumps(data))
        socketio.sleep( 3 )
        i +=1
        print(i)

@socketio.on('@TRADING_BOT')
def on_connect(msg):
    global thread
    print('Client connected')
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomTrading)

@socketio.on('disconnect')
def on_disconnect():
    # thread_stop_event.set()
    # disconnect()
    print('Client disconnected')
    
def format_date_time(value):
    return value.strftime("%m-%d-%Y %H:%M")
