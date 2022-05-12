from .app import app
from .bc_app import bc
from flask import request
import json

@app.route('/')
def index():
    if bc.is_system_initialized():
        return "<p>Blockchain instance is already initialized.</p>"
    else:
        return "<p>Blockchain is not initialized yet.</p>"


@app.route('/get_wallets', methods=["GET"])
def get_wallets():
    if request.method == 'GET':
        wallets_info = []
        data = bc.get_wallets()
        if isinstance(data, Exception):
            return {
                "data": None,
                "error": data
            }
        wallets = data
        for address, wallet in wallets.items():
            data = bc.get_balance(address)
            if not isinstance(data, Exception):
                balance = data
                wallets_info.append(
                    {
                        "address": address,
                        "wallet": bc.serialize_wallet(wallet),
                        "balance": balance
                    }
                )
        return {
            "data": wallets_info,
            "error": None
        }


@app.route('/new_wallet', methods=["POST"])
def new_wallet():
    if request.method == 'POST':
        data = bc.new_wallet()
        if isinstance(data, Exception):
            return {
                "data": None,
                "error": "{}: {}".format(data.error_type, data.error_message)
            }
        return {
            "data": data,
            "error": None
        }


@app.route('/get_blocks', methods=["GET"])
def get_blocks():
    if request.method == 'GET':
        blocks = []
        for block in bc.get_blocks():
            blocks.append({
                "hash": block.hash,
                "serializedBlock": block.serializedBlock,
                "txsRootNode": block.txsRootNode
            })
        return json.dumps(blocks)


@app.route('/get_chainstate', methods=["GET"])
def get_chainstate():
    if request.method == 'GET':
        utxo = {}
        for serialized_utxo_item in bc.chain_state.get_utxo(False):
            utxo[serialized_utxo_item.txID] = {
                "serializedUnspentOutputs": serialized_utxo_item.serializedUnspentOutputs
            }
        return utxo


@app.route('/get_pool', methods=["GET"])
def get_pool():
    if request.method == 'GET':
        txs_pool = bc.get_all_pool()
        pool = []
        for tx in txs_pool:
            pool.append({
                "txID": tx.txID if tx.txID else "None",
                "fromAddr": tx.fromAddr,
                "toAddr": tx.toAddr,
                "amount": tx.amount,
                "serializedTransaction": tx.serializedTransaction,
                "error": tx.error,
                "errorText": tx.errorText
            })
        return json.dumps(pool)


@app.route('/send', methods=["POST"])
def send():
    if request.method == 'POST':
        if not request.is_json:
            return {
                "data": None,
                "error": "Request: request content-type error"
            }
        data = request.get_json()
        if type(data["from"]) is str and type(data["to"]) is str and type(data["amount"]) is int:
            if data["amount"] < 1:
                return {
                    "data": None,
                    "error": "Request: invalid amount value"
                }
            data = bc.send(data["from"], data["to"], data["amount"])
            if isinstance(data, Exception):
                return {
                    "data": None,
                    "error": "{}: {}".format(data.error_type, data.error_message)
                }
            return {
                "data": "Transaction is added to pool",
                "error": None
            }
        return {
            "data": None,
            "error": "Request: invalid parameters"
        }

@app.route('/mine_block', methods=["POST"])
def mine_block():
    if request.method == 'POST':
        if not request.is_json:
            return {
                "data": None,
                "error": "Request: request content-type error"
            }
        data = request.get_json()
        if type(data["address"]) is str and type(data["txAmount"]) is int:
            if data["txAmount"] < 1:
                return {
                    "data": None,
                    "error": "Request: invalid amotxAmountunt value"
                }
            data = bc.mine_block(data["address"], data["txAmount"])
            if isinstance(data, Exception):
                return {
                    "data": None,
                    "error": "{}: {}".format(data.error_type, data.error_message)
                }
            return {
                "data": "Block is mined",
                "error": None
            }
        else:
            return {
                "data": None,
                "error": "Request: invalid parameters"
            }

@app.route('/reset_system', methods=["POST"])
def reset_system():
    if request.method == 'POST':
        data = bc.clean_system()
        if isinstance(data, Exception):
            return {
                "data": None,
                "error": "{}: {}".format(data.error_type, data.error_message)
            }
        addresses = []
        for address in range(8):
            data = bc.new_wallet()
            if isinstance(data, Exception):
                return {
                    "data": None,
                    "error": "{}: {}".format(data.error_type, data.error_message)
                }
            address = data
            addresses.append(address)
        bc.init_system(addresses[0])

        amount = [3, 2, 1, 1, 1, 1, 1]

        for address in range(7):
            data = bc.send(addresses[0], addresses[address + 1], amount[address])
            if isinstance(data, Exception):
                return {
                    "data": None,
                    "error": "{}: {}".format(data.error_type, data.error_message)
                }
            data = bc.mine_block(addresses[0])
            if isinstance(data, Exception):
                return {
                    "data": None,
                    "error": "{}: {}".format(data.error_type, data.error_message)
                }

        for address in range(7):
            data = bc.send(addresses[address + 1], addresses[0], 1)
            if isinstance(data, Exception):
                return {
                    "data": None,
                    "error": "{}: {}".format(data.error_type, data.error_message)
                }

        data = bc.mine_block(addresses[1], 2)
        if isinstance(data, Exception):
            return {
                "data": None,
                "error": "{}: {}".format(data.error_type, data.error_message)
            }
        data = bc.mine_block(addresses[1], 3)
        if isinstance(data, Exception):
            return {
                "data": None,
                "error": "{}: {}".format(data.error_type, data.error_message)
            }

        return {
            "data": "System is reset",
            "error": None
        }