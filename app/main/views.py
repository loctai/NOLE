from datetime import datetime,date
import time
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash 
from . import main
from flask_pymongo import pymongo ,MongoClient
from flask_login import login_required
from .forms import ContactForm, PostForm,PropertyForm,EditProfileForm,CommentForm,EditProfileAdminForm
from flask_login import current_user
from werkzeug import secure_filename
from functools import wraps
from cloudinary.uploader import upload_image
from cloudinary.utils import cloudinary_url
from app import cache 
from app.utils import helpers
# mongodb database connection
from app import mongo
from app.tasks import celery
def admin_required(f):
    @wraps(f)
    def  wrap(*args, **kwargs):
        users = mongo.db.Users
        query= users.find({'email': session['email'] },{'role':'1'})
        for i in query:
            dbRole = i['role']
            if dbRole != 'admin':
                    return redirect(url_for('auth.login', next=request.url))
            else:
                return f(*args, **kwargs)
    return wrap

def delete(collection,uniqueid):
    return collection.remove({'_id': uniqueid})

#Main pages of twre site
@main.route('/', methods=['GET','POST'])
@main.route('/home', methods=['GET','POST'])
# @cache.cached(timeout=15, key_prefix="home")
def home():
    form = ContactForm()
    ref = request.args.get('ref', '')
    if ref != '':
        existing_user = mongo.db.Users.find_one({'username': ref.upper() })
        if existing_user is not None:
            session['ref'] = ref
            return redirect('/auth/signup')
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
                "name": 1,
                "amount": 1,
                "cust_name": "$customer.username"
            }
        },
        {
            "$unwind": "$cust_name"
        }
    ]
    # totos = mongo.db.todos.aggregate(pipeline)
    msg = {'task_id':767676, 'command':'command', 'magic':'magic_type'}
    # celery.send_task('task_deposit', retry=True, args=(msg,))
    if request.method == 'POST':
        print('request.form', request.form)
    if form.validate_on_submit():
        print(request.form)
        mongo.db.Contacts.insert({    
            "status": 0,        
            'name': request.form['name'],
            "email": request.form['email'],
            "message": request.form['message'],
            'createdAt': datetime.now()
        })
        flash('Send message successfully')
    # estates =[]
    # query = mongo.db.Estates.find({}, {"_id":"1" ,"Title":"1", "Category":"1","Price":"1" ,"Address":"1" ,"Photos": "1"  }).limit(8).sort("_id" ,-1)
    # for i in query:
    #     _id =i['_id']
    #     title = i['Title']
    #     category = i['Category'] 
    #     price = i['Price']
    #     address = i['Address']
    #     image = i['Photos']
    #     estates.append([ _id,title, category , price , address , image])
    return render_template('home/pages/home.html', form=form )
@main.route('/news',methods=['GET','POST'])
def EventPage():
    return render_template('home/pages/news.html', page="event_page")

@main.route('/contact',methods=['GET','POST'])
def contactPage():
    form = ContactForm()
    if form.validate_on_submit():
        print(request.form)
        mongo.db.Contacts.insert({    
            "status": 0,        
            'name': request.form['name'],
            "email": request.form['email'],
            "message": request.form['message'],
            'createdAt': datetime.now()
        })
        flash('Send message successfully')
    return render_template('home/pages/contact.html', page="page_contact", form=form )

@main.route('/explorer',methods=['GET','POST'])
@cache.cached(timeout=15, key_prefix="explorer")
def explorer():
    return render_template('home/pages/explorer.html', page="page_explorer")

@main.route('/trading-bot-signals',  methods=['GET','POST'])
@cache.cached(timeout=15, key_prefix="properties")
@login_required
def TradingBotSignals():
    tradeDB=mongo.db.trades
    estates =[]
    query=tradeDB.find({}).sort("_id" ,-1)    
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    return render_template('main/pages/trading_bot_signals.html', user=user,data=query )

@main.route('/properties',  methods=['GET','POST'])
@cache.cached(timeout=15, key_prefix="properties")
def properties():
    estatesDB=mongo.db.Estates
    estates =[]
    query=estatesDB.find({},{"_id":"1" ,"Title":"1", "Category":"1","Price":"1" ,"Address":"1" ,"Photos": "1"  }).sort("_id" ,-1)
    for i in query:
        _id = i['_id']
        title = i['Title']
        category = i['Category'] 
        price = i['Price']
        address = i['Address']
        photos = i['Photos']
        estates.append([ _id,title, category , price , address , photos])
    
    return render_template('properties.html', estates=estates )

    
@main.route('/blog',methods=['GET','POST'])
@cache.cached(timeout=15, key_prefix="blog")
def blog():
    posts = []
    query = mongo.db.Posts.find({}).sort('_id' , -1)
    for  i in query:
        _id = i['_id']
        title = i['Title']
        summary = i['Summary']
        image = i['Image_url']
        slug = i['Slug']
        posts.append([_id ,title , summary ,image, slug ])
    return render_template('home/pages/blog.html' ,posts=posts   )


@main.route('/about')
@cache.cached(timeout=15, key_prefix="about")
def about():
    return render_template('about.html')

@main.route('/user')
@cache.cached(timeout=15, key_prefix="user")
def user():
    query = mongo.db.Users.find({'email' : session['email'] },{'username': '1', 'email': '1', 'name': '1','location': '1','about_me' : '1'})
    user ={}
    for i in query:
        user={
            'username' :  i['username'],
            'email' : i['email'],
            'name' : i['name'],
            'location' : i['location'],
        'about_me' : i['about_me']
        }
    if user is None:
        abort(404)
    return render_template('user.html' , user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    query = mongo.db.Users.find({'email': session['email']},{'_id': '1' ,'password':'1', 'email': '1', 'username': '1', 'name': '1' , 'location': '1', 'about_me': '1' ,'role': '1', 'Date':'1'})
    for i in query:
        oldId = i['_id']
        oldPassword = i['password']
        oldEmail  = i['email']
        oldUsername = i['username']
        oldName = i['name']
        oldLocation = i['location']
        oldAboutme = i['about_me']
        oldRole = i['role']
        date = i['Date']
  
    form = EditProfileForm( )
    if form.validate_on_submit():
        mongo.db.Users.update( {'_id':oldId},{'_id': oldId, 'password': oldPassword, 'email' : oldEmail, 'username' : oldUsername,'name': request.form['name'], 'location' : request.form['location'],'about_me' : request.form['about_me'] ,'role':  oldRole, 'Date' : date , 'Edit-date': datetime.now()})
        flash('Your profile has been updated.')
        return redirect(url_for('.user'))
    
    form.name.data = oldName
    form.location.data = oldLocation
    form.about_me.data = oldAboutme
    
    return render_template('edit_profile.html', form=form)   

@main.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    query = mongo.db.Posts.find({"Slug": slug })
    post ={}

    for i in query:
        post={
        '_id' :i['_id'],
       'title' :i['Title'],
        'body_html':i['Body'],
        'image' :i['Image_url'],
        'date':i['Date']
        }
   
    return render_template('home/pages/post.html', post=post)

@main.route('/property/<int:id>', methods=['GET', 'POST'])
def property(id):
    query = mongo.db.Estates.find({"_id": id }, {"_id":"1", "Title":"1", "Category":"1","Price":"1" ,"Address":"1", "Body" :"1" ,"Photos": "1"   })
    estate = {}

    for i in query:
        estate = {
            '_id': i['_id'],
            'title': i['Title'] ,
            'category': i['Category'], 
            'price': i['Price'], 
            'address': i['Address'],
            'body': i['Body'], 
            'image': i['Photos']
        }
    
    return render_template('property.html', estate=estate )


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    query = mongo.db.Users.find({'_id' : id},{'_id': '1' ,'password':'1', 'email': '1', 'username': '1', 'name': '1' , 'location': '1', 'about_me': '1' , 'Date':'1'})
    for i in query:
        oldId = i['_id']
        oldPassword = i['password']
        oldEmail = i['email']
        oldUsername = i['username']
        oldName = i['name']
        oldLocation = i['location']
        oldAboutme = i['about_me']
        date = i['Date']

    form = EditProfileAdminForm( )
    if form.validate_on_submit():
        mongo.db.Users.update( {'_id':id},{'_id': oldId, 'password': oldPassword, 'email' : request.form['email'], 'username' : request.form['username'] ,'name': request.form['name'], 'location' : request.form['location'],'about_me' : request.form['about_me'] ,'role': request.form['role'] , 'Date' : date , 'Edit-date': datetime.now()})
        flash('The profile has been updated.')
        return redirect(url_for('admin.admin_users'))
    form.email.data = oldEmail
    form.username.data = oldUsername
    form.name.data = oldName
    form.location.data = oldLocation
    form.about_me.data = oldAboutme
    return render_template('edit_profile.html', form=form)
