from base58 import b58decode


class Transaction(object):
    def __init__(self, id, inputs, outputs, created, included_in_block=None):
        self.id = id
        self.inputs = inputs
        self.outputs = outputs
        self.created = created
        self.included_in_block = included_in_block

    def __repr__(self):
        inputs_representation = []
        for v_in in self.inputs:
            inputs_representation.append(v_in.__repr__)
        outputs_representation = []
        for v_out in self.outputs:
            outputs_representation.append(v_out.__repr__)
        return "Transaction: id = {}, inputs = {}, outputs = {}, created = {}".format(self.id, inputs_representation,
                                                                                      outputs_representation,
                                                                                      self.created)


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