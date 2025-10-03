from flask import Flask
from dotenv import load_dotenv
import os
from app.database import init_db
from app.routes import api
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)

    CORS(
        app,
        supports_credentials=True,
        origins="*",
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    mongo_uri = (
        f"mongodb://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}"
        f"@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/"
        f"{os.getenv('MONGO_DB')}?authSource={os.getenv('MONGO_AUTH_DB')}"
    )
    app.config["MONGO_URI"] = mongo_uri
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    
    if(os.getenv("mongo_full")=="true"):
        app.config["MONGO_URI"] = mongo_uri
    else:
        app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET")
    app.config["JWT_ALGORITHM"] = os.getenv("JWT_ALGORITHM", "HS256")

    print(app.config)
    # DB
    init_db(app)

    # Routes
    app.register_blueprint(api, url_prefix="/")

    return app
