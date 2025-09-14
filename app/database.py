from flask_pymongo import PyMongo
from flask import current_app
import time
mongo = PyMongo()

def init_db(app):
    
    print(app.config)
    
    mongo.init_app(app, uri=app.config["MONGO_URI"])
