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


# from app import db
# from models import *

class Wallet(object):
    def __init__(self, private_key, public_key, public_key_bytes):
        self.private_key = private_key
        self.public_key = public_key
        self.public_key_bytes = public_key_bytes


class Transaction(object):
    def __init__(self, id, v_in, v_out):
        self.id = id
        self.v_in = v_in
        self.v_out = v_out

    def __repr__(self):
        v_in_representation = []
        for v_in in self.v_in:
            v_in_representation.append(v_in.__repr__)
        v_out_representation = []
        for v_out in self.v_out:
            v_out_representation.append(v_out.__repr__)
        return "Transaction: id = {}, vIn = {}, vOut = {}".format(self.id, v_in_representation, v_out_representation)


class TransactionInput(object):
    def __init__(self, id, v_out, sig, pub_key, pub_key_bytes):
        self.id = id
        self.v_out = v_out
        self.sig = sig
        self.pub_key = pub_key
        self.pub_key_bytes = pub_key_bytes

    def __repr__(self):
        return "TransactionInput: " \
               "id = {}, vOut = {}, " \
               "sig = {}, pubKey = {}, " \
               "pubKeyBytes = {}".format(self.id, self.v_out, self.sig, self.pub_key, self.pub_key_bytes)

    def uses_key(self, pub_key, pub_key_hash):
        return pub_key == pub_key_hash


class TransactionOutput(object):
    def __init__(self, val, pub_key_hash):
        self.val = val
        self.pub_key_hash = pub_key_hash

    def __repr__(self):
        return "TransactionOutput: val = {}, pubKeyHash = {}".format(self.val, self.pub_key_hash)

    def lock(self, address, version, addr_check_sum_len):
        pub_key_hash = b58decode(address)
        pub_key_hash = pub_key_hash[len(version): len(pub_key_hash) - addr_check_sum_len]
        return pub_key_hash

    def is_locked_with_key(self, pub_key_hash):
        return pub_key_hash == self.pub_key_hash


class Block(object):
    def __init__(self, time_stamp, transactions, prev_hash, hash, nonce):
        self.time_stamp = time_stamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.hash = hash
        self.nonce = nonce


class Chain(object):
    def __init__(self):
        # self.blocks = []
        # self.wallets = {}
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

    def new_wallet(self):
        pr_key, pub_key, pub_key_bytes = self.new_key_pair()
        wallet = Wallet(pr_key, pub_key, pub_key_bytes)
        address = str(self.get_address(wallet), 'utf-8')
        self.save_wallet(wallet, address)
        # self.wallets[address] = wallet
        print('Your new address: ' + address)
        return address

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
        for v_in in transaction.v_in:
            prev_transaction = self.find_transaction(v_in.id)
            if prev_transaction is None:
                print('Failed to find previous transaction')
                return
            prev_transactions[prev_transaction.id] = prev_transaction
        return self.sign(transaction, prev_transactions, private_key)

    def sign(self, transaction, prev_transactions, private_key):
        for v_in in transaction.v_in:
            if not (v_in.id in prev_transactions and prev_transactions[v_in.id].id):
                print('Previous transaction is not correct')
                return
        tx_trimmed_copy = self.tx_trimmed_copy(transaction)
        for index, v_in in enumerate(tx_trimmed_copy.v_in):
            prev_transaction = prev_transactions[v_in.id]
            v_in.sig = None
            v_in.pub_key_bytes = prev_transaction.v_out[v_in.v_out].pub_key_hash
            data_to_sign = tx_trimmed_copy.__repr__()
            r, s = ecdsa.sign(data_to_sign, private_key)
            transaction.v_in[index].sig = {'r': r, 's': s}
            v_in.pub_key = None
        return transaction

    def verify_transaction(self, transaction):
        if self.is_coin_base(transaction):
            return
        prev_transactions = {}
        for v_in in transaction.v_in:
            prev_transaction = self.find_transaction(v_in.id)
            if prev_transaction is None:
                print('Failed to find previous transaction')
                return
            prev_transactions[prev_transaction.id] = prev_transaction
        return self.verify(transaction, prev_transactions)

    def verify(self, transaction, prev_transactions):
        for v_in in transaction.v_in:
            if not (v_in.id in prev_transactions and prev_transactions[v_in.id].id):
                print('Previous transaction is not correct')
                return
        tx_trimmed_copy = self.tx_trimmed_copy(transaction)
        for index, v_in in enumerate(transaction.v_in):
            prev_transaction = prev_transactions[v_in.id]
            tx_trimmed_copy.v_in[index].sig = None
            tx_trimmed_copy.v_in[index].pub_key_bytes = prev_transaction.v_out[v_in.v_out].pub_key_hash
            if v_in.sig is None:
                return False
            r, s = v_in.sig['r'], v_in.sig['s']
            data_to_verify = tx_trimmed_copy.__repr__()
            verify = ecdsa.verify((r, s), data_to_verify, v_in.pub_key)
            if verify is False:
                return False
        return True

    def tx_trimmed_copy(self, transaction):
        inputs = []
        outputs = []
        for v_in in transaction.v_in:
            inputs.append(TransactionInput(v_in.id, v_in.v_out, None, None, None))
        for v_out in transaction.v_out:
            outputs.append(TransactionOutput(v_out.val, v_out.pub_key_hash))
        return Transaction(transaction.id, inputs, outputs)

    def transaction_hash(self, transaction):
        all_in_one = ''
        for tx_in in transaction.v_in:
            all_in_one += str(tx_in.id) + str(tx_in.v_out) + str(tx_in.sig) + str(tx_in.pub_key)
        for tx_out in transaction.v_out:
            all_in_one += str(tx_out.val) + str(tx_out.pub_key_hash)
        tx_hash = hashlib.sha256(all_in_one.encode('utf-8')).hexdigest()
        return tx_hash

    def coin_base_tx(self, to, data):
        tx_in = TransactionInput(None, -1, None, data, data)
        tx_out = TransactionOutput(self.sign_unit, None)
        tx_out.pub_key_hash = tx_out.lock(to, self.version, self.addr_check_sum_len)
        tr = Transaction(0, [tx_in], [tx_out])
        tr.id = self.transaction_hash(tr)
        return tr

    def is_coin_base(self, transaction):
        return len(transaction.v_in) == 1 and transaction.v_in[0].id is None and transaction.v_in[0].v_out == -1

    def unspent_txs(self, pub_key_hash):
        unspent_txs = []
        unlocking_inputs = []
        unspent_valid_txs = []
        blocks = self.get_blocks()
        if blocks is None:
            return None
        for serialized_block in blocks:
            block = self.de_serialize(serialized_block.serializedBlock)
            for tx in block.transactions:
                for index, v_out in enumerate(tx.v_out):
                    move = True
                    for v_in in tx.v_in:
                        # if an input have any reference to the output -> tx was spent
                        if (index == v_in.v_out) and (v_in.id == tx.id):
                            move = False
                            break
                    if move is False: continue
                    # check if provided public key hash was used to lock the output
                    if v_out.is_locked_with_key(pub_key_hash):
                        # set tx itself, index of the vOut and vOut itself
                        unspent_txs.append([tx, index, v_out])
                for v_in in tx.v_in:
                    if v_in.v_out == -1: break  # first transaction
                    if v_in.uses_key(self.pub_key_hash(v_in.pub_key_bytes), pub_key_hash):
                        unlocking_inputs.append(v_in)
        # we have unlocking inputs and unspent transactions -> get valid unspent transactions
        if len(unlocking_inputs) == 0:
            unspent_valid_txs = unspent_txs
        else:
            for unspent_tx in unspent_txs:
                for _ in unlocking_inputs:
                    equals = False
                    for v_input in unlocking_inputs:
                        if (v_input.id == unspent_tx[0].id) and (v_input.v_out == unspent_tx[1]):
                            equals = True
                            break
                    if equals is False:
                        unspent_valid_txs.append(unspent_tx)
                        break
        return unspent_valid_txs

    def acc_verify(self, pub_key_hash, amount):
        unspent_txs = self.unspent_txs(pub_key_hash)
        unspent_address_txs = []
        acc = 0
        for tx in unspent_txs:
            if tx[0].v_out[tx[1]].is_locked_with_key(pub_key_hash) and (acc < amount):
                acc += tx[2].val
                unspent_address_txs.append(tx)
                if acc >= amount: break
        return acc, unspent_address_txs

    def new_transaction(self, fr, to, amount):
        inputs = []
        outputs = []

        from_wallet = self.get_wallets().get(fr, False)
        if not from_wallet:
            print("There is no such an address: " + fr)
            return

        acc, unspent_address_txs = self.acc_verify(self.pub_key_hash(from_wallet.public_key_bytes), amount)

        if acc < amount:
            print('Not enough units...')
            return

        for tx in unspent_address_txs:
            inputs.append(TransactionInput(tx[0].id, tx[1], None, from_wallet.public_key, from_wallet.public_key_bytes))

        output = TransactionOutput(amount, None)
        output.pub_key_hash = output.lock(to, self.version, self.addr_check_sum_len)
        outputs.append(output)

        if acc > amount:
            output = TransactionOutput(acc - amount, None)
            output.pub_key_hash = output.lock(fr, self.version, self.addr_check_sum_len)
            outputs.append(output)

        # reward
        print("Reward to {} for mining the block: {}".format(to, str(self.sign_unit)))
        output = TransactionOutput(self.sign_unit, None)
        output.pub_key_hash = output.lock(fr, self.version, self.addr_check_sum_len)
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
        nonce, all_ids_txs_in_one, data_hash = 0, '', ''
        for tx in block.transactions:
            all_ids_txs_in_one += tx.id
        tx_hash = hashlib.sha256(all_ids_txs_in_one.encode('utf-8')).hexdigest()
        while nonce < max_int64:
            all_in_one = str(block.time_stamp) + str(tx_hash) + str(block.prev_hash) + '{:x}'.format(int(nonce))
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

    def new_block(self, transactions, prev_hash):
        block = Block(datetime.now(), transactions, prev_hash, '', '')
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
        # prev_block = self.blocks[len(self.blocks) - 1]
        last_block = models.LastBlock.query.first()
        prev_block = models.Blocks.query.filter_by(hash=last_block.hash).first()
        if prev_block is None:
            print("Blockchain is not initialized yet.")
            return
        prev_block = self.de_serialize(prev_block.serializedBlock)
        new_block = self.new_block(
            transactions,
            self.set_hash(
                Block(
                    prev_block.time_stamp,
                    prev_block.transactions,
                    prev_block.prev_hash,
                    prev_block.hash,
                    prev_block.nonce
                )
            )
        )
        serialized_block = self.serialize(new_block)
        # de_serialized_block = self.deSerialize(serialized_block)
        db_block = models.Blocks(hash=new_block.hash, serializedBlock=serialized_block)
        db.session.add(db_block)
        db_last_block = models.LastBlock.query.first()
        if db_last_block is None:
            db_last_block = models.LastBlock(hash=new_block.hash)
            db.session.add(db_last_block)
        else:
            db_last_block.hash = new_block.hash
        db.session.commit()
        # self.blocks.append(newBlock)
        return True

    def send(self, fr, to, amount):
        print('Sending data=' + str(amount) + ' from ' + fr + ' to ' + to)
        transaction = self.new_transaction(fr, to, amount)
        if transaction:
            block_is_added = self.add_block([transaction])
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
                print(' - Inputs (count):' + str(len(transaction.v_in)))
                print(' - Outputs (count):' + str(len(transaction.v_out)))
                print(' ---')
                for v_in_index, v_in in enumerate(transaction.v_in):
                    print(' -> Input ' + str(v_in_index))
                    print(' -> Input id:' + str(v_in.id))
                    print(' -> Input sig:' + str(v_in.sig))
                    print(' -> Relative id of output:' + str(v_in.v_out))
                    if not self.is_coin_base(transaction):
                        print(' -> Input pub key (elliptic curve):' + 'X: {}, Y: {}'.format(str(v_in.pub_key.x),
                                                                                            str(v_in.pub_key.y)))
                        print(' -> Input pub key(bytes):' + str(v_in.pub_key_bytes))
                    print(' ---')
                for v_out_index, v_out in enumerate(transaction.v_out):
                    print(' -> Output ' + str(v_out_index))
                    print(' -> Output value:' + str(v_out.val))
                    print(' -> Output public key(bytes):' + str(v_out.pub_key_hash))
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
            genesis_block = self.new_block(transactions, '')
            serialized_genesis_block = self.serialize(genesis_block)
            db_block = models.Blocks(hash=genesis_block.hash, serializedBlock=serialized_genesis_block)
            db.session.add(db_block)
            db_last_block = models.LastBlock(hash=genesis_block.hash)
            db.session.add(db_last_block)
            db.session.commit()
            print('Success.')

    def is_serialized_soinbase_tx(self, jsonTx):
        return len(jsonTx["vIn"]) == 1 and json.loads(jsonTx["vIn"][0])["id"] is None and json.loads(jsonTx["vIn"][0])[
            "vOut"] == -1

    def serialize(self, block):
        json_block = {
            "timeStamp": block.time_stamp.isoformat(),
            "transactions": [],
            "prevHash": block.prev_hash,
            "hash": block.hash,
            "nonce": block.nonce
        }
        for tx in block.transactions:
            json_tx = {
                "id": tx.id,
                "vIn": [],
                "vOut": []
            }
            for v_in in tx.v_in:
                json_vin = {
                    "id": v_in.id,
                    "vOut": v_in.v_out,
                    "sig": (DEREncoder.encode_signature(v_in.sig["r"], v_in.sig["s"])).decode(
                        "latin1") if not self.is_coin_base(tx) else None,
                    "pubKey": PEMEncoder.encode_public_key(v_in.pub_key) if not self.is_coin_base(tx) else v_in.pub_key,
                    "pubKeyBytes": (v_in.pub_key_bytes).decode("latin1") if not self.is_coin_base(
                        tx) else v_in.pub_key_bytes
                }
                json_tx["vIn"].append(json.dumps(json_vin))
            for v_out in tx.v_out:
                jsonv_out = {
                    "val": v_out.val,
                    "pubKeyHash": (v_out.pub_key_hash).decode("latin1")
                }
                json_tx["vOut"].append(json.dumps(jsonv_out))
            json_block["transactions"].append(json.dumps(json_tx))
        json_data = json.dumps(json_block)
        return json_data

    def de_serialize(self, json_data):
        json_block = json.loads(json_data)
        block_tx = []
        for tx in json_block["transactions"]:
            json_tx = json.loads(tx)
            block_vin = []
            for vIn in json_tx["vIn"]:
                json_vin = json.loads(vIn)
                sig = DEREncoder.decode_signature(json_vin["sig"].encode("latin1")) if json_vin["sig"] is not None else None
                block_vin.append(
                    TransactionInput(
                        json_vin["id"],
                        json_vin["vOut"],
                        {'r': sig[0], 's': sig[1]} if not self.is_serialized_soinbase_tx(json_tx) else sig,
                        PEMEncoder.decode_public_key(json_vin["pubKey"], curve=curve.P256) if not self.is_serialized_soinbase_tx(json_tx) else json_vin["pubKey"],
                        json_vin["pubKeyBytes"].encode("latin1") if not self.is_serialized_soinbase_tx(json_tx) else json_vin["pubKeyBytes"]
                    )
                )
            block_vout = []
            for v_out in json_tx["vOut"]:
                json_vout = json.loads(v_out)
                block_vout.append(
                    TransactionOutput(
                        json_vout["val"],
                        json_vout["pubKeyHash"].encode("latin1")
                    )
                )
            block_tx.append(
                Transaction(
                    json_tx["id"],
                    block_vin,
                    block_vout
                )
            )
        block = Block(
            datetime.fromisoformat(json_block["timeStamp"]),
            block_tx,
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
        else:
            print('Blockchain is not initialized yet.')
