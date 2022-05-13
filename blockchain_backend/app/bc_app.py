# from blockchain_backend.app.blockchain_app.blockchain import BlockChain
from .blockchain_app.blockchain import BlockChain
from .app import db

bc = BlockChain(db)
