import pymongo

client = pymongo.MongoClient("mongodb://172.17.0.1:27017/")
db = client['userID']
print(db.list_collection_names()) 
