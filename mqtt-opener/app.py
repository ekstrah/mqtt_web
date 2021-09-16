from flask import Flask, jsonify, request
import docker, random
from flask_pymongo import PyMongo
from flask_cors import CORS
import os

#Importing Environment
app = Flask(__name__)
CORS(app)
mongo = PyMongo(app, uri="mongodb://localhost:27017/userID")
db = mongo.db
client = docker.from_env()
abs_path = os.getcwd()
# Essential Database Controller
def database_controller_ad(resp_data, userID):
    port = resp_data['port']
    container_name = resp_data['container_name']

    def manage_container_by_userID(port, container_name, userID):
        col = db['port']
        data = {'port': port, 'CTName': container_name, 'userID': userID}
        col.insert_one(data)
        return 0

    def manage_userID_container(port, container_name, userID, resp_data):
        # data = {'userID': 'ekstrah', 'port': 1883, 'CTName': 'mqtt_dev'}
        col = db[userID]
        data = {'userID': userID, 'port': port, 'CTName': container_name, "dbController": 0, "dbCTName": "None", "CTCreds": resp_data['container_cred'], 'container_cred_user': resp_data['container_cred_user'], 'container_cred_pwd': resp_data['container_cred_pwd']}
        col.insert_one(data)
    manage_container_by_userID(port, container_name, userID)
    manage_userID_container(port, container_name, userID, resp_data)

def database_controller_rm(userID, CTName, port):
    def find_port_by_CTName(CTName):
        col = db[userID]
        data = col.find_one({'CTName': CTName})
        print("found port %d".format(data['port']))
        return data['port']

    def manage_container_by_userID_rm(port, container_name, userID):
        col = db['port']
        data = {'port': port, 'CTName': container_name, 'userID': userID}
        resp = col.delete_one(data)
        print("deleted ", resp)
        return 0

    def manage_userID_container_rm(port, container_name, userID):
        col = db[userID]
        data = {'userID': userID, 'port': port, 'CTName': container_name}
        resp = col.delete_one(data)
        print("deleted ", resp)
    manage_container_by_userID_rm(port, CTName, userID)
    manage_userID_container_rm(port, CTName, userID)


def is_port_available(port):
    col = db['port']    
    length_v2 = col.count_documents({'port': port})
    if  length_v2 < 1:
        return 1
    return 0

def create_container(data, CTName=None):
    flag = 0
    while(flag == 0):
        rand_port = random.randint(20000, 30000)
        flag = is_port_available(rand_port)
    port_dict = {'1883/tcp' : ('0.0.0.0', rand_port) }
    if data['type'] == 0: #Create Simple Container
        vol = {'/Users/ekstrah/Desktop/mqtt_web/mqtt-opener/config_basic/.' : {'bind' : '/mosquitto/config/.', 'mode': 'rw'}}
    elif data['type'] == 1:
        mqtt_user = data['mqtt_user']
        mqtt_pwd = data['mqtt_pwd']

        #We need to create directory for user and remove it
        tmp_dir_path = abs_path+mqtt_user
        from os import path
        import subprocess
        import shutil
        if path.exists(tmp_dir_path):
            shutil.rmtree(tmp_dir_path)
            os.mkdir(tmp_dir_path)
        else:
            os.mkdir(tmp_dir_path)
        tmp_pwd_path = tmp_dir_path + "/"+mqtt_user
        creds_str = mqtt_user+":"+mqtt_pwd
        with open(tmp_pwd_path, "w") as f:
            f.write(creds_str)
        subprocess.call(['bash', './mqtt_pwd_gen.sh', tmp_pwd_path])
        fin_tmp_dir_path = tmp_dir_path+"."
        vol = {tmp_dir_path : {'bind' : '/mosquitto/config/.', 'mode': 'rw'}}
        vol = {'/Users/ekstrah/Desktop/mqtt_web/mqtt-opener/config/.' : {'bind' : '/mosquitto/config/.', 'mode': 'rw'}}
    if CTName == None:
        container = client.containers.run(image='eclipse-mosquitto:latest', detach=True, ports=port_dict, volumes=vol, auto_remove=True)
        # container = client.containers.run(image='eclipse-mosquitto:latest', detach=True,  volumes=vol, auto_remove=True)
    else:
        container = client.containers.run(image='eclipse-mosquitto:latest', detach=True, ports=port_dict, volumes=vol, name=CTName, auto_remove=True)
        # container = client.containers.run(image='eclipse-mosquitto:latest', detach=True, volumes=vol, name=CTName, auto_remove=True)
    if data['type'] == 1:
        ret_info = {'port': rand_port, 'container_id': container.id, 'container_name' : container.name, 'container_cred': data['type'], 'container_cred_user': mqtt_user, 'container_cred_pwd': mqtt_pwd}
    else:
        ret_info = {'port': rand_port, 'container_id': container.id, 'container_name' : container.name, 'container_cred': data['type'], 'container_cred_user': "None", 'container_cred_pwd': "None"}
    return ret_info
# Flask App code starts from here
    
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/dev/create', methods=['POST', 'GET'])
def create_new_container():
    if request.method == 'POST':
        CTName = None
        data = request.get_json()
        print(data)
        if data['userID'] == None:
            return jsonify({'action': 'create', 'status': 'success', 'message': 'userID invalid', 'statusCode' : -1})
        if data['CTName'] != "None":
            resp_data = create_container(data, CTName=data['CTName'])
        else:
            resp_data = create_container(data)
        database_controller_ad(resp_data, data['userID'])
        return jsonify({'action': 'create', 'status': 'success', 'message': 'Successfully Added', 'statusCode' : 1})
    if request.method == 'GET':
        return jsonify({'action': 'create', 'status': 'success', 'message': 'Get Request made', 'statusCode' : -1})

@app.route('/dev/delete', methods=['POST', 'GET'])
def delete_old_container():
    if request.method == "POST":
        data = request.get_json()
        if data['userID'] == None or data['CTName'] == None or data['port'] == None:
            return jsonify({'status': 'error', 'message': 'error in json data'})
        CTName = data['CTName']
        userID = data['userID']
        port = data['port']
        print(CTName, userID, port)
        try:
            container = client.containers.get(CTName)
        except docker.errors.NotFound:
            return jsonify({'action': 'delete', 'status': 'error', 'message' : "can't find the container with given name", 'statusCode': -1})
        print(container.name)
        container.stop()
        database_controller_rm(userID, CTName, port)
        return jsonify({'action': 'delete', 'status': 'success', 'message': 'Successfully removed', 'statusCode' : 1})
    else:
        return jsonify({'action': 'delete', 'status': 'failure', 'message': 'Other request received which is not implemented', 'statusCode': -1})

if __name__ == "__main__":
     app.run(host='0.0.0.0', port=5000)
