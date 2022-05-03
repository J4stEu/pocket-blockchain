import hashlib


class MerkleTree(object):

    def get_txs_hashes(self, transactions):
        txs_hashes = []
        for transaction in transactions:
            txs_hashes.append(transaction.id)
        return txs_hashes

    def find_merkle_hash(self, txs_hashes):
        if len(txs_hashes) % 2 != 0:
            txs_hashes.append(txs_hashes[len(txs_hashes) - 1])
        secondary = []
        for k in [txs_hashes[x:x + 2] for x in range(0, len(txs_hashes), 2)]:
            secondary.append(hashlib.sha256((k[0] + k[1]).encode('utf-8')).hexdigest())
        if len(secondary) == 1:
            return secondary[0]
        else:
            return self.find_merkle_hash(secondary)