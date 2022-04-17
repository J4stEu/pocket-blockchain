import hashlib
import os.path
from fastecdsa import curve, ecdsa, keys
from fastecdsa.encoding.pem import PEMEncoder
from fastecdsa.encoding.der import DEREncoder
from base58 import b58encode, b58decode
from datetime import datetime
import json
from app import db
import models


class Wallet(object):
    def __init__(self, private_key, public_key, public_key_bytes):
        self.private_key = private_key
        self.public_key = public_key
        self.public_key_bytes = public_key_bytes


class Transaction(object):
    def __init__(self, id, inputs, outputs):
        self.id = id
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        inputs_representation = []
        for v_in in self.inputs:
            inputs_representation.append(v_in.__repr__)
        outputs_representation = []
        for v_out in self.outputs:
            outputs_representation.append(v_out.__repr__)
        return "Transaction: id = {}, inputs = {}, outputs = {}".format(self.id, inputs_representation, outputs_representation)


class TransactionInput(object):
    def __init__(self, id, output, sig, public_key, public_key_bytes):
        self.id = id
        self.output = output
        self.sig = sig
        self.public_key = public_key
        self.public_key_bytes = public_key_bytes

    def __repr__(self):
        return "TransactionInput: " \
               "id = {}, output = {}, " \
               "sig = {}, public_key = {}, " \
               "public_key_bytes = {}".format(self.id, self.output, self.sig, self.public_key, self.public_key_bytes)

    def uses_key(self, public_key, public_key_hash):
        return public_key == public_key_hash


class TransactionOutput(object):
    def __init__(self, val, public_key_hash):
        self.val = val
        self.public_key_hash = public_key_hash

    def __repr__(self):
        return "TransactionOutput: val = {}, pubKeyHash = {}".format(self.val, self.public_key_hash)

    def lock(self, address, version, addr_check_sum_len):
        public_key_hash = b58decode(address)
        public_key_hash = public_key_hash[len(version): len(public_key_hash) - addr_check_sum_len]
        return public_key_hash

    def is_locked_with_key(self, public_key_hash):
        return public_key_hash == self.public_key_hash


class Block(object):
    def __init__(self, time_stamp, transactions, txsRootNode, prev_hash, hash, nonce):
        self.time_stamp = time_stamp
        self.transactions = transactions
        self.txsRootNode = txsRootNode
        self.prev_hash = prev_hash
        self.hash = hash
        self.nonce = nonce


class MerkleTree(object):
    def __init__(self):
        pass

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
            self.find_merkle_hash(secondary)
        pass

class ChainState(object):
    def __init__(self):
        self.unspent_tx_outputs = []

    def get_utxo(self):
        serialized_unspent_tx_outputs = models.UTXO.query.all()
        return self.de_serialize_unspent_tx_outputs(serialized_unspent_tx_outputs)

    def store_utxo(self, unspent_tx_outputs):
        # delete old cache
        db.session.query(models.UTXO).delete()
        db.session.commit()
        serialized_unspent_tx_outputs = self.serialize_unspent_tx_outputs(unspent_tx_outputs)
        utxo = []
        for key, serialized_output in serialized_unspent_tx_outputs.items():
            utxo.append(models.UTXO(txID=key, serializedUnspentOutputs=json.dumps(serialized_output)))
        db.session.add_all(utxo)
        db.session.commit()


    def update_utxo(self, transaction):
        utxo = self.get_utxo()
        new_unspent_tx_outputs = {}
        for key, unspent_tx_outputs in utxo.items():
            for unspent_tx_output in unspent_tx_outputs:
                spent = False
                for input in transaction.inputs:
                    if input.id == key and input.output == unspent_tx_output["outputID"]:
                        spent = True
                        break
                if spent is False:
                    if key in new_unspent_tx_outputs:
                        new_unspent_tx_outputs[key].append(
                            {
                                "outputID": unspent_tx_output["outputID"],
                                "output": unspent_tx_output["output"]
                            }
                        )
                    else:
                        new_unspent_tx_outputs[key] = []
                        new_unspent_tx_outputs[key].append(
                            {
                                "outputID": unspent_tx_output["outputID"],
                                "output": unspent_tx_output["output"]
                            }
                        )
        for index, output in enumerate(transaction.outputs):
            if transaction.id in new_unspent_tx_outputs:
                new_unspent_tx_outputs[transaction.id].append(
                    {
                        "outputID": index,
                        "output": output
                    }
                )
            else:
                new_unspent_tx_outputs[transaction.id] = []
                new_unspent_tx_outputs[transaction.id].append(
                    {
                        "outputID": index,
                        "output": output
                    }
                )
        self.store_utxo(new_unspent_tx_outputs)

    def reindex_utxo(self, serialized_blocks, de_serialize):
        # get spent outputs: tx id -> spent outputs
        spent_tx_outputs = {}
        for serialized_block in serialized_blocks:
            block = de_serialize(serialized_block.serializedBlock)
            for tx in block.transactions:
                for index, input in enumerate(tx.inputs):
                    if input.id in spent_tx_outputs:
                        spent_tx_outputs[input.id].append(input.output)
                    else:
                        spent_tx_outputs[input.id] = []
                        spent_tx_outputs[input.id].append(input.output)
        # get unspent tx outputs: tx id -> spent outputs
        unspent_tx_outputs = {}
        for serialized_block in serialized_blocks:
            block = de_serialize(serialized_block.serializedBlock)
            for tx in block.transactions:
                for index, output in enumerate(tx.outputs):
                    move = True
                    if tx.id in spent_tx_outputs:
                        for spent_output_index in spent_tx_outputs[tx.id]:
                            if index == spent_output_index:
                                move = False
                    if move is False: continue
                    if tx.id in unspent_tx_outputs:
                        unspent_tx_outputs[tx.id].append(
                            {
                                "outputID": index,
                                "output": output
                            }
                        )
                    else:
                        unspent_tx_outputs[tx.id] = []
                        unspent_tx_outputs[tx.id].append(
                            {
                                "outputID": index,
                                "output": output
                            }
                        )
        return unspent_tx_outputs

    def reindex(self, serialized_blocks, de_serialize):
        unspent_tx_outputs = self.reindex_utxo(serialized_blocks, de_serialize)
        self.unspent_tx_outputs = unspent_tx_outputs
        self.store_utxo(unspent_tx_outputs)

    def serialize_unspent_tx_outputs(self, unspent_tx_outputs):
        serialized_unspent_tx_outputs = {}
        for key, outputs in unspent_tx_outputs.items():
            for output in outputs:
                if key in serialized_unspent_tx_outputs:
                    serialized_unspent_tx_outputs[key].append({
                        "outputID": output["outputID"],
                        "val": output["output"].val,
                        "publicKeyHash": (output["output"].public_key_hash).decode("latin1")
                    })
                else:
                    serialized_unspent_tx_outputs[key] = []
                    serialized_unspent_tx_outputs[key].append({
                        "outputID": output["outputID"],
                        "val": output["output"].val,
                        "publicKeyHash": (output["output"].public_key_hash).decode("latin1")
                    })
        return serialized_unspent_tx_outputs

    def de_serialize_unspent_tx_outputs(self, serialized_unspent_txs):
        unspent_tx_outputs = {}
        for serialized_unspent_tx in serialized_unspent_txs:
            serialized_unspent_outputs = json.loads(serialized_unspent_tx.serializedUnspentOutputs)
            for output in serialized_unspent_outputs:
                if serialized_unspent_tx.txID in unspent_tx_outputs:
                    unspent_tx_outputs[serialized_unspent_tx.txID].append(
                        {
                            "outputID": output["outputID"],
                            "output": TransactionOutput(
                                output["val"],
                                (output["publicKeyHash"]).encode("latin1"),
                            )
                        }
                    )
                else:
                    unspent_tx_outputs[serialized_unspent_tx.txID] = []
                    unspent_tx_outputs[serialized_unspent_tx.txID].append(
                        {
                            "outputID": output["outputID"],
                            "output": TransactionOutput(
                                output["val"],
                                (output["publicKeyHash"]).encode("latin1"),
                            )
                        }
                    )
        return unspent_tx_outputs

class Chain(object):
    def __init__(self):
        # wallets store location
        self.wallets_store = "./wallets.bcw"
        # target_bits - we can change target bits due to control complexity of making new blocks
        # self.target_bits = int(24)
        self.target_bits = int(12)
        # sign_unit - reward value for mining
        self.sign_unit = 10
        # addr_check_sum_len - default length of the address checksum
        self.addr_check_sum_len = 4
        # version - target network is the mainnet, version = 0x00
        self.version = bytes(0x00)
        # unspent transaction outputs - cache
        self.chain_state = ChainState()
        self.merkle_tree = MerkleTree()

    def new_wallet(self):
        pr_key, pub_key, pub_key_bytes = self.new_key_pair()
        wallet = Wallet(pr_key, pub_key, pub_key_bytes)
        address = str(self.get_address(wallet), 'utf-8')
        self.save_wallet(wallet, address)
        print('Your new address: ' + address)
        return address

    def save_wallet(self, wallet, address):
        wallets_bcw = os.path.isfile(self.wallets_store)
        if wallets_bcw:
            with open(self.wallets_store, 'r') as f:
                serialized_wallets = json.load(f)
            wallets = self.de_serialize_wallets(serialized_wallets)
            wallets[address] = wallet
            new_serialized_wallets = self.serialize_wallets(wallets)
            with open(self.wallets_store, 'w') as f:
                json.dump(new_serialized_wallets, f)
        else:
            wallets = {address: wallet}
            new_serialized_wallets = self.serialize_wallets(wallets)
            with open(self.wallets_store, 'w') as f:
                json.dump(new_serialized_wallets, f)

    def serialize_wallet(self, wallet):
        return {
            "privateKey": wallet.private_key,
            "publicKey": PEMEncoder.encode_public_key(wallet.public_key),
            "publicKeyBytes": (wallet.public_key_bytes).decode("latin1")
        }

    def serialize_wallets(self, wallets):
        serialized_wallets = {}
        for address, wallet in wallets.items():
            serialized_wallets[address] = self.serialize_wallet(wallet)
        return serialized_wallets

    def de_serialize_wallet(self, wallet):
        return Wallet(
            wallet["privateKey"],
            PEMEncoder.decode_public_key(wallet["publicKey"], curve=curve.P256),
            wallet["publicKeyBytes"].encode("latin1"),
        )

    def de_serialize_wallets(self, serialized_wallets):
        wallets = {}
        for address, serialized_wallet in serialized_wallets.items():
            wallet = self.de_serialize_wallet(serialized_wallet)
            wallets[address] = wallet
        return wallets

    def get_wallets(self):
        wallets_bcw = os.path.isfile(self.wallets_store)
        if not wallets_bcw:
            print("There is no any wallets.")
            return None
        with open(self.wallets_store, 'r') as f:
            serialized_wallets = json.load(f)
        return self.de_serialize_wallets(serialized_wallets)

    def new_key_pair(self):
        # generate a private key for curve P256
        pr_key = keys.gen_private_key(curve.P256)
        # get the public key corresponding to the private key we just generated
        pub_key = keys.get_public_key(pr_key, curve.P256)
        # public key to bytes
        pub_key_bytes = pub_key.x.to_bytes(32, "big") + pub_key.y.to_bytes(32, "big")
        return pr_key, pub_key, pub_key_bytes

    def get_address(self, wallet):
        pub_key_hash = self.pub_key_hash(self.version + wallet.public_key_bytes)
        # first 4 bytes - checksum
        checksum = hashlib.sha256(hashlib.sha256(pub_key_hash).digest()).digest()[:self.addr_check_sum_len]
        address = b58encode(pub_key_hash + checksum)
        return address

    # def is_address_valid(self, address):
    #     pub_key_hash = b58decode(address)
    #     # pub key
    #     pub_key = pub_key_hash[: len(pub_key_hash) - self.addr_check_sum_len]
    #     # check sum
    #     check_sum = pub_key_hash[len(pub_key_hash) - self.addr_check_sum_len:]
    #     pass

    def pub_key_hash(self, pub_key_bytes):
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(pub_key_bytes).digest())
        return ripemd160.digest()

    def sign_transaction(self, transaction, private_key):
        if self.is_coin_base(transaction):
            return
        prev_transactions = {}
        for input in transaction.inputs:
            prev_transaction = self.find_transaction(input.id)
            if prev_transaction is None:
                print('Failed to find previous transaction')
                return
            prev_transactions[prev_transaction.id] = prev_transaction
        return self.sign(transaction, prev_transactions, private_key)

    def sign(self, transaction, prev_transactions, private_key):
        for input in transaction.inputs:
            if not (input.id in prev_transactions and prev_transactions[input.id].id):
                print('Previous transaction is not correct')
                return
        tx_trimmed_copy = self.tx_trimmed_copy(transaction)
        for index, input in enumerate(tx_trimmed_copy.inputs):
            prev_transaction = prev_transactions[input.id]
            input.sig = None
            input.public_key_bytes = prev_transaction.outputs[input.output].public_key_hash
            data_to_sign = tx_trimmed_copy.__repr__()
            r, s = ecdsa.sign(data_to_sign, private_key)
            transaction.inputs[index].sig = {'r': r, 's': s}
            input.public_key = None
        return transaction

    def verify_transaction(self, transaction):
        if self.is_coin_base(transaction):
            return
        prev_transactions = {}
        for input in transaction.inputs:
            prev_transaction = self.find_transaction(input.id)
            if prev_transaction is None:
                print('Failed to find previous transaction')
                return
            prev_transactions[prev_transaction.id] = prev_transaction
        return self.verify(transaction, prev_transactions)

    def verify(self, transaction, prev_transactions):
        for input in transaction.inputs:
            if not (input.id in prev_transactions and prev_transactions[input.id].id):
                print('Previous transaction is not correct')
                return
        tx_trimmed_copy = self.tx_trimmed_copy(transaction)
        for index, input in enumerate(transaction.inputs):
            prev_transaction = prev_transactions[input.id]
            tx_trimmed_copy.inputs[index].sig = None
            tx_trimmed_copy.inputs[index].public_key_bytes = prev_transaction.outputs[input.output].public_key_hash
            if input.sig is None:
                return False
            r, s = input.sig['r'], input.sig['s']
            data_to_verify = tx_trimmed_copy.__repr__()
            verify = ecdsa.verify((r, s), data_to_verify, input.public_key)
            if verify is False:
                return False
        return True

    def tx_trimmed_copy(self, transaction):
        inputs = []
        outputs = []
        for input in transaction.inputs:
            inputs.append(TransactionInput(input.id, input.output, None, None, None))
        for output in transaction.outputs:
            outputs.append(TransactionOutput(output.val, output.public_key_hash))
        return Transaction(transaction.id, inputs, outputs)

    def transaction_hash(self, transaction):
        all_in_one = ''
        for tx_input in transaction.inputs:
            all_in_one += str(tx_input.id) + str(tx_input.output) + str(tx_input.sig) + str(tx_input.public_key)
        for tx_output in transaction.outputs:
            all_in_one += str(tx_output.val) + str(tx_output.public_key_hash)
        tx_hash = hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()
        return tx_hash

    def coin_base_tx(self, to, data):
        tx_input = TransactionInput(0, -1, None, data, data)
        tx_output = TransactionOutput(self.sign_unit, None)
        tx_output.public_key_hash = tx_output.lock(to, self.version, self.addr_check_sum_len)
        tr = Transaction(0, [tx_input], [tx_output])
        tr.id = self.transaction_hash(tr)
        return tr

    def is_coin_base(self, transaction):
        return len(transaction.inputs) == 1 and transaction.inputs[0].id == 0 and transaction.inputs[0].output == -1

    # def unspent_txs(self, pub_key_hash):
    #     unspent_txs = []
    #     unlocking_inputs = []
    #     unspent_valid_txs = []
    #     blocks = self.get_blocks()
    #     if blocks is None:
    #         return None
    #     for serialized_block in blocks:
    #         block = self.de_serialize(serialized_block.serializedBlock)
    #         for tx in block.transactions:
    #             for index, output in enumerate(tx.outputs):
    #                 move = True
    #                 for input in tx.inputs:
    #                     # if an input have any reference to the output -> tx was spent
    #                     if (index == input.output) and (input.id == tx.id):
    #                         move = False
    #                         break
    #                 if move is False: continue
    #                 # check if provided public key hash was used to lock the output
    #                 if output.is_locked_with_key(pub_key_hash):
    #                     # set tx itself, index of the vOut and vOut itself
    #                     unspent_txs.append([tx, index, output])
    #             for input in tx.inputs:
    #                 if self.is_coin_base(tx): break  # first transaction
    #                 if input.uses_key(self.pub_key_hash(input.pub_key_bytes), pub_key_hash):
    #                     unlocking_inputs.append(input)
    #     # we have unlocking inputs and unspent transactions -> get valid unspent transactions
    #     if len(unlocking_inputs) == 0:
    #         unspent_valid_txs = unspent_txs
    #     else:
    #         for unspent_tx in unspent_txs:
    #             for _ in unlocking_inputs:
    #                 equals = False
    #                 for input in unlocking_inputs:
    #                     if (input.id == unspent_tx[0].id) and (input.v_out == unspent_tx[1]):
    #                         equals = True
    #                         break
    #                 if equals is False:
    #                     unspent_valid_txs.append(unspent_tx)
    #                     break
    #     return unspent_valid_txs

    def unspent_txs(self, pub_key_hash):
        unspent_valid_txs = []
        unspent_transactions = self.chain_state.get_utxo()
        for key, unspent_transaction_outputs in unspent_transactions.items():
            for output in unspent_transaction_outputs:
                if output["output"].is_locked_with_key(pub_key_hash):
                    unspent_valid_txs.append([key, output["outputID"], output["output"]])
        return unspent_valid_txs

    def acc_verify(self, pub_key_hash, amount):
        unspent_txs = self.unspent_txs(pub_key_hash)
        address_txs_to_spend = []
        acc = 0
        for tx in unspent_txs:
            if acc < amount:
                acc += tx[2].val
                address_txs_to_spend.append(tx)
                if acc >= amount: break
        return acc, address_txs_to_spend

    def new_transaction(self, fr, to, amount):
        inputs = []
        outputs = []

        from_wallet = self.get_wallets().get(fr, False)
        if not from_wallet:
            print("There is no such an address: " + fr)
            return

        acc, address_txs_to_spend = self.acc_verify(self.pub_key_hash(from_wallet.public_key_bytes), amount)

        if acc < amount:
            print('Not enough units...')
            return

        for tx in address_txs_to_spend:
            inputs.append(TransactionInput(tx[0], tx[1], None, from_wallet.public_key, from_wallet.public_key_bytes))

        output = TransactionOutput(amount, None)
        output.public_key_hash = output.lock(to, self.version, self.addr_check_sum_len)
        outputs.append(output)

        if acc > amount:
            output = TransactionOutput(acc - amount, None)
            output.public_key_hash = output.lock(fr, self.version, self.addr_check_sum_len)
            outputs.append(output)

        # reward
        print("Reward to {} for mining the block: {}".format(to, str(self.sign_unit)))
        output = TransactionOutput(self.sign_unit, None)
        output.public_key_hash = output.lock(fr, self.version, self.addr_check_sum_len)
        outputs.append(output)

        tx = Transaction(None, inputs, outputs)
        tx.id = self.transaction_hash(tx)
        tx = self.sign_transaction(tx, from_wallet.private_key)
        return tx

    def find_transaction(self, id):
        blocks = self.get_blocks()
        if blocks is None:
            return None
        for serialized_block in blocks:
            block = self.de_serialize(serialized_block.serializedBlock)
            for tx in block.transactions:
                if tx.id == id:
                    return tx
        return None

    def pow(self, block):
        # hash - 256 bits
        # target bits - 25 bits -> target instance that is smaller than the hash (not valid proof of work)
        # we need to calculate new hash(for new block) with (nonce + new block info) to be smaller than target instance
        target = int(str(int(10 ** round((256 - self.target_bits) / 4))), 16)  # target bits -> target instance
        max_int64 = int(9223372036854775807)  # 64 bits (8 bytes). To prevent overflow
        nonce, data_hash = 0, ''
        # for tx in block.transactions:
        #     all_ids_txs_in_one += tx.id
        # tx_hash = hashlib.sha256(all_ids_txs_in_one.encode('utf-8')).hexdigest()
        while nonce < max_int64:
            all_in_one = block.txsRootNode + '{:x}'.format(int(nonce))
            data_hash = hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()
            # cmp
            if ((int(data_hash, 16) > target) - (int(data_hash, 16) < target)) == -1:
                break
            else:
                nonce += 1
        return data_hash, nonce

    def test_pow(self, data, nonceToCheck=None):
        target = int(str(int(10 ** round((256 - self.target_bits) / 4))), 16)  # target bits -> target instance
        max_int64 = int(9223372036854775807)  # 64 bits (8 bytes). To prevent overflow
        nonce = 0
        orig_hash = hashlib.sha256(
            (data + '{:x}'.format(int(nonceToCheck)) if nonceToCheck is not None else "").encode('utf-8')).hexdigest()
        data_hash = ''
        while nonce < max_int64:
            all_in_one = data + '{:x}'.format(int(nonce)) if nonce != 0 else ""
            data_hash = hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()
            # cmp
            if ((int(data_hash, 16) > target) - (int(data_hash, 16) < target)) == -1:
                break
            else:
                nonce += 1
        print("Original hash: {}, Hash with nonce: {}, Nonce: {}, Nonce(hex): {}".format(orig_hash, data_hash, nonce,
                                                                                         '{:x}'.format(int(nonce))))

    # check if proof of work is valid for a single block
    def check_block_pow(self, block):
        all_ids_txs_in_one = ''
        for tx in block.transactions:
            all_ids_txs_in_one += tx.id
        tx_hash = hashlib.sha256(all_ids_txs_in_one.encode('utf-8')).hexdigest()
        all_in_one = str(block.block.time_stamp) + str(tx_hash) + str(block.block.prev_hash) + '{:x}'.format(int(block.nonce))
        target = int(str(int(10 ** round((256 - self.target_bits) / 4))), 16)
        data_hash = hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()
        return ((int(data_hash, 16) > target) - (int(data_hash, 16) < target)) == -1

    def check_pow(self):
        blocks = self.get_blocks()
        if blocks is None:
            return None
        for serialized_block in blocks:
            block = self.de_serialize(serialized_block.serializedBlock)
            print('Proof of work: ' + 'valid' if self.check_block_pow(block) else 'invalid')
            print('\n')

    def new_block(self, transactions, mk_hash, prev_hash):
        block = Block(datetime.now(), transactions, mk_hash, prev_hash, '', '')
        block.hash, block.nonce = self.pow(block)
        return block

    def set_hash(self, block):
        all_ids_txs_in_one = ''
        for tx in block.transactions:
            all_ids_txs_in_one += tx.id
        tx_hash = hashlib.sha256(all_ids_txs_in_one.encode('utf-8')).hexdigest()
        all_in_one = str(block.time_stamp) + str(tx_hash) + str(block.prev_hash) + '{:x}'.format(int(block.nonce))
        return hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()

    def add_block(self, transactions):
        print('Mining the block...')
        for tx in transactions:
            if self.verify_transaction(tx) is False:
                print('Invalid transaction')
                return False
        txs_hashes = self.merkle_tree.get_txs_hashes(transactions)
        mk_hash = self.merkle_tree.find_merkle_hash(txs_hashes)
        last_block = models.LastBlock.query.first()
        prev_block = models.Blocks.query.filter_by(hash=last_block.hash).first()
        if prev_block is None:
            print("Blockchain is not initialized yet.")
            return
        prev_block = self.de_serialize(prev_block.serializedBlock)
        new_block = self.new_block(
            transactions,
            mk_hash,
            prev_block.hash
        )
        serialized_block = self.serialize(new_block)
        # de_serialized_block = self.deSerialize(serialized_block)
        db_block = models.Blocks(hash=new_block.hash, txsRootNode=new_block.txsRootNode, serializedBlock=serialized_block)
        db.session.add(db_block)
        db_last_block = models.LastBlock.query.first()
        if db_last_block is None:
            db_last_block = models.LastBlock(hash=new_block.hash)
            db.session.add(db_last_block)
        else:
            db_last_block.hash = new_block.hash
        db.session.commit()
        return True

    def send(self, fr, to, amount):
        print('Sending data=' + str(amount) + ' from ' + fr + ' to ' + to)
        transaction = self.new_transaction(fr, to, amount)
        if transaction:
            block_is_added = self.add_block([transaction])
            # update unspent transactions outputs
            if not self.is_coin_base(transaction):
                self.chain_state.update_utxo(transaction)
            if block_is_added:
                print('Success.')
            else:
                print('Error.')

    def get_balance(self, address):
        wallets = self.get_wallets()
        wallet = wallets.get(address, False)
        if not wallet:
            print("There is no such an address: " + address)
            return
        balance = 0
        unspent_txs = self.unspent_txs(self.pub_key_hash(wallet.public_key_bytes))
        if unspent_txs is None:
            return
        for tx in unspent_txs:
            balance += int(tx[2].val)
        print('Balance of ' + address + ': ' + str(balance))

    def show_blocks(self):
        print('All blocks:')
        print('\n')
        blocks = self.get_blocks()
        if blocks is None:
            return None
        for index, serialized_block in enumerate(blocks):
            block = self.de_serialize(serialized_block.serializedBlock)
            print('Block Id: ' + str(index))
            print('Hash: ' + block.hash)
            print('Nonce: ' + str(block.nonce))
            print('Pr.hash: %s' % (block.prev_hash if block.prev_hash else 'none'))
            print('Time: ' + str(block.time_stamp))
            print('Transactions(count): ' + str(len(block.transactions)))
            for tx_index, transaction in enumerate(block.transactions):
                print(' - Transaction ' + str(tx_index + 1) + '(coin base transaction)' if self.is_coin_base(
                    transaction) else '')
                print(' - Transaction id:' + str(transaction.id))
                print(' - Inputs (count):' + str(len(transaction.inputs)))
                print(' - Outputs (count):' + str(len(transaction.outputs)))
                print(' ---')
                for input_index, input in enumerate(transaction.inputs):
                    print(' -> Input ' + str(input_index))
                    print(' -> Input id:' + str(input.id))
                    print(' -> Input sig:' + str(input.sig))
                    print(' -> Relative id of output:' + str(input.output))
                    if not self.is_coin_base(transaction):
                        print(' -> Input pub key (elliptic curve):' + 'X: {}, Y: {}'.format(str(input.public_key.x),
                                                                                            str(input.public_key.y)))
                        print(' -> Input pub key(bytes):' + str(input.public_key_bytes))
                    print(' ---')
                for output_index, output in enumerate(transaction.outputs):
                    print(' -> Output ' + str(output_index))
                    print(' -> Output value:' + str(output.val))
                    print(' -> Output public key(bytes):' + str(output.public_key_hash))
            print('\n')

    def get_blocks(self):
        if self.is_system_initialized():
            return models.Blocks.query.all()
        else:
            print("Blockchain is not initialized yet.")
            return None

    def is_system_initialized(self):
        db_block = models.Blocks.query.first()
        if db_block is not None:
            return True
        else:
            return False

    def init_system(self, to):
        if self.is_system_initialized():
            print("Blockchain system is already initialized.")
        else:
            print('Mining the Genesis Block with data "Genesis Block"...')
            transactions = [self.coin_base_tx(to, "Genesis block")]
            txs_hashes = self.merkle_tree.get_txs_hashes(transactions)
            mk_hash = self.merkle_tree.find_merkle_hash(txs_hashes)
            genesis_block = self.new_block(transactions, mk_hash, '')
            serialized_genesis_block = self.serialize(genesis_block)
            db_block = models.Blocks(hash=genesis_block.hash, txsRootNode=genesis_block.txsRootNode, serializedBlock=serialized_genesis_block)
            db.session.add(db_block)
            db_last_block = models.LastBlock(hash=genesis_block.hash)
            db.session.add(db_last_block)
            db.session.commit()
            print('Success.')
            blocks = self.get_blocks()
            if blocks is None:
                print("Failed reindex.")
            self.chain_state.reindex(blocks, self.de_serialize)

    def is_serialized_soinbase_tx(self, jsonTx):
        return len(jsonTx["inputs"]) == 1 and json.loads(jsonTx["inputs"][0])["id"] == 0 and json.loads(jsonTx["inputs"][0])[
            "output"] == -1

    def serialize(self, block):
        json_block = {
            "timeStamp": block.time_stamp.isoformat(),
            "transactions": [],
            "txsRootNode": block.txsRootNode,
            "prevHash": block.prev_hash,
            "hash": block.hash,
            "nonce": block.nonce
        }
        for tx in block.transactions:
            json_tx = {
                "id": tx.id,
                "inputs": [],
                "outputs": []
            }
            for v_in in tx.inputs:
                json_vin = {
                    "id": v_in.id,
                    "output": v_in.output,
                    "sig": (DEREncoder.encode_signature(v_in.sig["r"], v_in.sig["s"])).decode(
                        "latin1") if not self.is_coin_base(tx) else None,
                    "publicKey": PEMEncoder.encode_public_key(v_in.public_key) if not self.is_coin_base(tx) else v_in.public_key,
                    "publicKeyBytes": (v_in.public_key_bytes).decode("latin1") if not self.is_coin_base(
                        tx) else v_in.public_key_bytes
                }
                json_tx["inputs"].append(json.dumps(json_vin))
            for v_out in tx.outputs:
                jsonv_out = {
                    "val": v_out.val,
                    "publicKeyHash": (v_out.public_key_hash).decode("latin1")
                }
                json_tx["outputs"].append(json.dumps(jsonv_out))
            json_block["transactions"].append(json.dumps(json_tx))
        json_data = json.dumps(json_block)
        return json_data

    def de_serialize(self, json_data):
        json_block = json.loads(json_data)
        block_tx = []
        for tx in json_block["transactions"]:
            json_tx = json.loads(tx)
            block_inputs = []
            for input in json_tx["inputs"]:
                json_input = json.loads(input)
                sig = DEREncoder.decode_signature(json_input["sig"].encode("latin1")) if json_input["sig"] is not None else None
                block_inputs.append(
                    TransactionInput(
                        json_input["id"],
                        json_input["output"],
                        {'r': sig[0], 's': sig[1]} if not self.is_serialized_soinbase_tx(json_tx) else sig,
                        PEMEncoder.decode_public_key(json_input["publicKey"], curve=curve.P256) if not self.is_serialized_soinbase_tx(json_tx) else json_input["publicKey"],
                        json_input["publicKeyBytes"].encode("latin1") if not self.is_serialized_soinbase_tx(json_tx) else json_input["publicKeyBytes"]
                    )
                )
            block_outputs = []
            for outputs in json_tx["outputs"]:
                json_output = json.loads(outputs)
                block_outputs.append(
                    TransactionOutput(
                        json_output["val"],
                        json_output["publicKeyHash"].encode("latin1")
                    )
                )
            block_tx.append(
                Transaction(
                    json_tx["id"],
                    block_inputs,
                    block_outputs
                )
            )
        block = Block(
            datetime.fromisoformat(json_block["timeStamp"]),
            block_tx,
            json_block["txsRootNode"],
            json_block["prevHash"],
            json_block["hash"],
            json_block["nonce"]
        )
        return block


class BlockChain(Chain):
    def __init__(self):
        super(BlockChain, self).__init__()
        print('BlockChain instance is created.')
        if self.is_system_initialized():
            print("Blockchain system is already initialized.")
            blocks = self.get_blocks()
            if blocks is None:
                print("Failed reindex.")
            self.chain_state.reindex(blocks, self.de_serialize)
        else:
            print('Blockchain is not initialized yet.')
