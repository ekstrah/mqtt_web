from requests import get as get_ip
import requests
from flask import Flask, jsonify, render_template, request, redirect, flash, url_for
from flask.views import MethodView
from flask_simplelogin import SimpleLogin, get_username, login_required
import pymongo
from flask_cors import CORS
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import json
from datetime import datetime


new_init_account = {
  'userName': "ekstrah",
  'password': "ulsan2015",
  'role': 5,
  'allowed_container': 100,
  "csrf_token": "None",
  "email": "dongho@ekstrah.com",
}
public_init_account = {
  'userName': "public",
  'password': "ulsan2015",
  'role': 5,
  'allowed_container': 1,
  "csrf_token": "None",
  "email": "public@ekstrah.com",
}

free_init_account = {
  'userName': "free",
  'password': "ulsan2015",
  'role': 1,
  'allowed_container': -1,
  "csrf_token": "None",
  "email": "free@ekstrah.com",
}

premium_init_account = {
  'userName': "premium",
  'password': "ulsan2015",
  'role': 3,
  'allowed_container': 1,
  "csrf_token": "None",
  "email": "premium@ekstrah.com",
}

test_init_account = {
  'userName': "test",
  'password': "ulsan2015",
  'role': 0,
  'allowed_container': -1,
  "csrf_token": "None",
  "email": "test@ekstrah.com",
}

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
msgClient = pymongo.MongoClient("mongodb://127.0.0.1:27018/")
logClient = pymongo.MongoClient("mongodb://127.0.0.1:27019/")
dbUserID = client['userID']
app = Flask(__name__)
CORS(app)
db = client['web']
userCollection = db['userAccount']
pub_ip = get_ip('https://api.ipify.org').text

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class containerForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class ProtectedView(MethodView):
    decorators = [login_required]

    def get(self):
        return "You are logged in as <b>{0}</b>".format(get_username())


def inititialize_start_account():
    new_init_account['time-created'] = str(datetime.now())
    premium_init_account['time-created'] = str(datetime.now())
    test_init_account['time-created'] = str(datetime.now())
    free_init_account['time-created'] = str(datetime.now())
    public_init_account['time-created'] = str(datetime.now())
    vl = userCollection.count_documents({'userName': "ekstrah"})
    if vl == 0:
        userCollection.insert_one(new_init_account)
        userCollection.insert_one(premium_init_account)
        userCollection.insert_one(test_init_account)
        userCollection.insert_one(free_init_account)
        userCollection.insert_one(public_init_account)
    else:
        print("admin account already exist")


def check_user_account(user):
    data = userCollection.find_one({"userName": user['username'], "password": user['password']})
    if not data or data['role'] == 0:
        return False
    elif data['password'] == user['password'] and data:
        userCollection.update_one({"userName": user["username"], "password": user["password"]}, {"$set": {"csrf_token": user['csrf_token']}})
        return True
    return False

app = Flask(__name__, static_url_path='/static')
CORS(app)
app.config.from_object("settings")
inititialize_start_account()


simple_login = SimpleLogin(app, login_checker=check_user_account)



@app.route("/")
def index():
    return render_template("index.html", )

@app.route("/home/")
def home():
	return render_template("index.html")

@app.route("/profile/")
@login_required()
def profile_view():

    return render_template("profile.html")

@app.route("/test")
def test_example():
    return render_template("test.html")

@app.route("/secret")
@login_required()
def secret():
    return render_template("secret.html")


@app.route("/api", methods=["POST"])
@login_required(basic=True)
def api():
    return jsonify(data="You are logged in with basic auth")


@app.context_processor
def is_admin():
    user = get_username()
    if user == None:
        return dict(is_admin= 0, counter=0)
    data = userCollection.find_one({"userName": user})
    collection = dbUserID[user]
    containers = collection.find()
    count = 0
    resp_body = []
    for container in containers:
        port = container['port']
        CTName = container['CTName']
        dbController = container['dbController']
        t_dict = {'userID': user, 'port': port, 'CTName': CTName, 'Status': 'Active', "button_tag": [user, CTName, str(port)], "dbController": dbController}
        resp_body.append(t_dict)
        count = count + 1
    #Getting Public MQTT Broker
    col = dbUserID['public']
    containers = col.find()
    for container in containers:
        port = container['port']
        CTName = container['CTName']
        dbController = container['dbController']
        t_dict = {'userID': user, 'port': port, 'CTName': CTName, 'Status': 'Active', "button_tag": [user, CTName, str(port)], "dbController": dbController}
        resp_body.append(t_dict)
        count += 1
    if data['role'] == 5:
        return dict(is_admin= 1, counter=count, ct_body=resp_body)
    return dict(is_admin = 0,counter=count,  ct_body=resp_body)


def be_admin(user):
    """Validator to check if user has admin role"""
    data = userCollection.find_one({"userName": user})
    if data['role'] != 5:
        return "User does not have admin role"

def be_non_free(user):
    data = userCollection.find_one({"userName": user})
    if data['role'] < 2:
        return -10
    return 10



def get_role(user):
    data = userCollection.find_one({"userName": user})
    if data['role'] == 1:
        return "Free"
    if data['role'] == 3:
        return "Premium"
    return "Admin"


def get_24h(userID, CTName):
    from datetime import datetime
    now = datetime.now()
    logDB = logClient[userID]
    logCol = logDB[CTName]
    logs = logCol.find()
    total_24 = 0
    bef_24 = 0
    for log in logs:
        t_dt_object = datetime.strptime(log['time-stamp'], '%Y-%m-%d %H:%M:%S.%f')
        t_time = now - t_dt_object
        msg_time = int(t_time.total_seconds())
        if msg_time < 86400:
            total_24 += 1
        if msg_time > 86400 and msg_time < 172800:
            bef_24 += 1
    return total_24, bef_24



def isPublic(CTName):
    col = dbUserID['public']
    containers = col.find()
    for container in containers:
        if CTName == container['CTName']:
            return 1
    return 0

@app.route("/<userID>/<CTName>", strict_slashes=False)
@login_required()
def topicDisplay(userID, CTName):
    b_userID = userID
    """
        Check whether the CTName is assigned by public user
    """
    if isPublic(CTName):
        userID = 'public'

    msgDB = msgClient[userID]
    col = msgDB[CTName]
    topics = col.distinct('topic')
    json_topic = {}
    for topic in topics:
        doc = col.find_one({'topic': topic})
        try:
            tmp = json.loads(doc['message'])
            json_topic[topic] = 1
        except json.decoder.JSONDecodeError:
            json_topic[topic]= 0
    json_keys = list(json_topic.keys())

    # Getting Tier
    tier = get_role(b_userID)
    ct_DB = dbUserID[userID]
    CT_object = ct_DB.find_one({"CTName": CTName})
    ct_port = CT_object['port']
    total_24, bef_24 = get_24h(userID, CTName)
    if bef_24 == 0:
        change_24 = (total_24/1)*100
    else:
        change_24 = (total_24/bef_24)*100
    num_topics = len(topics)
    """
        - We need to get the port number somehow
        - Get Tier
    """
    button_tag=[userID,CTName, str(ct_port)]
    print(button_tag)
    return render_template("container.html", CTName=CTName, userID=userID, topics=topics, json_topic=json_topic, tier=tier, pub_ip=pub_ip, ct_port=ct_port, total_24=total_24, num_topics=num_topics, change_24=change_24, bef_24=int(total_24-bef_24),button_tag=button_tag)

# Fix the Json view and String view of the database
@app.route("/<userID>/<CTName>", strict_slashes=False)
@app.route("/<userID>/<CTName>/<path:topic>/string", strict_slashes=False)
def dbDisplay(userID, CTName, topic):
    if topic == None:
        topicDisplay(userID, CTName)
    msgDB = msgClient[userID]
    col = msgDB[CTName]
    dbData = col.find({"topic": topic})
    pub_count = dbData.count()
    table_data = []
    return render_template("string_view_topic.html", userID=userID, CTName=CTName, topic=topic, dbData=dbData, pub_count=pub_count )



@app.route("/<userID>/<CTName>/", strict_slashes=False)
@app.route("/<userID>/<CTName>/<path:topic>/json")
def dbDisplayJson(userID, CTName, topic):
    msgDB = msgClient[userID]
    col = msgDB[CTName]
    dbData = col.find({"topic": topic})
    table_data = []
    for data in dbData:
        table_data.append(json.loads(data['message']))
    s_data = col.find_one({"topic": topic})
    dict_keys = json.loads(s_data['message'])
    keys = list(dict_keys.keys())
    pub_count = dbData.count()
    return render_template('json_view_topic.html', userID=userID, CTName=CTName, topic=topic, keys=keys, table_data=table_data, pub_count=pub_count)


@app.route("/viewAC/<userName>")
@login_required(must=[be_admin])
def complex_view(userName):
    data = userCollection.find_one({'userName': userName})
    email = data['email']
    allowed_container = data['allowed_container']
    print(data['allowed_container'])
    return render_template("edit_indiv_user.html", userName=userName, email=email, allowed_container=allowed_container)

@app.route("/viewAC/")
@login_required(must=[be_admin])
def viewAC():
    data = userCollection.find()
    allAccount = []
    for account in data:
        tmp = {}
        tmp['userName'] = account["userName"]
        tmp['email'] = account["email"]
        tmp['role'] = account['role']
        tmp['num_cont'] = account['allowed_container']
        tmp['time-created'] = account['time-created']
        allAccount.append(tmp)
    data = userCollection.find({"isVerified": 0})
    unVerifiedAccount = []
    for account in data:
        unVerifiedAccount.append(account["userName"])
    return render_template("edit_user.html", allAccount=allAccount, unVerifiedAccount=unVerifiedAccount)


app.add_url_rule("/protected", view_func=ProtectedView.as_view("protected"))


@app.route("/createC/")
@login_required()
def create_container():
    username = get_username()
    if be_non_free(username) < 0:
        return render_template("non_free.html")
    return render_template("create_mqtt.html", userID=username)


@app.route("/edit/<userID>")
def login_test_view():
    return render_template("register2.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        userInit = {"userName": form.username.data, "password": form.password.data, "role": 0, "csrf_token": "None", "email": form.email.data}
        vl =userCollection.count_documents(userInit)
        if vl > 0:
            flash("Either user exist or username is already taken")
            return redirect(url_for('register'))
        else:
            userCollection.insert_one(userInit)
        flash('Thanks for registering')
        return redirect(url_for('simplelogin.login'))
    return render_template('registration.html', form=form)

@app.route('/user/update', methods=['GET', 'POST'])
@login_required(must=[be_admin])
def updaet_user_account():
    if request.method == 'POST':
        data = request.get_json()
        print(data['ctn_count'])
        print(userCollection.update_one({'userName': data['userName']}, {"$set" : {"role": int(data['tier']), "allowed_container" : int(data['ctn_count'])}}))
        
    return "a"
if __name__ == '__main__':
    app.run(debug=True, port=8080)