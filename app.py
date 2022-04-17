from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api_cors_config = {
    "origins": ["http://localhost:5000"],
    "methods": ["OPTIONS", "GET", "POST"],
    "allow_headers": ["Authorization", "Content-Type"]
}
cors = CORS(app, resources={r"/*": api_cors_config}, supports_credentials=True)

from blockchain import BlockChain
import models

bc = BlockChain()
