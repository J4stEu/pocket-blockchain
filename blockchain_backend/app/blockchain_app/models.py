from ..app import db


class Blocks(db.Model):
    __tablename__ = 'b'

    hash = db.Column(db.String(256), primary_key=True, nullable=False)
    txsRootNode = db.Column(db.String(256), nullable=False)
    serializedBlock = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Blocks, self).__init__(*args, **kwargs)

    def __repr__(self):
        return 'hash: {}, txsRootNode: {}, serializedBlock: {}>'.format(self.hash, self.txsRootNode,
                                                                        self.serializedBlock)


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

    txID = db.Column(db.String(256), primary_key=True, nullable=False)
    serializedUnspentOutputs = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(UTXO, self).__init__(*args, **kwargs)

    def __repr__(self):
        return 'txID: {}, serializedOutput: {}>'.format(self.txID, self.serializedOutput)


class TXPool(db.Model):
    __tablename__ = 'p'

    id = db.Column(db.INT, primary_key=True, autoincrement=True)
    txID = db.Column(db.String(256), nullable=True)
    fromAddr = db.Column(db.Text, nullable=False)
    toAddr = db.Column(db.Text, nullable=False)
    amount = db.Column(db.INT, nullable=False)
    serializedTransaction = db.Column(db.Text, nullable=True)
    error = db.Column(db.Boolean, nullable=False)
    errorText = db.Column(db.Text, nullable=True)

    def __init__(self, *args, **kwargs):
        super(TXPool, self).__init__(*args, **kwargs)

    def __repr__(self):
        return 'txID: {},  fromAddr: {}, toAddr: {}, amount: {}, serializedTransaction: {}, error: {}, errorText: {}>'.format(
            self.txID, self.fromAddr, self.toAddr, self.amount, self.serializedTransaction,  self.error, self.errorText)
