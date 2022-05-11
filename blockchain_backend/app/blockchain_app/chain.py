import hashlib
import os.path
from fastecdsa import curve, ecdsa, keys
from fastecdsa.encoding.pem import PEMEncoder
from fastecdsa.encoding.der import DEREncoder
from base58 import b58encode
from datetime import datetime
import json

from .errors import BcSystemError
from .wallets import Wallet
from .transactions import Transaction, TransactionInput, TransactionOutput
from .block import Block
from .merkle_tree import MerkleTree
from .chainstate import ChainState

from . import models


class Chain(object):
    def __init__(self, db, wallets_store):
        # database instance (Flask-SQLAlchemy)
        # you can use your own database instance / separate SQLAlchemy
        self.db = db
        # wallets store location
        self.wallets_store = wallets_store
        # target_bits - we can change target bits due to control complexity of making new blocks
        # self.target_bits = int(24)
        self.target_bits = int(12)
        # sign_unit - reward value for mining
        self.sign_unit = int(10)
        # addr_check_sum_len - default length of the address checksum
        self.addr_check_sum_len = int(4)
        # version - target network is the mainnet, version = 0x00
        self.version = bytes(0x00)
        # unspent transaction outputs - cache
        self.chain_state = ChainState(db)
        self.merkle_tree = MerkleTree()

    # System

    def init_system(self, to):
        if self.is_system_initialized():
            print("Blockchain system is already initialized.")
        else:
            print('Mining the Genesis Block with data "Genesis Block"...')
            transactions = [self.coin_base_tx(to, "Genesis block")]
            txs_hashes = self.merkle_tree.get_txs_hashes(transactions)
            mk_hash = self.merkle_tree.find_merkle_hash(txs_hashes)
            genesis_block = self.new_block(transactions, mk_hash, '')
            serialized_genesis_block = self.serialize_block(genesis_block)
            db_block = models.Blocks(hash=genesis_block.hash, txsRootNode=genesis_block.txsRootNode,
                                     serializedBlock=serialized_genesis_block)
            self.db.session.add(db_block)
            db_last_block = models.LastBlock(hash=genesis_block.hash)
            self.db.session.add(db_last_block)
            self.db.session.commit()
            print('Success.')
            blocks = self.get_blocks()
            if blocks is None:
                print("Failed reindex.")
            self.chain_state.reindex(blocks, self.de_serialize_block)

    def is_system_initialized(self):
        db_block = models.Blocks.query.first()
        if db_block is None:
            return False
        return True

    def clean_system(self):
        self.db.session.query(models.Blocks).delete()
        self.db.session.query(models.LastBlock).delete()
        self.db.session.query(models.UTXO).delete()
        self.db.session.query(models.TXPool).delete()
        self.db.session.commit()
        data = self.clean_wallets_store()
        if isinstance(data, Exception):
            return data
        cleaned_wallets = data
        return cleaned_wallets

    def create_wallets_store(self):
        wallets_bcw = os.path.isfile(self.wallets_store)
        try:
            if self.is_system_initialized():
                if wallets_bcw:
                    return True
                else:
                    return False
            else:
                wallets = {}
                with open(self.wallets_store, 'w') as f:
                    json.dump(wallets, f)
                return True
        except:
            return False

    def clean_wallets_store(self):
        try:
            wallets = {}
            with open(self.wallets_store, 'w') as f:
                json.dump(wallets, f)
            return True
        except:
            return False

    # Wallets

    def new_wallet(self):
        try:
            pr_key, pub_key, pub_key_bytes = self.new_key_pair()
            wallet = Wallet(pr_key, pub_key, pub_key_bytes)
            address = str(self.get_address(wallet), 'utf-8')
            save_wallet = self.save_wallet(wallet, address)
            if not save_wallet:
                raise BcSystemError("Wallet", "Failed to save wallet...")
            return address
        except BcSystemError as error:
            return error

    def save_wallet(self, wallet, address):
        wallets_bcw = os.path.isfile(self.wallets_store)
        try:
            if wallets_bcw:
                with open(self.wallets_store, 'r') as f:
                    serialized_wallets = json.load(f)
                wallets = self.de_serialize_wallets(serialized_wallets)
                wallets[address] = wallet
                new_serialized_wallets = self.serialize_wallets(wallets)
                with open(self.wallets_store, 'w') as f:
                    json.dump(new_serialized_wallets, f)
                return True
            else:
                return False
        except:
            return False

    def get_wallets(self):
        try:
            wallets_bcw = os.path.isfile(self.wallets_store)
            if not wallets_bcw:
                # return None, "There are no any wallets."
                raise BcSystemError("Wallets", "There are no any wallets.")
            with open(self.wallets_store, 'r') as f:
                serialized_wallets = json.load(f)
            return self.de_serialize_wallets(serialized_wallets)
        except BcSystemError as error:
            return error

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

    # Transactions

    def sign_transaction(self, transaction, private_key):
        try:
            if self.is_coin_base(transaction):
                # return None, "Transaction is coinbase."
                raise BcSystemError("Transaction", "Transaction is coinbase.")
            prev_transactions = {}
            for input in transaction.inputs:
                prev_transaction = self.find_transaction(input.id)
                if prev_transaction is None:
                    # return None, "Failed to find previous transaction"
                    raise BcSystemError("Transaction", "Failed to find previous transaction.")
                prev_transactions[prev_transaction.id] = prev_transaction
            return self.sign(transaction, prev_transactions, private_key)
        except BcSystemError as error:
            return error

    def sign(self, transaction, prev_transactions, private_key):
        try:
            for input in transaction.inputs:
                if not (input.id in prev_transactions and prev_transactions[input.id].id):
                    # return None, "Previous transaction is not correct"
                    raise BcSystemError("Transaction", "Previous transaction is not correct.")
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
        except BcSystemError as error:
            return error

    def verify_transaction(self, transaction):
        if self.is_coin_base(transaction):
            return False
        prev_transactions = {}
        for input in transaction.inputs:
            prev_transaction = self.find_transaction(input.id)
            if prev_transaction is None:
                return False
            prev_transactions[prev_transaction.id] = prev_transaction
        return self.verify(transaction, prev_transactions)

    def verify(self, transaction, prev_transactions):
        for input in transaction.inputs:
            if not (input.id in prev_transactions and prev_transactions[input.id].id):
                print('Previous transaction is not correct')
                return False
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
        return Transaction(transaction.id, inputs, outputs, transaction.created)

    def transaction_hash(self, transaction):
        # all_in_one = ''
        # for tx_input in transaction.inputs:
        #     all_in_one += str(tx_input.id) + str(tx_input.output) + str(tx_input.sig) + str(tx_input.public_key)
        # for tx_output in transaction.outputs:
        #     all_in_one += str(tx_output.val) + str(tx_output.public_key_hash)
        tx_hash = hashlib.sha256(transaction.__repr__().encode('utf-8')).hexdigest()
        return tx_hash

    def coin_base_tx(self, to, data):
        tx_input = TransactionInput(0, -1, None, data, data)
        tx_output = TransactionOutput(self.sign_unit, None)
        tx_output.public_key_hash = tx_output.lock(to, self.version, self.addr_check_sum_len)
        tr = Transaction(0, [tx_input], [tx_output], datetime.now())
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
        try:
            inputs = []
            outputs = []

            # wallets, error = self.get_wallets()
            # if wallets is None and error != "":
            #     return None, error

            data = self.get_wallets()
            if isinstance(data, Exception):
                return data

            wallets = data

            from_wallet = wallets.get(fr, False)
            if not from_wallet:
                # print("There is no such an address: " + fr)
                raise BcSystemError("Address", "There is no such an address: " + fr)
                # return None, "There is no such an address: " + fr

            acc, address_txs_to_spend = self.acc_verify(self.pub_key_hash(from_wallet.public_key_bytes), amount)

            if acc < amount:
                # print('Not enough units...')
                raise BcSystemError("Units", "Not enough units...")
                # return None, "Not enough units..."

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
            # if is_last:
            #     print("Reward to {} for mining the block: {}".format(fr, str(self.sign_unit)))
            #     output = TransactionOutput(self.sign_unit, None)
            #     output.public_key_hash = output.lock(fr, self.version, self.addr_check_sum_len)
            #     outputs.append(output)

            tx = Transaction(None, inputs, outputs, datetime.now())
            tx.id = self.transaction_hash(tx)
            data = self.sign_transaction(tx, from_wallet.private_key)
            if isinstance(data, Exception):
                return data
            tx = data
            return tx
        except BcSystemError as error:
            return error

    def reward_transaction(self, to):
        try:
            # wallets, error = self.get_wallets()
            # if wallets is None and error != "":
            #     return None, error
            data = self.get_wallets()
            if isinstance(data, Exception):
                return data
            wallets = data
            from_wallet = wallets.get(to, False)
            if not from_wallet:
                # print("There is no such an address: " + fr)
                # return None, "There is no such an address: " + to
                raise BcSystemError("Address", "There is no such an address: " + to)
            inputs = []
            outputs = []
            print("Reward to {} for mining the block: {}".format(to, str(self.sign_unit)))
            output = TransactionOutput(self.sign_unit, None)
            output.public_key_hash = output.lock(to, self.version, self.addr_check_sum_len)
            outputs.append(output)
            tx = Transaction(None, inputs, outputs, datetime.now())
            tx.id = self.transaction_hash(tx)
            data = self.sign_transaction(tx, from_wallet.private_key)
            if isinstance(data, Exception):
                return data
            tx = data
            return tx
        except BcSystemError as error:
            return error

    def find_transaction(self, id):
        blocks = self.get_blocks()
        if blocks is None:
            return None
        for serialized_block in blocks:
            block = self.de_serialize_block(serialized_block.serializedBlock)
            for tx in block.transactions:
                if tx.id == id:
                    return tx
        return None

    def get_from_pool(self, fr):
        try:
            pined_transactions = models.TXPool.query.filter(models.TXPool.fromAddr == fr).all()
            if len(pined_transactions) > 0:
                # return None, "Your wallet is locked due to awaiting for previous transaction confirmation."
                raise BcSystemError("Pool", "Your wallet is locked due to awaiting for previous transaction confirmation.")
            return pined_transactions
        except BcSystemError as error:
            return error

    def get_all_pool(self):
        return models.TXPool.query.all()

    def send(self, fr, to, amount):
        # fr_pined_transactions, error = self.get_from_pool(fr)
        data = self.get_from_pool(fr)
        if isinstance(data, Exception):
            print("{}: {}".format(data.error_type, data.error_message))
            return
        fr_pined_transactions = data
        # if fr_pined_transactions is None and error != "":
        #     print(error)
        print('Sending data=' + str(amount) + ' from ' + fr + ' to ' + to)
        # transaction, error = self.new_transaction(fr, to, amount)

        data = self.new_transaction(fr, to, amount)
        if isinstance(data, Exception):
            pool_tx = models.TXPool(txID=None, fromAddr=fr,
                                    toAddr=to, amount=amount,
                                    serializedTransaction=None, error=True, errorText="{}: {}".format(data.error_type, data.error_message))
            self.db.session.add(pool_tx)
            self.db.session.commit()
            print("{}: {}".format(data.error_type, data.error_message))
            return
        transaction = data
        # add transaction to pull
        serialized_transaction = self.serialize_transaction(transaction, True)
        pool_tx = models.TXPool(txID=transaction.id, fromAddr=fr,
                                toAddr=to, amount=amount,
                                serializedTransaction=json.dumps(serialized_transaction), error=False,
                                errorText=None)
        self.db.session.add(pool_tx)
        self.db.session.commit()
        print("Transaction is added to pool.")

    def get_balance(self, address):
        try:
            # wallets, error = self.get_wallets()
            # if wallets is None and error != "":
            #     return None, error
            data = self.get_wallets()
            if isinstance(data, Exception):
                return data
            wallets = data
            wallet = wallets.get(address, False)
            if not wallet:
                # return None, "There is no such an address: " + address
                raise BcSystemError("Address", "There is no such an address: " + address)
            balance = 0
            unspent_txs = self.unspent_txs(self.pub_key_hash(wallet.public_key_bytes))
            if unspent_txs is None:
                # return None, "Failed to get unspent transactions."
                raise BcSystemError("Transactions", "Failed to get unspent transactions.")
            for tx in unspent_txs:
                balance += int(tx[2].val)
            print('Balance of ' + address + ': ' + str(balance))
            return balance
        except BcSystemError as error:
            return error

    def is_serialized_soinbase_tx(self, jsonTx):
        return len(jsonTx["inputs"]) == 1 and json.loads(jsonTx["inputs"][0])["id"] == 0 and \
               json.loads(jsonTx["inputs"][0])[
                   "output"] == -1

    def serialize_transaction(self, transaction, to_txs_pool=False):
        json_tx = {
            "id": transaction.id,
            "inputs": [],
            "outputs": [],
            "created": transaction.created.isoformat()
        }
        if not to_txs_pool:
            json_tx["included_in_block"] = transaction.included_in_block.isoformat()
        for v_in in transaction.inputs:
            json_vin = {
                "id": v_in.id,
                "output": v_in.output,
                "sig": (DEREncoder.encode_signature(v_in.sig["r"], v_in.sig["s"])).decode(
                    "latin1") if not self.is_coin_base(transaction) else None,
                "publicKey": PEMEncoder.encode_public_key(v_in.public_key) if not self.is_coin_base(
                    transaction) else v_in.public_key,
                "publicKeyBytes": (v_in.public_key_bytes).decode("latin1") if not self.is_coin_base(
                    transaction) else v_in.public_key_bytes
            }
            json_tx["inputs"].append(json.dumps(json_vin))
        for v_out in transaction.outputs:
            jsonv_out = {
                "val": v_out.val,
                "publicKeyHash": (v_out.public_key_hash).decode("latin1")
            }
            json_tx["outputs"].append(json.dumps(jsonv_out))
        return json_tx

    def de_serialize_transaction(self, transaction, from_txs_pool=False):
        json_tx = json.loads(transaction)
        block_inputs = []
        for input in json_tx["inputs"]:
            json_input = json.loads(input)
            sig = DEREncoder.decode_signature(json_input["sig"].encode("latin1")) if json_input[
                                                                                         "sig"] is not None else None
            block_inputs.append(
                TransactionInput(
                    json_input["id"],
                    json_input["output"],
                    {'r': sig[0], 's': sig[1]} if not self.is_serialized_soinbase_tx(json_tx) else sig,
                    PEMEncoder.decode_public_key(json_input["publicKey"],
                                                 curve=curve.P256) if not self.is_serialized_soinbase_tx(json_tx) else
                    json_input["publicKey"],
                    json_input["publicKeyBytes"].encode("latin1") if not self.is_serialized_soinbase_tx(json_tx) else
                    json_input["publicKeyBytes"]
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
        if from_txs_pool:
            return Transaction(
                json_tx["id"],
                block_inputs,
                block_outputs,
                datetime.fromisoformat(json_tx["created"]),
            )
        return Transaction(
            json_tx["id"],
            block_inputs,
            block_outputs,
            datetime.fromisoformat(json_tx["created"]),
            datetime.fromisoformat(json_tx["included_in_block"])
        )

    # Blocks

    def pow(self, block):
        # zhash - 256 bits
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

    # def test_pow(self, data, nonceToCheck=None):
    #     target = int(str(int(10 ** round((256 - self.target_bits) / 4))), 16)  # target bits -> target instance
    #     max_int64 = int(9223372036854775807)  # 64 bits (8 bytes). To prevent overflow
    #     nonce = 0
    #     orig_hash = hashlib.sha256(
    #         (data + '{:x}'.format(int(nonceToCheck)) if nonceToCheck is not None else "").encode('utf-8')).hexdigest()
    #     data_hash = ''
    #     while nonce < max_int64:
    #         all_in_one = data + '{:x}'.format(int(nonce)) if nonce != 0 else ""
    #         data_hash = hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()
    #         # cmp
    #         if ((int(data_hash, 16) > target) - (int(data_hash, 16) < target)) == -1:
    #             break
    #         else:
    #             nonce += 1
    #     print("Original hash: {}, Hash with nonce: {}, Nonce: {}, Nonce(hex): {}".format(orig_hash, data_hash, nonce,
    #                                                                                      '{:x}'.format(int(nonce))))

    # check if proof of work is valid for a single block
    def check_block_pow(self, block):
        # all_ids_txs_in_one = ''
        # for tx in block.transactions:
        #     all_ids_txs_in_one += tx.id
        # tx_hash = hashlib.sha256(all_ids_txs_in_one.encode('utf-8')).hexdigest()
        # all_in_one = str(block.block.time_stamp) + str(tx_hash) + str(block.block.prev_hash) + '{:x}'.format(
        #     int(block.nonce))
        all_in_one = block.txsRootNode + '{:x}'.format(int(block.nonce))
        data_hash = hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()
        target = int(str(int(10 ** round((256 - self.target_bits) / 4))), 16)
        return ((int(data_hash, 16) > target) - (int(data_hash, 16) < target)) == -1

    def check_pow(self):
        blocks = self.get_blocks()
        if blocks is None:
            return None
        for serialized_block in blocks:
            block = self.de_serialize_block(serialized_block.serializedBlock)
            print('Proof of work: ' + 'valid' if self.check_block_pow(block) else 'invalid')
            print('\n')

    def new_block(self, transactions, mk_hash, prev_hash):
        for transaction in transactions:
            transaction.included_in_block = datetime.now()
        block = Block(datetime.now(), transactions, mk_hash, prev_hash, '', '')
        block.hash, block.nonce = self.pow(block)
        return block

    # def set_hash(self, block):
    #     all_ids_txs_in_one = ''
    #     for tx in block.transactions:
    #         all_ids_txs_in_one += tx.id
    #     tx_hash = hashlib.sha256(all_ids_txs_in_one.encode('utf-8')).hexdigest()
    #     all_in_one = str(block.time_stamp) + str(tx_hash) + str(block.prev_hash) + '{:x}'.format(int(block.nonce))
    #     return hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()

    def add_block(self, transactions):
        for tx in transactions:
            if not self.verify_transaction(tx):
                print('Invalid transaction')
                return False
        txs_hashes = self.merkle_tree.get_txs_hashes(transactions)
        mk_hash = self.merkle_tree.find_merkle_hash(txs_hashes)
        last_block = models.LastBlock.query.first()
        prev_block = models.Blocks.query.filter_by(hash=last_block.hash).first()
        if prev_block is None:
            print("Blockchain is not initialized yet.")
            return False
        prev_block = self.de_serialize_block(prev_block.serializedBlock)
        new_block = self.new_block(
            transactions,
            mk_hash,
            prev_block.hash
        )
        serialized_block = self.serialize_block(new_block)
        # de_serialized_block = self.deSerialize(serialized_block)
        db_block = models.Blocks(hash=new_block.hash, txsRootNode=new_block.txsRootNode,
                                 serializedBlock=serialized_block)
        self.db.session.add(db_block)
        db_last_block = models.LastBlock.query.first()
        if db_last_block is None:
            db_last_block = models.LastBlock(hash=new_block.hash)
            self.db.session.add(db_last_block)
        else:
            db_last_block.hash = new_block.hash
        self.db.session.commit()
        return True

    def mine_block(self, who, tx_count=5):
        print('Mining the block...')
        pined_transactions = models.TXPool.query.filter(models.TXPool.error == False).limit(tx_count).all()
        if pined_transactions is None:
            print('There is no new transactions to mine new block.')
            return
        transactions = []
        for pined_transaction in pined_transactions:
            # serialized_transaction = json.loads(pined_transaction.serializedTransaction)
            transaction = self.de_serialize_transaction(pined_transaction.serializedTransaction, True)
            transactions.append(transaction)
        # reward_tx, error = self.reward_transaction(who)
        data = self.reward_transaction(who)
        if isinstance(data, Exception):
            print("{}: {}".format(data.error_type, data.error_message))
            return
        # if reward_tx is None and error != "":
        #     print(error)
        #     return
        reward_tx = data
        transactions.append(reward_tx)
        block_is_added = self.add_block(transactions)
        if block_is_added:
            # update unspent transactions outputs
            for transaction in transactions:
                if not self.is_coin_base(transaction):
                    self.chain_state.update_utxo(transaction)
            unpined_transactions_ids = []
            for pined_transaction in pined_transactions:
                unpined_transactions_ids.append(pined_transaction.txID)
            self.db.session.query(models.TXPool).filter(models.TXPool.txID.in_(unpined_transactions_ids)).delete()
            self.db.session.commit()
            print('Success.')
        else:
            print('Error.')

    def get_blocks(self):
        if self.is_system_initialized():
            return models.Blocks.query.all()
        else:
            print("Blockchain is not initialized yet.")
            return None

    def show_blocks(self):
        print('All blocks:')
        print('\n')
        blocks = self.get_blocks()
        if blocks is None:
            return None
        for index, serialized_block in enumerate(blocks):
            block = self.de_serialize_block(serialized_block.serializedBlock)
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

    def serialize_block(self, block):
        json_block = {
            "timeStamp": block.time_stamp.isoformat(),
            "transactions": [],
            "txsRootNode": block.txsRootNode,
            "prevHash": block.prev_hash,
            "hash": block.hash,
            "nonce": block.nonce
        }
        for tx in block.transactions:
            json_tx = self.serialize_transaction(tx)
            json_block["transactions"].append(json.dumps(json_tx))
        json_data = json.dumps(json_block)
        return json_data

    def de_serialize_block(self, json_data):
        json_block = json.loads(json_data)
        block_tx = []
        for tx in json_block["transactions"]:
            transaction = self.de_serialize_transaction(tx)
            block_tx.append(
                transaction
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
