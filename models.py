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

# chainstate - store unspent tx outputs (cache)
class UTXO(db.Model):
    __tablename__ = 'c'

    txID = db.Column(db.String(256), nullable=False)
    serializedUnspentOutputs = db.Column(db.Text, primary_key=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(UTXO, self).__init__(*args, **kwargs)

    def __repr__(self):
        return 'txID: {}, serializedOutput: {}>'.format(self.txID, self.serializedOutput)
