import json
from .transaction import TransactionOutput
from . import models


class ChainState(object):
    def __init__(self, db):
        self.db = db

    def get_utxo(self, de_serialize=True):
        serialized_unspent_tx_outputs = models.UTXO.query.all()
        if de_serialize:
            return self.de_serialize_unspent_tx_outputs(serialized_unspent_tx_outputs)
        return serialized_unspent_tx_outputs

    def store_utxo(self, unspent_tx_outputs):
        # delete old cache
        self.db.session.query(models.UTXO).delete()
        self.db.session.commit()
        # set new cache
        serialized_unspent_tx_outputs = self.serialize_unspent_tx_outputs(unspent_tx_outputs)
        utxo = []
        for key, serialized_output in serialized_unspent_tx_outputs.items():
            utxo.append(models.UTXO(txID=key, serializedUnspentOutputs=json.dumps(serialized_output)))
        self.db.session.add_all(utxo)
        self.db.session.commit()

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