import docker
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS

#Importing Environment
app = Flask(__name__)
CORS(app)
mongo = PyMongo(app, uri="mongodb://localhost:27017/userID")
db = mongo.db
client = docker.from_env()

def create_dbController(userID, CTName, dbCTName):
    #create_dbController calls container to feed mqtt message to database
    collection = db[userID]
    collection.update_one({"userID": userID, "CTName": CTName}, {"$set": {"dbController": 1, "dbCTName": dbCTName}})

def delete_dbController(userID, CTName):
    #delete_dbController deletes container that was feeding from mqtt
    collection = db[userID]
    collection.update_one({"userID": userID, "CTName": CTName}, {"$set": {"dbController": 0, "dbCTName": "None"}})

@app.route("/")
def hello_world():
    #Just host web loading
    return "<p>Hello, World!</p>"

@app.route('/dev/create', methods=["POST"])
def create_middle():
    #API Request that calls create_dbController
    if request.method == "POST":
        data = request.get_json()
        if data['userID'] is None or data['topic'] is None or data['CTName'] is None:
            return jsonify({'status': 'error', 'message': 'error in json data'})
        CT_port = 1883
        CT_user = data['userID']
        collection = db[data['userID']]
        try:
            container = client.containers.get(data['CTName'])
        except docker.errors.NotFound:
            return jsonify({'action': 'create handler', 'status': 'error', 'message' : "can't find the container with given name", 'statusCode': -1})
        CT_ip = container.attrs['NetworkSettings']['IPAddress']
        print(CT_user, CT_ip)
        container_query = collection.find_one({"userID": CT_user, "CTName": data['CTName']})
        CTCreds = container_query['CTCreds']
        print(CTCreds)
        mqttuser = container_query['container_cred_user']
        mqttpwd = container_query['container_cred_pwd']
        if CTCreds == 0:
            arg_cmd = "--user " + CT_user + " --ip " + CT_ip + " --topic " + data['topic'] + " --ctname " + data["CTName"] + " --cred " + str(CTCreds)
        else:
            arg_cmd = "--user " + CT_user + " --ip " + CT_ip + " --topic " + data['topic'] + " --ctname " + data["CTName"] + " --cred " + str(CTCreds) + " --mqttU " + mqttuser + " --mqttP " + mqttpwd
        ctn = client.containers.run("ekstrah/mqtt_sub:0.6", arg_cmd,  detach=True, auto_remove=True)
        print(ctn.logs())
        create_dbController(CT_user, data['CTName'], ctn.name)
        return jsonify({'action': 'create handler', 'status': 'success', 'message': 'Successfully added', 'statusCode' : 1})

@app.route('/dev/delete', methods=["POST"])
def delete_middle():
    #API Call that calls database delete
    if request.method == "POST":
        data = request.get_json()
        if data['userID'] is None or data['CTName'] is None:
            return jsonify({'status': 'error', 'message': 'error in json data'})
        CT_user = data['userID']
        collection = db[CT_user]
        dataDB = collection.find_one({"userID": CT_user, "CTName": data["CTName"]})
        print(dataDB)
        try:
            container = client.containers.get(dataDB['dbCTName'])
        except docker.errors.NotFound:
            return jsonify({'action': 'delete', 'status': 'error', 'message' : "can't find the container with given name", 'statusCode': -1})
        delete_dbController(CT_user, data['CTName'])
        container.stop()
        return jsonify({'action': 'delete handler', 'status': 'success', 'message': 'Successfully deleted', 'statusCode' : 1})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)
