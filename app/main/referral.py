from datetime import datetime,date
from flask import render_template, session, redirect, url_for,request,current_app,abort,flash, json, jsonify
from flask_login import login_required
from . import main
from app import cache, mongo
from bson import ObjectId, json_util
@main.route('/account/referral', methods=['GET','POST'])
@login_required
def referral():
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    referral = mongo.db.Users.find({'p_node' : session['user_id']})
    total_binary_lefts =  total_binary_left(session['user_id'])
    total_binary_rights =  total_binary_right(session['user_id'])
    print(total_binary_lefts, total_binary_rights)
    return render_template('main/pages/referral.html', user=user, referral=referral, total_binary_lefts=total_binary_lefts, total_binary_rights=total_binary_rights)
@main.route('/account/update-position', methods=['GET','POST'])
@login_required
def update_position():
    user = mongo.db.Users.find_one({'_id' : session['user_id'] })
    if user['position'] == 1:
        mongo.db.Users.update({'_id': session['user_id']}, {"$set": {"position": 0}})
    else:
        mongo.db.Users.update({'_id': session['user_id']}, {"$set": {"position": 1}})
    return jsonify({'success': 1})
def check_binary_left (userId):
    status = True
    customer_ml = mongo.db.Users.find_one({'_id' : float(userId) })
    print(customer_ml['name'])
    p_binary = 0
    customer_ml_p_binary = None
    if customer_ml['_id'] == session['user_id']:
        return True
    while (True):
        customer_ml_p_binary = mongo.db.Users.find_one({'left': customer_ml['_id']})
        if customer_ml_p_binary is None:
            status = False
            break
        if customer_ml_p_binary['_id'] == session['user_id']:
            status = True
            break
        else:
            p_binary = customer_ml_p_binary['_id']
            customer_ml = customer_ml_p_binary 
    return status
def check_binary_right (userId):
    status = True
    customer_ml = mongo.db.Users.find_one({'_id' : float(userId) })
    print(customer_ml['name'])
    p_binary = 0
    if customer_ml['_id'] == session['user_id']:
        return True
    customer_ml_p_binary = None
    while (True):
        customer_ml_p_binary = mongo.db.Users.find_one({'right': customer_ml['_id']})
        if customer_ml_p_binary is None:
            status = False
            break
        if customer_ml_p_binary['_id'] == session['user_id']:
            status = True
            break
        else:
            p_binary = customer_ml_p_binary['_id']
            customer_ml = customer_ml_p_binary 
    return status

@main.route('/account/check-node', methods=['GET','POST'])
def check_node():
    print(request.form)
    p_binary = request.form['p_binary']
    position = request.form['positon']
    check_p_node = mongo.db.Users.find_one({'username': p_binary.upper() })
    status = False
    if check_p_node is not None:
        if position == "left":
            status = check_binary_left(check_p_node['_id'])
        else:
            status = check_binary_right(check_p_node['_id'])
        print(status)
    return jsonify({"success": status})

@main.route('/account/json_tree', methods=['GET','POST'])
def json_tree():
    uid = request.form['id_user']
    Json = reduceTreeBinary(int(uid))
    return json_util.dumps(Json)


def find_sponsor(uid):
    print(uid)
    sponor = mongo.db.Users.find_one({'_id': int(uid)})
    if sponor is not None:
        return sponor["name"]
    else:
        return "---"


def reduceTreeBinary(_id):
    users = mongo.db.Users
    user =  users.find_one({'_id': _id})
    json = []
    sponsor = find_sponsor(user['p_node'])
    tree = {
        "id":user['_id'],
        "sponsor": sponsor,
        "name": user['name'],
        "username":user['username'],
        "invest": user['balance']['total_invest'],
        'level': user['level'],
        'team_left': user['balance']['team_left'],
        'team_right': user['balance']['team_right'],
        'total_team_left': user['balance']['total_team_left'],
        'total_team_right': user['balance']['total_team_right'],
        "fl":1,
        "iconCls":"level2 root",
        'children' : []
    }
    json.append(tree)
    return children_tree_binary(tree)

def children_tree_binary(json):
    users = mongo.db.Users
    user =  users.find_one({'_id': json['id']})
    if user['left'] != 0:
        user_p_left = users.find_one({"$and" :[{'p_binary': json['id']}, {'_id': user['left']}] })
        fl = json['fl'] + 1
        sponsor = find_sponsor(user_p_left['p_node'])
        tree = {
            "id":user_p_left['_id'],
            "sponsor": sponsor,
            "name": user_p_left['name'],
            "username":user_p_left['username'],
            "invest": user_p_left['balance']['total_invest'],
            'level': user_p_left['level'],
            'team_left': user_p_left['balance']['team_left'],
            'team_right': user_p_left['balance']['team_right'],
            'total_team_left': user_p_left['balance']['total_team_left'],
            'total_team_right': user_p_left['balance']['total_team_right'],
            "fl": fl,
            "iconCls":"level2 left",
            'children' : []
        }
        if fl < 5:
            json['children'].append(tree)
            children_tree_binary(tree)
    else:
        fl = json['fl'] + 1
        tree = {  
            "fl":fl,
            "p_binary":json['username'],
            "empty":True,
            "iconCls":"level1 left",
            "id":"-1",
        }
        if fl < 5:
            json['children'].append(tree)
    
    if user['right'] != 0:
        user_p_right = users.find_one({"$and" :[{'p_binary': json['id']}, {'_id': user['right']}] })
        fl = json['fl'] + 1
        sponsor = find_sponsor(user_p_right['p_node'])
        tree = {
            "id":user_p_right['_id'],
            "sponsor": sponsor,
            "name": user_p_right['name'],
            "username":user_p_right['username'],
            "invest": user_p_right['balance']['total_invest'],
            'level': user_p_right['level'],
            'team_left': user_p_right['balance']['team_left'],
            'team_right': user_p_right['balance']['team_right'],
            'total_team_left': user_p_right['balance']['total_team_left'],
            'total_team_right': user_p_right['balance']['total_team_right'],
            "fl": fl,
            "iconCls":"level2 right",
            'children' : []
        }
        if fl < 5:
            json['children'].append(tree)
            children_tree_binary(tree)
    else:
        fl = json['fl'] + 1
        tree = {  
            "fl":fl,
            "p_binary":json['username'],
            "empty":True,
            "iconCls":"level1 right",
            "id":"-1"
        }
        if fl < 5:
            json['children'].append(tree)
    return json

def get_id_tree(ids):
    listId = ''
    query = mongo.db.Users.find({'p_binary': int(ids)})
    for x in query:
        listId += ', %s'%(x['_id'])
        listId += get_id_tree(x['_id'])
    return listId
def total_binary_right(customer_id):
    customer =mongo.db.Users.find_one({'_id': customer_id})
    count_right = 0
    if customer['right'] == 0:
        count_right = 0
    else:
        id_right_all = str(customer['right'])+get_id_tree(customer['right'])
        id_right_all = id_right_all.split(',')
        if (len(id_right_all) > 0):
            for yy in id_right_all:
                count_right = count_right + 1
    return count_right
def total_binary_left(customer_id):
    customer =mongo.db.Users.find_one({'_id': customer_id})
    count_left = 0
    if customer['left'] == 0:
        count_left = 0
    else:
        id_left_all = str(customer['left'])+get_id_tree(customer['left'])
        id_left_all = id_left_all.split(',')
        if (len(id_left_all) > 0):
            for yy in id_left_all:
                count_left = count_left + 1
    return count_left