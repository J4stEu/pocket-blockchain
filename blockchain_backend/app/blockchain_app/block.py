class Block(object):
    def __init__(self, time_stamp, transactions, txsRootNode, prev_hash, hash, nonce):
        self.time_stamp = time_stamp
        self.transactions = transactions
        self.txsRootNode = txsRootNode
        self.prev_hash = prev_hash
        self.hash = hash
        self.nonce = nonce