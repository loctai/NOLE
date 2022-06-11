
from flask import Flask, render_template, request, g, session, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
import logging
import threading
import time
import requests
from flask_socketio import SocketIO
# from flask_pymongo import pymongo ,MongoClient
from flask_pymongo import PyMongo
from config import Config
from flask_login import LoginManager,UserMixin
from flask_caching import Cache
from flask_babel import Babel, lazy_gettext as _l, get_locale
from coinpayments import CoinPaymentsAPI
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from .models import User

from app.utils import template_filters, standard_view, web3_api

# client = pymongo.MongoClient("mongodb://127.0.0.1:27017/test")
# mongo= client.test

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins='*')
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

ClientCoinpayment = CoinPaymentsAPI(public_key=app.config['COINPAYMENT_PUBLIC_KEY'],
                          private_key=app.config['COINPAYMENT_PRIVATE_KEY'])

rpc_user = Config().rpc_user
rpc_password = Config().rpc_password
rpc_host = Config().rpc_host
rpc_port = Config().rpc_port
rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpc_user, rpc_password, rpc_host, rpc_port))


bootstrap = Bootstrap(app)
mail = Mail(app)
moment = Moment(app)
cache = Cache(app=app, config={'CACHE_TYPE': 'simple'})   
babel = Babel(app)

from app.assets import compile_main_assets
compile_main_assets(app)

template_filters.init_template_filters(app)
standard_view.init_standard_views(app)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .admin import admin_router as admin_blueprint
app.register_blueprint(admin_blueprint)

from .api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from .cronjobs import bp as jobs_bp
app.register_blueprint(jobs_bp, url_prefix='/jobs')
@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print('An error occured:')
    print(e)
@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200
    else:
        return jsonify({'ip': request.environ['HTTP_X_FORWARDED_FOR']}), 200
    return jsonify(origin=request.headers.get('X-Forwarded-For', request.remote_addr))
@app.route('/lang/<lang>', methods =['GET', 'POST'])
def setLang(lang):
    
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang
    return jsonify({'success': 1}), 200

@login_manager.user_loader
def load_user(user_id):
    users = mongo.db.Users
    user_json = users.find_one({'_id': 'Int32(user_id)' })
    return User(user_json)

@babel.localeselector
def get_locale():
    session['lang'] = app.config['BABEL_DEFAULT_LOCALE']
    return app.config['BABEL_DEFAULT_LOCALE']
    lang = request.path[1:].split('/', 1)[0]
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang
        return lang
    if session.get('lang') is not None and session.get('lang') in app.config['LANGUAGES']:
        return session.get('lang')
    default_lang = request.accept_languages.best_match(app.config['LANGUAGES'])
    if default_lang is None:
        default_lang = app.config['BABEL_DEFAULT_LOCALE']
    session['lang'] = default_lang
    # return default_lang
    return app.config['BABEL_DEFAULT_LOCALE']
@app.before_request
def get_global_language():
    g.locale = str(get_locale())

@app.before_first_request
def setup_db():
    tickers = mongo.db.Tickers
    if not tickers.find_one({}) :
        data_ticker = {
            'btc_price' : 4555,
            'btc_change' : 1.2,
            'trx_price': 0.02,
            'trx_change': 1,
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


# @app.before_first_request
# def activate_job():
#     def run_job():
#         web3_api.filter_loop(mongo)
#         # while True:
#         #     print("Run recurring task")
#         #     time.sleep(5)
#     thread = threading.Thread(target=run_job)
#     thread.start()


# @app.before_first_request
# def do():
#     def run():
#         i = 0
#         while True:
#             i = i + 1
#             time.sleep(3)
#             r = requests.get('http://localhost:5889/admin/auto-pay-withdraw-profit-qtc')
#             time.sleep(2)
#             r = requests.get('http://localhost:5889//admin/auto-pay-withdraw-profit')
#             print("Run recurring task", i)
#     thread = threading.Thread(target=run)
#     thread.start()
def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://127.0.0.1:5889/')
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)
    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()
def create_app(config_filename):
    app = Flask(__name__)
    return app