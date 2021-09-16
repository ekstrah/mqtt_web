import pymongo

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
db = client['userID']
collection = db['ekstrah']
data = collection.find_one({"userID": "ekstrah"})
print(data['dbCTName'])
