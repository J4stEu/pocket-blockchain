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
                "txID": tx.txID,
                "fromAddr": tx.fromAddr,
                "toAddr": tx.toAddr,
                "amount": tx.amount,
                "serializedTransaction": tx.serializedTransaction,
                "error": tx.error,
                "errorText": tx.errorText
            })
        return json.dumps(pool)
