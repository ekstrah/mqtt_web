import pymongo

client = pymongo.MongoClient("mongodb://127.0.0.1:27018/")
db = client['test']
collection = db['my_coll']
data = {"component": "hello World", "path": "/home/user/ekstrah/Desktop", "dummy": "helloWorld"}
x = collection.insert_one(data)