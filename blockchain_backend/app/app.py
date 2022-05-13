from flask import Flask
from .config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_cors import CORS

app = Flask(__name__, static_folder='../blockchain_frontend/dist')
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

from .blockchain_app.models import *