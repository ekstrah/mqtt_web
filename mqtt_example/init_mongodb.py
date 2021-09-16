import pymongo

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
db = client['userID']
collection = db['ekstrah']
data = {'userID': 'ekstrah', 'port': 1883, 'CTName': 'mqtt_dev'}
x = collection.insert_one(data)
collection = db.port
data = {'CTName': 'testy', 'port': 1883, 'userID': 'ekstrah'}
x = collection.insert_one(data)