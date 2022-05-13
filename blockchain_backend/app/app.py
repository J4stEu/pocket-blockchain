from flask import Flask
from .config import Configuration, DockerDeployConfiguration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
# from flask_cors import CORS

app = Flask(__name__, template_folder='./dist', static_folder='./dist/assets')
if os.environ.get("DOCKER_DEPLOY") == "1":
    app.config.from_object(DockerDeployConfiguration)
else:
    app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

from .blockchain_app.models import *