from flask import json, jsonify, request, url_for, g, abort
from app.cronjobs import bp
from app import mongo
import requests
def send_api_request(url):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.get(url).json()

@bp.route('/auto-tickers', methods=['GET', 'POST'])
def auto_tickers():
    response_btc = send_api_request("https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD")   
    response_eth = send_api_request("https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD")    
    # response_trx = send_api_request("https://min-api.cryptocompare.com/data/price?fsym=TRX&tsyms=USD")
    # response_trx['USD']
    response_trx = send_api_request("https://api.binance.com/api/v1/ticker/price?symbol=TRXUSDT") 
    mongo.db.Tickers.update({},{'$set': {'trx_price': response_trx['price'], 'eth_price': response_eth['USD'],'btc_price' : response_btc['USD']}})
    return json.dumps({'BTC' : response_btc['USD'], 'ETH' : response_eth['USD'], 'TRX': response_trx['price']})

@bp.route('/auto-tickers-price', methods=['GET', 'POST'])
def auto_tickerwewes():
    data = send_api_request("https://adminapp.nole.ai/api/v1/ticker-price")
    mongo.db.Tickers.update({},{'$set': {'trx_price': data['TRX']['price'], 'eth_price': data['ETH']['price'],'btc_price' : data['BTC']['price']}})
    return json.dumps({'BTC' : data['BTC']['price'], 'ETH' : data['ETH']['price'], 'TRX': data['TRX']['price']})