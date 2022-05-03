class Wallet(object):
    def __init__(self, private_key, public_key, public_key_bytes):
        self.private_key = private_key
        self.public_key = public_key
        self.public_key_bytes = public_key_bytes
