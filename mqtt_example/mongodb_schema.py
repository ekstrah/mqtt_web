from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27018/")
db = client.test
print(db.list_collection_names())