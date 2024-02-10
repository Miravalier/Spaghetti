import pymongo


client = pymongo.MongoClient("mongodb://spaghetti_db:27017")
db = client.spaghetti_db

users = db.users
users.create_index({"name": 1}, unique=True)
