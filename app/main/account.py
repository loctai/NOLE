from datetime import datetime,date
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash, json
from flask_login import login_required
from . import main
from app import cache, mongo, rpc_connection
from .forms import ResetPasswordForm, walletAddressForm, Form2FA, KycForm, FormAvatar
import onetimepass
import bcrypt
import os
from app.utils import helpers, web3_api, tron_api
from cloudinary import CloudinaryImage
from cloudinary.uploader import upload_image, upload
from cloudinary.utils import cloudinary_url
salt = b'$2b$07$Kw/qwGlHgmUwSgX4InYrMe'
def get_totp_uri(otp_secret, user):
  return 'otpauth://totp/NOLE:{0}?secret={1}&issuer=NOLE' \
    .format(user['name'], otp_secret)
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)

@main.route('/account/profile', methods=['GET','POST'])
@login_required
def profiles():
    form_2fa = Form2FA()
    form_reset_password = ResetPasswordForm()
    form_wallet = walletAddressForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    url_otp = get_totp_uri(user['security']['two_factor_auth']['code'],user)
    if request.method=="POST":
        print(request.form)
        otp=request.form['code']
        check_otp = mongo.db.Otps.find_one({'user_id': session['user_id'], "code": otp, "status": 0})
        error = False
        if check_otp is None:
            error = True
            flash("Wrong OTP code")
        existing_user = mongo.db.Users.find({'email': request.form['email'].lower() }).count()
        if int(existing_user) >= 5:
            error = True
            flash("Please use another email")
        if error == False:
            mongo.db.Otps.update({"_id": check_otp['_id']}, {"$set":{"status": 1}})
            mongo.db.Users.update( {'_id':user['_id']},{'$set':{"email":request.form['email'].lower()}})
            flash("Update email successfully")
            return redirect('/account/profile')
    return render_template('main/pages/account.html', user=user,
    url_otp=url_otp,
    form_2fa=form_2fa,
    form_reset_password=form_reset_password,form_wallet=form_wallet)

@main.route('/account/reset-password', methods=['GET','POST'])
@login_required
def accountResetPassword():
    form_2fa = Form2FA()
    form_reset_password = ResetPasswordForm()
    form_wallet = walletAddressForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    url_otp = get_totp_uri(user['security']['two_factor_auth']['code'],user)
    if form_reset_password.validate_on_submit():
        if bcrypt.hashpw((request.form['old_password']).encode('utf-8'), salt)  == user['password']:
            hashpass = bcrypt.hashpw((request.form['password']).encode('utf-8'), salt)
            mongo.db.Users.update( {'_id':user['_id']},{'$set':{"password":hashpass}})
            flash('Your Password has been updated.')
        else:
            flash('Current password is incorrect')
        return redirect('/account/profile')
    return render_template('main/pages/account.html', user=user, 
    form_2fa=form_2fa,
    url_otp=url_otp,
    form_reset_password=form_reset_password,form_wallet=form_wallet)

@main.route('/account/update-wallet', methods=['GET','POST'])
@login_required
def accountUpdateWallet():
    form_2fa = Form2FA()
    form_reset_password = ResetPasswordForm()
    form_wallet = walletAddressForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    url_otp = get_totp_uri(user['security']['two_factor_auth']['code'],user)
    if form_wallet.validate_on_submit():
        error = False
        otp=request.form['code']
        check_otp = mongo.db.Otps.find_one({'user_id': session['user_id'], "code": otp, "status": 0})
        if check_otp is None:
            error = True
            flash("Wrong OTP code")
        if(request.form['btc_address']) is not None:
            validate_address_btc = helpers.verify_address(request.form['btc_address'], "btc")
            if validate_address_btc == 0:
                error = True
                flash("Invalid Address BTC")
            else:
                mongo.db.Users.update( {'_id':user['_id']},{'$set':{"wallet.btc_address":request.form['btc_address']}})
        if(request.form['eth_address']) is not None and error == False:
            validate_address_eth = helpers.verify_address(request.form['eth_address'], "eth")
            if validate_address_eth == 0:
                error = True
                flash("Invalid Address ETH")
            else:
                mongo.db.Users.update( {'_id':user['_id']},{'$set':{"wallet.eth_address":request.form['eth_address']}})
        if(request.form['trx_address']) is not None and error == False:
            # validate_address_trx = helpers.verify_address(request.form['trx_address'], "trx")
            check_trx_address = tron_api.isAddress(request.form['trx_address'])
            if check_trx_address == False:
            # if validate_address_trx == 0:
                error = True
                flash("Invalid Address TRX")
            else:
                mongo.db.Users.update( {'_id':user['_id']},{'$set':{"wallet.trx_address":request.form['trx_address']}})
        if(request.form['coin_address']) is not None and error == False:
            # validate_address_qtc = helpers.verify_address(request.form['coin_address'], "qtc")
            verify_address_qtc = rpc_connection.validateaddress(request.form['coin_address'])
            if verify_address_qtc['isvalid'] == False:
                error = True
                flash("Invalid Address QTC")
            else:
                mongo.db.Users.update( {'_id':user['_id']},{'$set':{"wallet.coin_address":request.form['coin_address']}})
        if(request.form['usdt_address']) is not None and error == False:
            validate_address_usdt = helpers.verify_address(request.form['usdt_address'], "eth")
            if validate_address_usdt == 0:
                error = True
                flash("Invalid Address USDT ERC20")
            else:
                mongo.db.Users.update( {'_id':user['_id']},{'$set':{"wallet.usdt_address":request.form['usdt_address']}})
        if error == True:
            return redirect('/account/profile')
        else:
            mongo.db.Otps.update({"_id": check_otp['_id']}, {"$set":{"status": 1}})
            flash('Your Wallet has been updated.')
            return redirect('/account/profile')
    return render_template('main/pages/account.html', user=user, 
    form_2fa=form_2fa,
    url_otp=url_otp,
    form_reset_password=form_reset_password,form_wallet=form_wallet)


@main.route('/account/2FA', methods=['GET','POST'])
@login_required
def update2FA():
    form_2fa = Form2FA()
    form_reset_password = ResetPasswordForm()
    form_wallet = walletAddressForm()
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    url_otp = get_totp_uri(user['security']['two_factor_auth']['code'],user)
    print(request.form)
    if form_2fa.validate_on_submit():
        otp = request.form['otp']
        checkVerifY = verify_totp(otp, user['security']['two_factor_auth']['code'])
        status_2fa = user['security']['two_factor_auth']['status']
        if checkVerifY == False:
            flash('The two-factor authentication code you specified is incorrect. Please check the clock on your authenticator device to verify that it is in sync.')
        else:
            if int(status_2fa) == 0:
                mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { "security.two_factor_auth.status": 1 } })
            else:
                mongo.db.Users.update({ "_id" : session['user_id'] }, { '$set': { "security.two_factor_auth.status": 0 } })
            flash('Your 2FA has been updated.')
            return redirect('/account/profile')
    return render_template('main/pages/account.html', user=user, 
    form_2fa=form_2fa,
    url_otp=url_otp,
    form_reset_password=form_reset_password,form_wallet=form_wallet)

@main.route('/account/kyc', methods=['GET','POST'])
@login_required
def kyc_application():
    form = KycForm()
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "../static", "country-list.json")
    data_country = json.load(open(json_url,  encoding='utf-8'))
    form.country.choices = [(c['country_code'],c['country_name']) for c in data_country]
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    data_kyc = mongo.db.Verifys.find_one({'user_id': session['user_id'], "status": {"$ne": 3}})
    if data_kyc is not None:
        # picture_url = CloudinaryImage('kyc/nfdr1ceelz6xeaapboog.jpg').build_url(
        #     aspect_ratio=0.8,
        #     crop='fill',
        #     gravity='face',
        #     width=512,
        #     dpr='auto'
        # )
        # print(picture_url)
        form.fullname.data = data_kyc['fullname']
        form.passport.data = data_kyc['passport']
        form.gender.data = data_kyc['gender']
        form.country.data=data_kyc['country']
    if form.validate_on_submit():
        check_kyc = mongo.db.Verifys.find_one({'user_id': session['user_id'], "$or":[ {"status":0}, {"status":2}]})
        if check_kyc is None:
            mongo.db.Verifys.update( {'user_id':session['user_id']}, {"$set": {"status": 3}}, multi=True)
            front = request.files['front']
            back = request.files['back']
            selfie = request.files['selfie']
            front_upload=upload_image(front, folder='kyc/')
            front_url=front_upload.url

            back_upload=upload_image(back, folder='kyc/')
            back_url=back_upload.url

            selfie_upload=upload_image(selfie, folder='kyc/')
            selfie_url=selfie_upload.url
            data_verifys = {
                'user_id': user['_id'],
                'username' : user['name'],
                "fullname": request.form['fullname'],
                "country": request.form['country'].upper(),
                "gender": request.form['gender'],
                "passport": request.form['passport'],
                'front' : front_url,
                'back': back_url,
                'selfie' : selfie_url,
                'date_added' : datetime.now(),
                'admin_note' : '',
                'status' : 0
            }
            mongo.db.Verifys.insert(data_verifys)
            flash('Submit document successfully')
            return redirect('/account/kyc')
    return render_template('main/pages/kyc.html', data_kyc=data_kyc, user=user, form=form, data_country=data_country)
def save_cloud(form_picture, image_res = (125, 125)):                                    
    upload_result = upload(form_picture)
    img_url, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=image_res[0], height=image_res[1], secure=True) 
    return img_url
@main.route('/account/upload-avatar', methods=['GET','POST'])
@login_required
def upload_avatr():
    if request.method == "POST":        
        if not request.files.get('avatar', None):
            return redirect('/account/dashboard')
        else:
            avatar = request.files['avatar']
            avatar_url = save_cloud(avatar, image_res=(125, 125))
            # avatar_upload=upload_image(avatar, folder='avatar/')
            # avatar_url=avatar_upload.url
            print(avatar_url)
            mongo.db.Users.update( {'_id': session['user_id']},{"$set": {'avatar': avatar_url}})
            flash('Change avatar successfully')
            return redirect('/account/dashboard')