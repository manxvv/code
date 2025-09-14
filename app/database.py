import pymongo, time
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    mongo_uri = app.config["MONGO_URI"]
    max_retries = 10

    for i in range(max_retries):
        try:
            client = pymongo.MongoClient(mongo_uri)
            client.admin.command("ping")
            print("✅ Connected to MongoDB")
            break
        except Exception:
            print("Waiting for MongoDB...")
            time.sleep(2)
    else:
        raise RuntimeError("Could not connect to MongoDB")

    mongo.init_app(app, uri=mongo_uri)
