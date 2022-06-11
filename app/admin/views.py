from datetime import datetime,date
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash, jsonify, send_file, make_response
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
from app.utils import helpers
from bson.objectid import ObjectId
import logging
import bcrypt
# mongodb database connection
from app import mongo, ClientCoinpayment
salt = b'$2b$07$Kw/qwGlHgmUwSgX4InYrMe'
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
def delete(collection,uniqueid):
    return collection.remove({'_id': uniqueid})

@admin_router.route('/generate-password/<passw>', methods=['GET','POST'])
def accountResetPasswpassord(passw):
    hashpass = bcrypt.hashpw((passw).encode('utf-8'), salt)
    print(hashpass)
    return jsonify({'hashpass':str(hashpass)})

@admin_router.route('/admin-management-page')
@login_required
@admin_required
def admin(): 
    count_posts = mongo.db.Posts.count()
    count_estates = mongo.db.Estates.count()
    count_users = mongo.db.Users.count()
    count_investment = mongo.db.Investments.count()
    count_withdraw = mongo.db.Withdraws.count()
    count_profit_Withdraw = mongo.db.WithdrawProfits.count()
    balances = ClientCoinpayment.balances()
    total_withdraw_profit = mongo.db.WithdrawProfits.aggregate([
    {
            '$match': {
                "status":1
            }
        },
        {
        '$group': {
            '_id': '$currency',
            'count': { '$sum': 1 },
            'totalMoneySpent': { '$sum': '$amount_coin_satoshi' },
        },
        },
    ])
    for i in total_withdraw_profit:
        print(i)
    balances_usdt = '0'
    balances_eth = '0'
    balances_btc = "0"
    balances_trx = "0"
    if len(balances['result']) > 0:
        print("ETH" in balances['result'])
        if "ETH" in balances['result']:
            balances_eth = balances['result']['ETH']['balancef']
        if "TRX" in balances['result']:
            balances_trx = balances['result']['TRX']['balancef']
        if "USDT.ERC20" in balances['result']:
            balances_usdt = balances['result']['USDT.ERC20']['balancef']
        if "BTC" in balances['result']:
            balances_btc = balances['result']['BTC']['balancef']

    return render_template('admin/pages/admin.html' , 
        count_posts=count_posts,
        count_investment=count_investment,
        count_withdraw=count_withdraw,
        count_profit_Withdraw=count_profit_Withdraw,
        count_estates=count_estates,
        count_users=count_users,
        balances_eth=balances_eth,
        balances_trx=balances_trx,
        balances_btc=balances_btc,
        balances_usdt=balances_usdt
    )


@admin_router.route('/admin-management-page/properties' ,methods=['GET' , 'POST'])
@login_required
@admin_required
def admin_properties():
    propertyList =[]
    query = mongo.db.Estates.find({},{"_id":"1" ,"Title":"1", "Category":"1","Price":"1" ,"Address":"1","Date": "1","Author" : "1"})
    for i in query:
            _id = i['_id']
            authorName=i['Author']
            title = i['Title']
            category = i['Category'] 
            address = i['Address']
            price = i['Price']
            date = i['Date']
            propertyList.append([_id,title, category ,address , price , date,authorName])

    form2 = PropertyForm()
    if form2.validate_on_submit():
        photo_file = {}
        photo_filenames=[]
        photo = request.files['images']
        for photo in form2.images.data:
            if photo:
                photo_upload=upload_image(photo, folder='properties/')
                photo_url=photo_upload.url
            photo_file = {
                'photo': photo_url
            }
            photo_filenames.append(photo_file)
        query1 = mongo.db.Users.find({'email': session['email'] },{'username': '1'})
        for i in query1:
            author=i['username']
        mongo.db.Estates.insert({ '_id': helpers.getNextSequence(mongo.db.Counters,"estateId"),'Author':author , 'Title' : request.form['title'], 'Category' : request.form['category'] ,'Address': request.form['address'],'Price': int(request.form['price']),'Body': request.form['body'],'Photos': photo_filenames ,'Date' : datetime.now()})
        return redirect(url_for('admin.properties'))
    return render_template('admin/pages/admin-properties.html', form2=form2, propertyList=propertyList )





@admin_router.route('/admin-management-page/posts' ,methods=['GET' , 'POST'])
@login_required
@admin_required
def admin_posts():
    postsList =[]
    query = mongo.db.Posts.find({},{"_id": "1" , "Title": "1" , "Date" : "1"})
    for  i in query:
        _id = i['_id']
        title = i['Title']
        date = i['Date']
        postsList.append([_id ,title , date ])
    form2 = PostForm()
    if form2.validate_on_submit(): 
        photo_filename =request.files['image']
        if photo_filename:
            photo_upload=upload_image(photo_filename , folder='posts/')
            photo_url=photo_upload.url
            
        mongo.db.Posts.insert({ '_id': helpers.getNextSequence(mongo.db.Counters,"postId"),'Title' : request.form['title'], 'Slug': request.form['slug'], 'Summary' : request.form['summary'] ,'Body': request.form['body'],'Image_url': photo_url , 'Date': datetime.now()})
        return redirect('/admin-management-page/posts')
    return render_template('admin/pages/admin-posts.html',form2=form2, postsList=postsList  )



@admin_router.route('/admin-management-page/users' , methods=['GET', 'POST'])
@login_required
@admin_required
def admin_users():
    usersList=[]
    query = mongo.db.Users.find({}).sort("_id" ,-1)
    
    return render_template('admin/pages/admin-users.html' ,usersList=query  )
@admin_router.route('/admin-management-page/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    query = mongo.db.Users.find({'_id' : id})
    for i in query:
        oldId = i['_id']
        oldPassword = i['password']
        oldEmail = i['email']
        oldUsername = i['username']
        oldName = i['name']
        date = i['createdAt']

    form = EditProfileAdminForm( )
    if form.validate_on_submit():
        mongo.db.Users.update( {'_id':id},{
            "$set": {
                'email' : request.form['email'],
                'updatedAt': datetime.now()
            }
        })
        flash('The profile has been updated.')
        return redirect('/admin-management-page/users')
    form.email.data = oldEmail
    form.username.data = oldUsername
    form.name.data = oldName
    return render_template('admin/pages/edit_profile.html', form=form)

@admin_router.route('/admin-management-page/user_delete/<int:id>', methods=[ 'GET','POST'])
@login_required
@admin_required
def delete_user (id):
    query = mongo.db.Users.find({'_id': id},{'email': '1'})
    for i in query:
        delete_email = i['email']
    if session['email'] == delete_email:
        flash('Warning: You Can Not  Delete Current User!')
        return redirect('/admin-management-page/users')
    else:
        delete_query=delete(mongo.db.Users, uniqueid=id)

    return redirect('/admin-management-page/users')

@admin_router.route('/admin-management-page/property_edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_property (id):
    query = mongo.db.Estates.find({'_id' : id }, {"Author" : "1", "Title":"1", "Category":"1","Price":"1" ,"Address":"1", "Body" :"1", "Photos": "1" ,"Date": "1"})

    for i in query:
        oldAuthor = i['Author']
        oldTitle = i['Title'] 
        oldCategory = i['Category'] 
        oldPrice = i['Price']
        oldAddress = i['Address']
        oldBody = i['Body']
        oldPhotos =i['Photos']
        date = i['Date']

    form = PropertyForm()
    if form.validate_on_submit():
        photo_file = {}
        photo_filenames=[]
        try:
            photo = request.files['images']
            for photo in form.images.data:
                if photo:
                    photo_upload=upload_image(photo, folder='properties/')
                    photo_url=photo_upload.url
                photo_file = {
                    'photo': photo_url
                }
                photo_filenames.append(photo_file)
                photos = photo_filenames
        except:
            photos = oldPhotos
        query1 = mongo.db.Users.find({'email': session['email'] },{'username': '1'})
        for i in query1:
            author=i['username']
        mongo.db.Estates.update({'_id': id},{
            'Author': author,
            'Title': request.form['title']  , 
            'Category' : request.form['category'],
             'Address' : request.form['address'] ,
             'Price': request.form['price'], 
             'Body' : request.form['body'], 
             'Photos': photos ,
             'Date' : date, 
             'Edit-Date': datetime.now() })
        flash('The property has been updated.')
        return redirect('/admin-management-page/properties')
    form.title.data = oldTitle
    form.price.data = oldPrice
    form.address.data = oldAddress
    form.body.data = oldBody
    return render_template('admin/pages/edit_property.html', form=form)

@admin_router.route('/admin-management-page/property_delete/<int:id>', methods=[ 'GET','POST'])
@login_required
@admin_required
def delete_property (id):
    delete_query=delete(mongo.db.Estates, uniqueid=id)
    flash('The property has been deleted.')
    return redirect(url_for('.admin_properties'))



@admin_router.route('/admin-management-page/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    query =mongo.db.Posts.find({'_id': id})

    for  i in query:
        oldSlug = i['Slug']
        oldTitle = i['Title']
        oldSummary = i['Summary']
        oldBody = i['Body']
        date = i['Date']
    form = PostForm()
    if form.validate_on_submit():
        photo_filename =request.files['image']
        if photo_filename:
            photo_upload=upload_image(photo_filename , folder='postsgit /')
            photo_url=photo_upload.url
        mongo.db.Posts.update({'_id':id},{'Slug': request.form['slug'], 'Title' : request.form['title'], 'Summary' : request.form['summary'], 'Body' : request.form['body'] ,'Image_url': photo_url, 'Date': date ,'Edit-Date': datetime.now()})
        flash('The post has been updated.')
        return redirect('/admin-management-page/posts')
    form.title.data = oldTitle
    form.summary.data = oldSummary
    form.body.data = oldBody
    form.slug.data = oldSlug
    return render_template('admin/pages/edit_post.html', form=form)

@admin_router.route('/admin-management-page/post_delete/<int:id>', methods=[ 'GET','POST'])
@login_required
@admin_required
def delete_post (id):
    delete_query=delete(mongo.db.Posts, uniqueid=id)
    flash('The post has been deleted.')
    return redirect(url_for('.admin_posts'))


@admin_router.route('/admin-management-page/update-profit', methods=[ 'GET','POST'])
@login_required
@admin_required
def update_profit ():
    form = ProfitForm()
    query =mongo.db.Systems.find_one({},{ "profit_daily": "1", })
    if form.validate_on_submit():
        print(request.form)
        _id = helpers.getNextSequence(mongo.db.Counters,"systemId")
        mongo.db.Systems.update({} , {"$push": {'profit_daily': { '$each': [{
                '_id': _id,
                "user_admin": session['user_id'],
                'Date': datetime.now(),
                "level1": request.form['level1'],
                "level2": request.form['level2'],
                "level3": request.form['level3'],
            }], '$position': 0  } }    } )
        # mongo.db.Systems.update({},{"$push": {
        #     "profit_daily": {
        #         '_id': _id,
        #         'Date': datetime.now(),
        #         "level1": request.form['level1'],
        #         "level2": request.form['level2'],
        #         "level3": request.form['level3'],
        #     }
        # }})
        flash('The profit update success.')
        return redirect('/admin-management-page/update-profit')
    return render_template('admin/pages/admin_profit.html', form=form, data=query['profit_daily'])

@admin_router.route('/admin-management-page/investments', methods=[ 'GET','POST'])
@login_required
@admin_required
def admin_investments ():
    pipeline = [
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "total_day":1,
                "count_day":1,
                "status":1,
                "percent": 1,
                "name": "$customer.name"
            }
        },
        { '$sort':  {'_id': -1}},
        {
            "$unwind": "$name"
        }
    ]
    query = mongo.db.Investments.aggregate(pipeline)
    return render_template('admin/pages/investments.html', query=query)


@admin_router.route('/admin-management-page/withdraw', methods=[ 'GET','POST'])
@login_required
@admin_required
def admin_withdraws ():
    pipeline = [
        {
            "$match": {
                "status": 0
            }  
        },
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "_id": 1,
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "address":1,
                "status":1,
                "name": "$customer.name"
            }
        },
        { '$sort':  {'_id': -1}},
        {
            "$unwind": "$name"
        }
    ]
    query = mongo.db.Withdraws.aggregate(pipeline)
    return render_template('admin/pages/withdraw.html', query=query)

@admin_router.route('/admin-management-page/withdraw-success', methods=[ 'GET','POST'])
@login_required
@admin_required
def admin_withdraws_success ():
    pipeline = [
        {
            "$match": {
                "status": 1
            }  
        },
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "_id": 1,
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "address":1,
                "status":1,
                "name": "$customer.name"
            }
        },
        { '$sort':  {'_id': -1}},
        {
            "$unwind": "$name"
        }
    ]
    query = mongo.db.Withdraws.aggregate(pipeline)
    return render_template('admin/pages/withdraw.html', query=query)

@admin_router.route('/admin-management-page/withdraw-profit', methods=[ 'GET','POST'])
@login_required
@admin_required
def admin_withdraws_profit ():
    pipeline = [
        {
            "$match": {
                "status": 0
            }  
        },
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "_id": 1,
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "address":1,
                "status":1,
                "name": "$customer.name"
            }
        },
        { '$sort':  {'_id': -1}},
        {
            "$unwind": "$name"
        }
    ]
    query = mongo.db.WithdrawProfits.aggregate(pipeline)
    return render_template('admin/pages/withdraw_profit.html', query=query)

@admin_router.route('/admin-management-page/withdraw-profit-success', methods=[ 'GET','POST'])
@login_required
@admin_required
def admin_withdraws_profit_success():
    pipeline = [
        {
            "$match": {
                "status": 1
            }  
        },
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "_id": 1,
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "address":1,
                "status":1,
                "name": "$customer.name"
            }
        },
        { '$sort':  {'_id': -1}},
        {
            "$unwind": "$name"
        }
    ]
    # query = mongo.db.WithdrawProfits.aggregate(pipeline)
    total_withdraw_profit = mongo.db.WithdrawProfits.aggregate([
    {
            '$match': {
                "status":1
            }
        },
        {
        '$group': {
            '_id': '$currency',
            'count': { '$sum': 1 },
            'totalMoneySpent': { '$sum': '$amount_coin_satoshi' },
        },
        },
    ])
    totalQTC = 0
    totalTRX = 0
    for i in total_withdraw_profit:
        if i['_id'] == "QTC":
            totalQTC = i['totalMoneySpent']
        else:
            totalTRX = i['totalMoneySpent']
        print(i)
    return render_template('admin/pages/withdraw-profit-success.html', totalQTC=totalQTC, totalTRX=totalTRX)

@admin_router.route('/admin-management-page/get-profit-withdraw-success', methods=[ 'GET','POST'])
@login_required
@admin_required
def admin_get_withdraws_profit_success():
    length = request.args.get('length')
    start = request.args.get('start')
    print(length, start)
    count_profit_Withdraw = mongo.db.WithdrawProfits.count()
    pipeline = [
        {
            "$match": {
                "status": 1
            }  
        },
        
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "_id": 1,
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "address":1,
                "status":1,
                "name": "$customer.name"
            }
        },
        
        { '$sort':  {'_id': -1}},
        { "$skip" : int(start) },
        { "$limit" : int(length) },         
        {
            "$unwind": "$name"
        }
        
    ]
    query = mongo.db.WithdrawProfits.aggregate(pipeline)
    data_send = []
    for x in query:
        x['amount_coin_satoshi'] = helpers.format_satoshi(x['amount_coin_satoshi'])
        x['createdAt'] = x['createdAt'].strftime("%b, %d %Y %H:%M")
        data_send.append(x)
    return jsonify({'data':data_send, 'recordsFiltered': count_profit_Withdraw, 'recordsTotal': count_profit_Withdraw })
import pandas
@admin_router.route('/admin-management-page/export-withdraw-profit-success', methods=[ 'GET','POST'])
@login_required
@admin_required
def admin_get_withewedraws_profit_success():
    # length = request.args.get('length')
    # start = request.args.get('start')
    # print(length, start)
    start = request.args.get('start')
    end = request.args.get('end')
    start=start.split('-')
    start = datetime(year=int(start[2]),month=int(start[1]),day=int(start[0]))
    end=end.split('-')
    end = datetime(year=int(end[2]),month=int(end[1]),day=int(end[0]))

    
    print(start, end)

    # start = datetime(2014, 9, 24, 7, 51, 04)
    # end = datetime(2014, 9, 24, 7, 52, 04)
    count_profit_Withdraw = mongo.db.WithdrawProfits.count()
    pipeline = [
        {
            "$match": {
                "status": 1,
                'createdAt': {'$lt': end, '$gte': start}
            }  
        },
        
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "_id": 1,
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "address":1,
                "status":1,
                "name": "$customer.name"
            }
        },
        
        { '$sort':  {'_id': -1}},
        # { "$skip" : int(start) },
        # { "$limit" : 70 },         
        {
            "$unwind": "$name"
        }
        
    ]
    query = mongo.db.WithdrawProfits.aggregate(pipeline)
    mongo_docs = list(query)
    docs = pandas.DataFrame(columns=[])
    for num, doc in enumerate(mongo_docs):
        del doc['status']
        doc["_id"] = str(doc["_id"])
        doc_id = doc["_id"]
        doc['amount_coin_satoshi'] = float(doc['amount_coin_satoshi'])/100000000
        series_obj = pandas.Series( doc, name=doc_id )
        docs = docs.append(series_obj)
    docs.to_csv("nole_withdraw_profit.csv", ",")
    csv_export = docs.to_csv(sep=",")
    resp = make_response(csv_export)
    resp.headers["Content-Disposition"] = "attachment; filename=nole_withdraw_profit.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

@admin_router.route('/admin-management-page/get-sum-withdraw', methods=[ 'GET','POST'])
@login_required
@admin_required
def get_sum_withdraw():
    # length = request.args.get('length')
    # start = request.args.get('start')
    # print(length, start)
    start = request.args.get('start')
    end = request.args.get('end')
    start=start.split('-')
    start = datetime(year=int(start[2]),month=int(start[1]),day=int(start[0]))
    end=end.split('-')
    end = datetime(year=int(end[2]),month=int(end[1]),day=int(end[0]))

    
    print(start, end)

    # start = datetime(2014, 9, 24, 7, 51, 04)
    # end = datetime(2014, 9, 24, 7, 52, 04)
    count_profit_Withdraw = mongo.db.WithdrawProfits.count()
    pipeline = [
        {
            "$match": {
                "status": 1,
                'createdAt': {'$lt': end, '$gte': start}
            }  
        },
        
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$project": {
                "_id": 1,
                "amount_usd": 1,
                "amount_coin_satoshi": 1,
                "currency":1,
                "createdAt":1,
                "address":1,
                "status":1,
                "name": "$customer.name"
            }
        },
        
        { '$sort':  {'_id': -1}},
        # { "$skip" : int(start) },
        # { "$limit" : 70 },         
        {
            "$unwind": "$name"
        }
        
    ]
    query = mongo.db.WithdrawProfits.aggregate(pipeline)
    mongo_docs = list(query)
    total_qtc = 0
    total_trx = 0
    for num, doc in enumerate(mongo_docs):
        if doc['currency'] == 'QTC':
            total_qtc = total_qtc + float(doc['amount_coin_satoshi'])
        else:
            total_trx = total_trx + float(doc['amount_coin_satoshi'])
    return jsonify({'qtc':float(total_qtc)/100000000, 'trx': float(total_trx)/100000000})




@admin_router.route('/admin-management-page/kyc' , methods=['GET', 'POST'])
@login_required
@admin_required
def admin_kyc():
    usersList=[]
    query = mongo.db.Verifys.find({}).sort("_id" ,-1)
    
    return render_template('admin/pages/admin_kyc.html' ,usersList=query  )

@admin_router.route('/admin-management-page/update-kyc/<id>', methods=['POST'])
@login_required
@admin_required
def admin_update_kyc(id):
    try:
        if request.method == 'POST':
            data = mongo.db.Verifys.find_one({'_id': ObjectId(id), 'status': 0})
            if data is not None:
                status = request.form['type']
                mongo.db.Verifys.update({'_id' : ObjectId(id) },{'$set' : {'status' : int(status)}})
        return jsonify({'success':1})
    except BaseException:
        logging.exception("An exception was thrown!")

@admin_router.route('/admin-management-page/add-note-kyc', methods=['POST'])
@login_required
@admin_required
def add_note_kyc():
    try:
        if request.method == 'POST':
            _id = request.form['note_id']
            body = request.form['note']
            mongo.db.Verifys.update({'_id' : ObjectId(_id) },{'$set' : {'admin_note' : body}})
        flash('Update success')
        return redirect("/admin-management-page/kyc")
    except BaseException:
        logging.exception("An exception was thrown!")

@admin_router.route('/admin-management-page/support' , methods=['GET', 'POST'])
@login_required
@admin_required
def admin_kycsupport():
    data=[]
    query = mongo.db.Contacts.find({}).sort("_id" ,-1)
    if request.method == 'POST':
        print(request.form)
        _id = request.form['_id']
        mongo.db.Contacts.update({'_id': ObjectId(_id)},{"$set": {"status":1}})
        query = mongo.db.Contacts.find({}).sort("_id" ,-1)
        return redirect("/admin-management-page/support")
    return render_template('admin/pages/admin_contact.html' ,data=query  )

@admin_router.route('/admin-management-page/support-user' , methods=['GET', 'POST'])
@login_required
@admin_required
def SupportUser():
    data=[]
    query = mongo.db.Supports.find({}).sort("_id" ,-1)
    if request.method == 'POST':
        print(request.form)
        _id = request.form['_id']
        mongo.db.Contacts.update({'_id': ObjectId(_id)},{"$set": {"status":1}})
        query = mongo.db.Contacts.find({}).sort("_id" ,-1)
        return redirect("/admin-management-page/support")
    return render_template('admin/pages/admin_support.html' ,data=query  )

@admin_router.route('/admin-management-page/support-user/<ids>' , methods=['GET', 'POST'])
@login_required
@admin_required
def SupportUserds(ids=""):
    data=[]
    query = mongo.db.Supports.find_one({"_id": ObjectId(ids) })
    if request.method == 'POST':
        print(request.form)
        _id = ids
        if request.form['msg'] != "":
            mongo.db.Supports.update({'_id': ObjectId(_id)},{"$set": {
                "status": 1,
                "read": 0
            },
            "$push": {
                "content": {
                    "msg": request.form['msg'],
                    "name":'Nole Support',
                    "date": datetime.now(),
                }
            }})
        return redirect("/admin-management-page/support-user")
    return render_template('admin/pages/admin_support_reply.html' ,data=query  )

