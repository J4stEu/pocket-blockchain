from app import db


# blocks
class Blocks(db.Model):
    __tablename__ = 'b'

    hash = db.Column(db.String(256), primary_key=True, nullable=False)
    serializedBlock = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Blocks, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return 'hash: {}, serializedBlock: {}>'.format(self.hash, self.serializedBlock)


# hash of the last block in a chain
class LastBlock(db.Model):
    __tablename__ = 'l'

    hash = db.Column(db.String(256), primary_key=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(LastBlock, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return 'hash: {}>'.format(self.hash)

# chain state
