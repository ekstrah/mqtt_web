import requests
from flask import Flask, jsonify, render_template, request, redirect, flash, url_for
from flask.views import MethodView
from flask_simplelogin import SimpleLogin, get_username, login_required
import pymongo
from flask_cors import CORS
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import json

init_account = {"userName": "ekstrah", "password": "ulsan2015", "isAdmin": 1, "csrf_token": "None", "isVerified": 3, "email": "dongho@ekstrah.com"}
dummy_account = {"userName": "test", "password": "test", "isAdmin": 0, "csrf_token": "None", "isVerified": 0, "email": "test@test.com"}
client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
msgClient = pymongo.MongoClient("mongodb://127.0.0.1:27018/")
dbUserID = client['userID']
app = Flask(__name__)
CORS(app)
db = client['web']
userCollection = db['userAccount']

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
    vl = userCollection.count_documents(init_account)
    if vl < 1:
        userCollection.insert_one(init_account)
        userCollection.insert_one(dummy_account)
    else:
        print("admin account already exist")


def check_user_account(user):
    data = userCollection.find_one({"userName": user['username'], "password": user['password']})
    if not data or data['isVerified'] == 0:
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
        return dict(is_admin= 0)
    data = userCollection.find_one({"userName": user})
    if data['isAdmin'] == 1:
        return dict(is_admin= 1)
    return dict(is_admin = 0)

def be_admin(user):
    """Validator to check if user has admin role"""
    data = userCollection.find_one({"userName": user})
    if data['isAdmin'] != 1:
        return "User does not have admin role"


def have_approval(username):
    """Validator: all users approved, return None"""
    return

@app.route("/activate", methods=["POST"])
def activate_account():
    if request.method == "POST":
        data = request.get_json()
        username = data['userName']
        userCollection.update_one({"userName": username}, {"$set": {"isVerified": 1}})
    return jsonify({"status": "success"})


@app.route("/complex")
@login_required(must=[be_admin, have_approval])
def complexview():
    return render_template("secret.html")

# Remove when publishing because it is used for dev only
@app.route('/dev', methods=["POST", "GET"])
@login_required()
def devel():
    form = containerForm(request.form)
    username = get_username()
    resp_body = []
    collection = dbUserID[username]
    containers = collection.find()
    button_tag = None
    for container in containers:
        port = container['port']
        CTName = container['CTName']
        dbController = container['dbController']
        t_dict = {'userID': username, 'port': port, 'CTName': CTName, 'Status': 'Active', "button_tag": [username, CTName, str(port)], "dbController": dbController}
        resp_body.append(t_dict)
        button_tag = [username, CTName, str(port)]
    if request.method == 'GET':
        return render_template('view_containers.html', ct_body=resp_body, userID=username, form=form)
    elif request.method == 'POST' and form.validate():
        userName = form.username.data
        passWord = form.password.data
        username = get_username()
        dataToSend = {"type" : 1, "userID": username, "CTName": "None", "mqtt_user": userName, "mqtt_pwd": passWord}
        res  = requests.post('http://localhost:5000/dev/create', json=dataToSend)
        return render_template('view_containers.html', ct_body=resp_body, userID=username, form=form)
    return render_template('view_containers.html', ct_body=resp_body, userID=username)


def inititialize_start_account():
    vl = userCollection.count_documents(init_account)
    if vl < 1:
        userCollection.insert_one(init_account)
    else:
        print("admin account already exist")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        userInit = {"userName": form.username.data, "password": form.password.data, "isAdmin": 0, "csrf_token": "None", "isVerified": 0, "email": form.email.data}
        vl =userCollection.count_documents(userInit)
        if vl > 0:
            flash("Either user exist or username is already taken")
            return redirect(url_for('register'))
        else:
            userCollection.insert_one(userInit)
        flash('Thanks for registering')
        return redirect(url_for('simplelogin.login'))
    return render_template('registration.html', form=form)


@app.route("/<userID>/<CTName>")
def dbDisplay(userID, CTName):
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
    return render_template('topic_list.html', CTName=CTName, userID=userID, topics=topics, json_keys=json_keys, json_topic=json_topic)

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
    return render_template('database_display_json.html', CTName=CTName, topic=topic, keys=keys, table_data=table_data)


@app.route("/<userID>/<CTName>/", strict_slashes=False)
@app.route("/<userID>/<CTName>/<path:topics>/string")
def dbDisplayString(userID, CTName, topics):
    msgDB = msgClient[userID]
    col = msgDB[CTName]
    dbData = col.find({"topic": topics})
    return render_template('database_display.html', CTName=CTName, topic=topics, dbData=dbData)



@app.route("/admin/verifyAC")
@login_required(must=[be_admin])
def complex_view():
    username = get_username()
    data = userCollection.find({"isVerified": 0})
    unVerifiedAccount = []
    for account in data:
        unVerifiedAccount.append(account["userName"])
    return render_template("user_verify.html",unVerifiedAccount=unVerifiedAccount)

@app.route("/admin/viewAC")
@login_required(must=[be_admin])
def viewAC():
    data = userCollection.find()
    allAccount = []
    print(data[0])
    for account in data:
        tmp = {}
        tmp['uesrName'] = account["userName"]
        tmp['email'] = account["email"]
        allAccount.append(tmp)
    return render_template("view_user.html", allAccount=allAccount)

app.add_url_rule("/protected", view_func=ProtectedView.as_view("protected"))


if __name__ == "__main__":
     app.run(host='0.0.0.0', port=5500)