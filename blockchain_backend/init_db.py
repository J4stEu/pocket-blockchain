from flask_sqlalchemy import inspect
from app.blockchain_app.models import *

table_names = inspect(db.engine).get_table_names()
if not table_names:
    db.drop_all()
    db.create_all()
