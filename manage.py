#Launch Script
import os
from app import app, mongo
from flask_script import Manager,Shell, Server
manager = Manager(app)
@manager.command
def setup_db():
    tickers = mongo.db.Tickers
    if not tickers.find_one({}) :
        data_ticker = {
            'btc_price' : 4555,
            'btc_change' : 1.2,
            'eth_price': 160,
            'eth_change': 0.5,
            'usdt_price': 1,
            'usdt_change': 0.1,
            'coin_price': 0.1,
            'coin_change': 0.2
        }
        tickers.insert_one(data_ticker)
    systems = mongo.db.Systems
    if not systems.find_one({}) :
        data_profit = {
            'profit_daily' : [            
            ]
        }
        systems.insert_one(data_profit)
    print(True)

@manager.command
def runserver():
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=os.environ.get('PORT', '5000'),
            debug=True)
if __name__ == '__main__':
    manager.run()